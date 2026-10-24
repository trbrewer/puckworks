"""S1 source-coordinate reconstruction and exact window enclosures; research only.

Offline: --reconstruct decodes the held DOCX (Pillow needed); ordinary analysis
uses committed native reading cells and the Python standard library only.
No physical shot identities, fitted endpoints, pressure mapping or mechanism fit.
"""
from __future__ import annotations

import argparse
import base64
import colorsys
import csv
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'puckworks/data/smrke2024/s1'
OUTPUT = ROOT / 'docs/analysis/sci_md_smrke_transient_hydraulics_001'
LEVELS = (0, 1, 2, 4)
SETTINGS = (190, 210, 250)
SOURCE_ID = 'S1_79a208a13500'
UNSUPPORTED = 'UNSUPPORTED'
OVERLAP = 'NOT_EXCLUDED_BY_OUTER_BOUNDS'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, default=str) + '\n')


def write_csv(path, rows, fields=None):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def outward(bounds, places=9):
    """Decimal strings enclosing exact rational bounds; never used for decisions."""
    scale = 10 ** places
    a, b = (F(x) * scale for x in bounds)
    integers = (a.numerator // a.denominator, -((-b.numerator) // b.denominator))
    return [('-' if n < 0 else '') + f'{abs(n)//scale}.{abs(n)%scale:0{places}d}'
            for n in integers]


class Calibration:
    def __init__(self, contract):
        c = contract['calibration']
        self.guard = F(c['reading_allowance_y_px'])
        g = F(c['anchor_allowance_px'])
        self.xa = list(product(*[(F(x)-g, F(x)+g) for x in c['x_anchors_px']]))
        self.ya = list(product(*[(F(y)-g, F(y)+g) for y in c['y_anchors_px']]))

    def query(self, a, b):
        # Positive affine inverse, extremal at interval/anchor corners.
        xs = [x0 + F(t) * (x80-x0)/80 for t, (x0, x80) in product((a, b), self.xa)]
        return min(xs), max(xs)

    def time(self, x0, x1):
        ts = [80*(F(x)-a)/(b-a) for x, (a, b) in product((x0, x1), self.xa)]
        return min(ts), max(ts)

    def flow(self, y0, y1, guard=None):
        g = self.guard if guard is None else F(guard)
        qs = [7*(a-y)/(a-b) for y, (a, b) in
              product((F(y0)-g, F(y1)+g), self.ya)]
        return min(qs), max(qs)


def colour(rgb, contract):
    h, s, v = colorsys.rgb_to_hsv(*(x/255 for x in rgb))
    if s < .25 or v < .15:
        return None
    for name in ('yellow', 'magenta', 'purple', 'blue'):
        lo, hi, _ = contract['colour_rules'][name]
        if lo <= h*360 <= hi:
            return name
    return None


def excluded(x, y, contract):
    for mask in contract['masks']:
        if mask['kind'] not in ('rectangle', 'outside_rectangle'):
            continue
        a, b, c, d = mask['box']
        inside = a <= x <= c and b <= y <= d
        if inside == (mask['kind'] == 'rectangle'):
            return mask['id']
    return None


def in_polygon(x, y, points):
    """Inclusive convex corridor membership via a ray; boundary guard below."""
    inside = False
    for (a, b), (c, d) in zip(points, points[1:] + points[:1]):
        if (x-a)*(d-b) == (y-b)*(c-a) and min(a, c) <= x <= max(a, c) and min(b, d) <= y <= max(b, d):
            return True
        if (b > y) != (d > y) and x < a + (y-b)*(c-a)/(d-b):
            inside = not inside
    return inside


def chain_runs(runs):
    """Terminate on branching/merging; vertical rank is never an identity."""
    by = {}
    for i, r in enumerate(runs):
        by.setdefault((r['colour'], r['x_px']), []).append(i)
    successors, predecessors = {}, {}
    for i, r in enumerate(runs):
        for j in by.get((r['colour'], r['x_px']+1), []):
            q = runs[j]
            if q['y_min_px'] <= r['y_max_px']+1 and r['y_min_px'] <= q['y_max_px']+1:
                successors.setdefault(i, []).append(j)
                predecessors.setdefault(j, []).append(i)
    assigned, count = {}, 0
    for i, r in enumerate(runs):
        parents = predecessors.get(i, [])
        if len(parents) == 1 and len(successors[parents[0]]) == 1:
            assigned[i] = assigned[parents[0]]
        else:
            count += 1
            assigned[i] = f'INK-{count:05d}'
        r['fragment_id'] = assigned[i]
        r['identity_boundary'] = ('BRANCH_OR_MERGE' if len(parents) > 1 or
                                  len(successors.get(i, [])) > 1 else 'NONE_OR_ENDPOINT')
    return runs


def bridge_columns(columns, max_missing=4, allowance=4):
    """Explicit bounded graphical gap rule; leave larger gaps unsupported."""
    result = dict(columns)
    xs = sorted(columns)
    for a, b in zip(xs, xs[1:]):
        if 1 < b-a <= max_missing+1:
            lo = min(columns[a][0], columns[b][0])-allowance
            hi = max(columns[a][1], columns[b][1])+allowance
            for x in range(a+1, b):
                result[x] = (lo, hi, 'BOUNDED_OCCLUSION_BRIDGE', f'{a}:{b}')
    return result


def reconstruct(data=DATA):
    """Decode authenticated image; write ink and conditional source cells only."""
    from io import BytesIO
    from PIL import Image

    c = json.loads((data/'contract.json').read_text())
    correction = json.loads((data/'qualification_correction.json').read_text())
    regions = json.loads((data/'regions.json').read_text())
    source = c['source']
    docx = DATA.parent/source['docx']
    if digest(docx) != source['docx_sha256']:
        raise ValueError('DOCX identity mismatch')
    with zipfile.ZipFile(docx) as archive:
        payload = archive.read(source['image_member'])
    if hashlib.sha256(payload).hexdigest() != source['image_sha256']:
        raise ValueError('embedded image identity mismatch')
    im = Image.open(BytesIO(payload)).convert('RGB')
    if list(im.size) != source['image_size_px']:
        raise ValueError('native size mismatch')
    pixels = im.load()
    columns, excluded_runs = {}, []
    for x in range(78, 1640):
        for y in range(78, 944):
            name = colour(pixels[x, y], c)
            if name:
                mask = excluded(x, y, c)
                columns.setdefault((name, x, mask or ''), []).append(y)
    runs = []
    for (name, x, mask), ys in sorted(columns.items()):
        groups = []
        for y in ys:
            if not groups or y > groups[-1][-1]+1:
                groups.append([y])
            else:
                groups[-1].append(y)
        for group in groups:
            row = dict(source_id=SOURCE_ID, colour=name, x_px=x,
                       y_min_px=min(group), y_max_px=max(group), pixel_count=len(group))
            if mask:
                excluded_runs.append(dict(row, mask_id=mask, status='EXCLUDED_NONDATA'))
            else:
                runs.append(row)
    chain_runs(runs)
    cal = Calibration(c)
    fragments = {}
    for i, r in enumerate(runs, 1):
        r['observation_id'] = f'S1-R{i:05d}'
        r['nominal_colour_fines_g'] = c['colour_rules'][r['colour']][2]
        r['grinder_setting'] = ''
        r['condition_membership'] = 'AMBIGUOUS_RASTER_COLOUR_AND_STYLE'
        r['admissible_settings'] = '190|210|250'
        r['admissible_fines_g'] = '0|1|2|4'
        r['colour_assignment'] = 'NOMINAL_MASK_CLASS_NOT_AUTHENTICATED_TRACE'
        r['phase'] = 'UNRESOLVED'
        r['temporal_status'] = 'UNSUPPORTED_IDENTITY_STYLE_PHASE_OR_GAP'
        # The black boundary can overpaint the contact pixel. Include the
        # calibration/reading/footprint neighbourhood, not just exact y==78.
        guard = correction['boundary_contact_guard_px']
        r['clipping'] = int(r['y_min_px'] <= 78+guard or r['y_max_px'] >= 943-guard or
                            r['x_px'] <= 78+guard or r['x_px'] >= 1639-guard)
        r['time_lower_s'], r['time_upper_s'] = outward(cal.time(F(r['x_px'])-F(1, 2), F(r['x_px'])+F(1, 2)))
        r['flow_lower_g_s'], r['flow_upper_g_s'] = ('', '') if r['clipping'] else outward(cal.flow(r['y_min_px'], r['y_max_px']))
        f = fragments.setdefault(r['fragment_id'], dict(fragment_id=r['fragment_id'], colour=r['colour'],
            nominal_colour_fines_g=r['nominal_colour_fines_g'], admissible_settings='190|210|250',
            admissible_fines_g='0|1|2|4',
            membership='AMBIGUOUS', phase='UNRESOLVED', persistent_shot_identity='NOT_ESTABLISHED',
            x_min_px=r['x_px'], x_max_px=r['x_px'], y_min_px=r['y_min_px'], y_max_px=r['y_max_px'],
            reading_count=0, clipping=0, temporal_status=r['temporal_status']))
        f['x_max_px'] = max(f['x_max_px'], r['x_px'])
        f['y_min_px'] = min(f['y_min_px'], r['y_min_px'])
        f['y_max_px'] = max(f['y_max_px'], r['y_max_px'])
        f['reading_count'] += 1
        f['clipping'] |= r['clipping']
    write_csv(data/'source_observations.csv', runs)
    write_csv(data/'ink_fragments.csv', list(fragments.values()))
    write_csv(data/'excluded_ink.csv', excluded_runs)
    cells = []
    for region in regions['retained']:
        a, b = region['x_support_px']
        if region['kind'] == 'branch_bundle':
            lo, hi = region['y_enclosure_px']
            support = [r['observation_id'] for r in runs if r['colour'] == region['colour'] and
                       a <= r['x_px'] <= b and r['y_min_px'] <= hi and r['y_max_px'] >= lo]
            cells.append(dict(cell_id=region['id']+'-SLAB', object_id=region['id'],
                source_id=SOURCE_ID, x_lower_px=a, x_upper_px=b, y_lower_px=lo, y_upper_px=hi,
                support_kind='AUDITED_SOLID_BUNDLE_ENCLOSURE', support_readings='|'.join(support)))
            continue
        selected = {}
        for x in range(a, b+1):
            ys = [y for y in range(78, 944) if colour(pixels[x, y], c) == region['colour']
                  and in_polygon(x, y, region['polygon'])]
            if ys:
                ids = [r['observation_id'] for r in runs if r['colour'] == region['colour'] and
                       r['x_px'] == x and r['y_min_px'] <= max(ys) and r['y_max_px'] >= min(ys)]
                selected[x] = (min(ys), max(ys), 'NATIVE_INK_COLUMN', '|'.join(ids))
        selected = bridge_columns(selected, c['gap_rule']['max_missing_columns'],
                                  c['gap_rule']['occlusion_guard_y_px'])
        for x, (lo, hi, kind, support) in sorted(selected.items()):
            cells.append(dict(cell_id=f'{region["id"]}-X{x}', object_id=region['id'], source_id=SOURCE_ID,
                x_lower_px=str(F(x)-F(1, 2)), x_upper_px=str(F(x)+F(1, 2)),
                y_lower_px=lo, y_upper_px=hi, support_kind=kind, support_readings=support))
    for cell in cells:
        cell['temporal_status'] = 'CONDITIONAL_READING_CANDIDATE_REQUIRES_IDENTITY_SUPPORT'
        for retired in correction['retire_from_temporal_support']:
            if (cell['object_id'] == retired['region_id'] and
                F(cell['x_upper_px']) > F(retired['x_lower_px'])-F(1, 2)):
                cell['temporal_status'] = retired['status']
    write_csv(data/'reading_cells.csv', cells)
    qualified, _ = split_support(regions['retained'], load_cells(data), correction)
    write_json(data/'qualified_fragments.json', qualified)
    write_json(data/'reconstruction.json', dict(source=source, observations=len(runs),
        generic_ink_fragments=len(fragments), excluded_colour_runs=len(excluded_runs),
        selected_regions=len(regions['retained']), qualified_objects=len(qualified), physical_shots_recovered=0,
        cells=len(cells), bridge_cells=sum(r['support_kind'] == 'BOUNDED_OCCLUSION_BRIDGE' for r in cells),
        note='Ink fragments and selected objects overlap; do not sum them as traces or shots.'))


def windows(offset=0, domain=(0, 85), width=3):
    a, b, width, offset = map(F, (*domain, width, offset))
    result = []
    if offset > a:
        result.append((a, offset, False))
    x = offset
    while x < b:
        result.append((x, min(x+width, b), x+width <= b))
        x += width
    return result


def covers(cells, a, b):
    end = a
    for c in sorted(cells, key=lambda r: r['x_lower_px']):
        lo, hi = c['x_lower_px'], c['x_upper_px']
        if hi < end:
            continue
        if lo > end:
            return False
        end = max(end, hi)
        if end >= b:
            return True
    return False


def window_mean(cells, a, b, cal, step=F(1, 20)):
    """Exact integration of a conservative cellwise outer enclosure.

    Each full time cell uses every intersected native support cell over the
    entire uncertain inverse-x range, including endpoints/partial cells.
    """
    a, b, step = F(a), F(b), F(step)
    if b <= a or step <= 0:
        raise ValueError('nonpositive interval')
    lower = upper = F(0)
    witnesses, x = [], a
    while x < b:
        end = min(x+step, b)
        xl, xu = cal.query(x, end)
        if not covers(cells, xl, xu):
            return dict(status=UNSUPPORTED, reason='INCOMPLETE_UNCERTAIN_X_SUPPORT',
                        missing_time_cell_s=[x, end], missing_x_px=[xl, xu], lower=None, upper=None)
        found = [c for c in cells if c['x_lower_px'] <= xu and c['x_upper_px'] >= xl]
        if any(c.get('unbounded', False) for c in found):
            return dict(status=UNSUPPORTED, reason='UNBOUNDED_CLIPPING_OR_GAP', lower=None, upper=None)
        yl = min(c['y_lower_px'] for c in found)
        yu = max(c['y_upper_px'] for c in found)
        ql, qu = cal.flow(yl, yu)
        lower += (end-x)*ql
        upper += (end-x)*qu
        witnesses.append(dict(time_s=[x, end], query_x_px=[xl, xu], y_extent_px=[yl, yu],
            cell_ids=[c['cell_id'] for c in found], q_bounds_g_s=[ql, qu]))
        x = end
    return dict(status='SUPPORTED_CONDITIONAL_GRAPHICAL', reason='COMPLETE_OUTER_ENCLOSURE',
                lower=lower/(b-a), upper=upper/(b-a), integration_cells=witnesses)


def qualified_window(cells, a, b, cal, phase, full_window):
    """Eligibility consumes the prior source phase label, never flow direction."""
    if not full_window or phase != 'GRAPHICAL_INTERIOR':
        return dict(status=UNSUPPORTED, reason='INCOMPLETE_DOMAIN_REMAINDER' if not full_window
                    else 'NONINTERIOR_OR_UNRESOLVED_GRAPHICAL_PHASE', lower=None, upper=None)
    return window_mean(cells, a, b, cal)


def ordered_change(a, b):
    if a is None or b is None:
        return dict(status=UNSUPPORTED, difference=None)
    diff = (b[0]-a[1], b[1]-a[0])
    return dict(status='RISE' if diff[0] > 0 else 'DECLINE' if diff[1] < 0 else OVERLAP,
                difference=diff)


def constant(bounds):
    if len(bounds) < 2:
        return dict(status='UNINFORMATIVE', intersection=None)
    lo, hi = max(x[0] for x in bounds), min(x[1] for x in bounds)
    return dict(status='EXCLUDED' if lo > hi else OVERLAP, intersection=[lo, hi])


def multiplier(bounds):
    """Intersect exact overlap inequalities for ONE fixed partner history, k>0."""
    if len(bounds) < 2:
        return dict(status='UNINFORMATIVE', interval=None, window_sets=[])
    lower, upper, sets = F(0), None, []
    for a, b in bounds:
        al, au, bl, bu = map(F, (*a, *b))
        if al > au or bl > bu:
            raise ValueError('ordered bounds required')
        lo, hi = F(0), None
        impossible = False
        # c*k <= d, without division by zero or epsilon clipping. Negative
        # coefficients reverse the inequality; graphical bounds may cross zero.
        for coefficient, rhs in ((al, bu), (-au, -bl)):
            if coefficient > 0:
                limit = rhs/coefficient
                hi = limit if hi is None else min(hi, limit)
            elif coefficient < 0:
                lo = max(lo, rhs/coefficient)
            elif rhs < 0:
                impossible = True
        sets.append(dict(lower=lo, upper=hi, impossible=impossible))
        lower = max(lower, lo)
        if hi is not None:
            upper = hi if upper is None else min(hi, upper)
        if impossible:
            upper = F(-1)
    empty = upper is not None and (upper < lower or upper <= 0)
    return dict(status='EXCLUDED' if empty else OVERLAP,
                interval=None if empty else [lower, upper], lower_open=lower == 0, window_sets=sets)


def multiplier_alternatives(pairings):
    """Union AFTER fixed-partner intersections. Never switch partners per window."""
    results = [multiplier(p) for p in pairings]
    if not results:
        status = UNSUPPORTED
    elif any(r['status'] == 'UNINFORMATIVE' for r in results):
        status = 'UNINFORMATIVE'
    elif all(r['status'] == 'EXCLUDED' for r in results):
        status = 'EXCLUDED_ALL_RETAINED_PAIRINGS'
    else:
        status = OVERLAP
    return dict(status=status, fixed_pairings=results,
                allowed_outer_union=[r['interval'] for r in results if r['status'] == OVERLAP])


def load_cells(data=DATA):
    cells = read_csv(data/'reading_cells.csv')
    for r in cells:
        for key in ('x_lower_px', 'x_upper_px', 'y_lower_px', 'y_upper_px'):
            r[key] = F(r[key])
    return cells


def split_support(regions, cells, correction=None):
    """An unbridged gap ends persistent identity as well as window support."""
    result, new_cells = [], []
    for region in regions:
        retire = (correction or {}).get('retire_from_temporal_support', [])
        selected = sorted([dict(c) for c in cells if c['object_id'] == region['id'] and
                           not any(r['region_id'] == region['id'] and
                                   c['x_upper_px'] > F(r['x_lower_px'])-F(1, 2) and
                                   c['x_lower_px'] < F(r['x_upper_px'])+F(1, 2) for r in retire)],
                          key=lambda c: c['x_lower_px'])
        groups = []
        for c in selected:
            if not groups or c['x_lower_px'] > groups[-1][-1]['x_upper_px']:
                groups.append([])
            groups[-1].append(c)
        for i, group in enumerate(groups):
            obj = dict(region)
            obj['parent_region_id'] = region['id']
            obj['id'] = region['id'] if len(groups) == 1 else f'{region["id"]}.{i+1}'
            obj['support_x_px'] = [group[0]['x_lower_px'], group[-1]['x_upper_px']]
            obj['identity_note'] = 'No identity continuation across any unbridged gap'
            result.append(obj)
            for c in group:
                c['object_id'] = obj['id']
                new_cells.append(c)
    return result, new_cells


def analyze(data=DATA, output=OUTPUT):
    output.mkdir(parents=True, exist_ok=True)
    contract = json.loads((data/'contract.json').read_text())
    regions = json.loads((data/'regions.json').read_text())['retained']
    cal, cells = Calibration(contract), load_cells(data)
    correction = json.loads((data/'qualification_correction.json').read_text())
    regions, cells = split_support(regions, cells, correction)
    write_json(output/'QUALIFIED_OBJECTS.json', regions)
    generic = read_csv(data/'ink_fragments.csv')
    end = F(correction['displayed_right_frame_nominal_s'])
    lattice = [(name, windows(offset, domain=(0, end))) for name, offset in [('PRIMARY', F(0)), ('SHIFTED', F(3, 2))]]
    write_json(output/'DOMAIN_COVERAGE.json', dict(lattice_domain_s=[F(0),end],
        native_x_domain_px=[78,1639], right_frame_time_outer_s=cal.time(1639,1639),
        edge_status='UNSUPPORTED_CENSORING_AND_CALIBRATION_EDGE',
        note='Incomplete remainders extend to nominal native right frame; uncertain frame neighbourhood is unsupported. Chart limits never bound unseen continuation.'))
    requests, detailed, by = [], {}, {}
    for design, wins in lattice:
        for obj in regions:
            for j, (a, b, full) in enumerate(wins):
                wid = f'{design}:{obj["id"]}:{j:02d}'
                r = qualified_window([c for c in cells if c['object_id'] == obj['id']],
                                     a, b, cal, obj['phase'], full)
                r.update(window_id=wid, object_id=obj['id'], lattice=design, window_index=j,
                         start_s=a, end_s=b, full_window=full, phase=obj['phase'], coverage=obj['coverage'],
                         persistent_identity=obj['persistent'], operational_phase='UNRESOLVED')
                detailed[wid] = r
                by[(design, obj['id'], j)] = r
                row = {k: v for k, v in r.items() if k not in ('integration_cells', 'missing_time_cell_s', 'missing_x_px')}
                row['lower'], row['upper'] = outward((r['lower'], r['upper'])) if r['lower'] is not None else ('', '')
                requests.append(row)
    # Explicit generic fragment/window requests, compact reasons and no fake means.
    generic_requests = dict(encoding='EXPLICIT_CARTESIAN_PRODUCT_WITH_SHARED_REASON',
        fragment_table='puckworks/data/smrke2024/s1/ink_fragments.csv',
        fragment_table_sha256=digest(data/'ink_fragments.csv'),
        fragment_key='fragment_id', fragment_reason_column='temporal_status',
        status=UNSUPPORTED, fragment_count=len(generic),
        windows=[dict(lattice=design, window_index=j, start_s=a, end_s=b,
                      reason_override=None if full else 'INCOMPLETE_DOMAIN_REMAINDER')
                 for design, wins in lattice for j, (a, b, full) in enumerate(wins)],
        note='Every table fragment times every listed window is requested; no omitted or implicitly successful rows.')
    generic_requests['request_count'] = len(generic)*len(generic_requests['windows'])
    write_json(output/'GENERIC_WINDOW_REQUESTS.json', generic_requests)
    write_csv(output/'WINDOWS.csv', requests)
    write_json(output/'WINDOW_WITNESSES.json', detailed)
    ordered, constants, recovery = [], [], []
    for design, wins in lattice:
        for obj in regions:
            selected = [by[(design, obj['id'], j)] for j in range(len(wins))]
            supported = [r for r in selected if r['lower'] is not None]
            ident = dict(object_id=obj['id'], lattice=design, windows=[r['window_id'] for r in supported])
            if not obj['persistent']:
                constants.append(dict(ident, status=UNSUPPORTED, reason='NO_PERSISTENT_IDENTITY', intersection=None))
                continue
            constants.append(dict(ident, **constant([(r['lower'], r['upper']) for r in supported])))
            for a, b in combinations(selected, 2):
                valid = a['lower'] is not None and b['lower'] is not None
                z = ordered_change((a['lower'], a['upper']) if valid else None,
                                   (b['lower'], b['upper']) if valid else None)
                ordered.append(dict(object_id=obj['id'], lattice=design,
                    earlier=a['window_id'], later=b['window_id'], **z,
                    reason='COMPLETE_SAME_FRAGMENT_WINDOWS' if valid else 'MISSING_COMPLETE_WINDOW'))
            for a, b, c in zip(selected, selected[1:], selected[2:]):
                valid = all(r['lower'] is not None for r in (a, b, c))
                margins = [a['lower']-b['upper'], c['lower']-b['upper']] if valid else None
                recovery.append(dict(object_id=obj['id'], lattice=design,
                    windows=[r['window_id'] for r in (a, b, c)], margins=margins,
                    status=UNSUPPORTED if not valid else 'DECLINE_RECOVERY' if min(margins) > 0 else OVERLAP))
    write_json(output/'TEMPORAL_COMPARISONS.json', dict(ordered=ordered, constant=constants, recovery=recovery))
    pairs, multipliers, coverage = [], [], []
    for setting in SETTINGS:
        for level in LEVELS:
            retained = [o for o in regions if o['grinder_setting'] == setting and o['fines_g'] == level]
            coverage.append(dict(grinder_setting=setting, replacement_fines_g=level, nominal_extractions=3,
                recovered_physical_shots=0, source_visible_trace_count=None,
                generic_fragments_with_admissible_membership=sum(str(level) in f['admissible_fines_g'].split('|') for f in generic),
                retained_objects=[o['id'] for o in retained], retained_persistent_fragments=sum(o['persistent'] for o in retained),
                condition_envelope_complete=False, unknown_fully_hidden_support='UNKNOWN',
                reason='Visible complete trajectory counts not identifiable; generic memberships overlap settings.'))
        for alevel, blevel in combinations(LEVELS, 2):
            pairid = f'{setting}:{alevel}:{blevel}'
            aa = [o for o in regions if o['grinder_setting'] == setting and o['fines_g'] == alevel]
            bb = [o for o in regions if o['grinder_setting'] == setting and o['fines_g'] == blevel]
            for design, wins in lattice:
                fixed = []
                for ao, bo in product(aa, bb):
                    if ao['persistent'] and bo['persistent']:
                        common = [(by[(design, ao['id'], j)], by[(design, bo['id'], j)]) for j in range(len(wins))]
                        common = [(a, b) for a, b in common if a['lower'] is not None and b['lower'] is not None]
                        fixed.append(dict(objects=[ao['id'], bo['id']], windows=[[a['window_id'], b['window_id']] for a, b in common],
                            result=multiplier([((a['lower'], a['upper']), (b['lower'], b['upper'])) for a, b in common])))
                multipliers.append(dict(pair_id=pairid, lattice=design, fixed_pairings=fixed,
                    status=UNSUPPORTED if not fixed else ('EXCLUDED_ALL_RETAINED_PAIRINGS' if all(p['result']['status'] == 'EXCLUDED' for p in fixed) else OVERLAP if any(p['result']['status'] == OVERLAP for p in fixed) else 'UNINFORMATIVE'),
                    reason='NO_TWO_PERSISTENT_CONDITION_MEMBERS' if not fixed else 'ALL_MAXIMAL_COMMON_WINDOWS',
                    condition_coverage='INCOMPLETE'))
                for j, (start, end, full) in enumerate(wins):
                    candidates = []
                    for ao, bo in product(aa, bb):
                        ar, br = by[(design, ao['id'], j)], by[(design, bo['id'], j)]
                        if ar['lower'] is not None and br['lower'] is not None:
                            candidates.append(dict(objects=[ao['id'], bo['id']], windows=[ar['window_id'], br['window_id']],
                                a_bounds=[ar['lower'], ar['upper']], b_bounds=[br['lower'], br['upper']],
                                difference=[br['lower']-ar['upper'], br['upper']-ar['lower']],
                                within_a_spread_lower_bound_g_s=F(0),
                                within_a_spread_upper_bound_g_s=ar['upper']-ar['lower'],
                                within_b_spread_lower_bound_g_s=F(0),
                                within_b_spread_upper_bound_g_s=br['upper']-br['lower']))
                    pairs.append(dict(pair_id=pairid, grinder_setting=setting, fines_a_g=alevel, fines_b_g=blevel,
                        priority='PRIMARY' if alevel == 0 else 'SECONDARY', lattice=design, start_s=start, end_s=end,
                        status='SUPPORTED_PARTIAL_GRAPHICAL_CONTRAST' if candidates else UNSUPPORTED,
                        reason='RETAINED_BUNDLES_ONLY' if candidates else 'INCOMPLETE_DOMAIN_REMAINDER' if not full else 'NO_COMMON_COMPLETE_INTERIOR_CONDITION_SUPPORT',
                        comparisons=candidates, condition_envelope_complete=False))
    write_json(output/'COVERAGE.json', coverage)
    write_json(output/'FINES_COMPARISONS.json', pairs)
    write_json(output/'MULTIPLIERS.json', multipliers)
    result = dict(task=contract['task'], classification=contract['classification'],
        SOURCE_RECONSTRUCTION='CORRECTED_NATIVE_INK_WITH_QUALIFIED_SUBSETS',
        INTERIOR_FLOW_BEHAVIOUR=dict(rises=sum(r['status'] == 'RISE' for r in ordered),
            declines=sum(r['status'] == 'DECLINE' for r in ordered),
            decline_recovery=sum(r['status'] == 'DECLINE_RECOVERY' for r in recovery), constant=constants,
            coverage='DISCONNECTED_FRAGMENTS_OF_ONE_RETAINED_CORRIDOR; OPERATIONAL_INTERIOR_UNRESOLVED'),
        FIXED_GRIND_FINES_CONTRASTS=dict(intended_pairs=18, requested_window_pairs=len(pairs),
            supported_window_pairs=sum(bool(p['comparisons']) for p in pairs),
            supported_intended_pairs=len({p['pair_id'] for p in pairs if p['comparisons']}),
            unsupported_primary_intended_pairs=9,
            complete_condition_envelopes=0, interpretation='RETAINED_SOLID_BUNDLES_ONLY; NOT_FINES_WIDE_SHAPE'),
        CONSTANT_MULTIPLIER_COMPATIBILITY=dict(status=UNSUPPORTED, intended_pairs=18,
            reason='NO_FIXED_PERSISTENT_CROSS_CONDITION_PAIR_WITH_TWO_COMMON_WINDOWS'),
        NORMALIZED_SHAPE_SUPPORT='UNRESOLVED_SOURCE_SUPPORT', PHYSICAL_VALIDATION='NOT_ESTABLISHED',
        nominal_conditions=12, nominal_extractions=36, recovered_physical_shots=0,
        generic_fragments=len(generic), selected_objects=len(regions),
        supported_selected_windows=sum(r['lower'] is not None for r in detailed.values()),
        requested_selected_windows=len(detailed), generic_window_requests=generic_requests['request_count'],
        hashes={name: digest(data/name) for name in ('contract.json', 'regions.json', 'qualification_correction.json', 'source_observations.csv', 'ink_fragments.csv', 'reading_cells.csv')})
    write_json(output/'RESULT.json', result)
    figures(contract, regions, detailed, output)
    return result


def figures(contract, regions, detailed, output):
    source = contract['source']
    with zipfile.ZipFile(DATA.parent/source['docx']) as archive:
        payload = base64.b64encode(archive.read(source['image_member'])).decode()
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1680" height="1120" viewBox="0 0 1680 1120">',
           '<rect width="1680" height="1120" fill="white"/>',
           f'<image width="1680" height="1041" href="data:image/jpeg;base64,{payload}"/>']
    for r in regions:
        if 'polygon' in r:
            pts = ' '.join(f'{x},{y}' for x, y in r['polygon'])
            a, b = map(float, r['support_x_px'])
            clip = 'support-'+r['id']
            svg.append(f'<defs><clipPath id="{clip}"><rect x="{a}" y="78" width="{b-a}" height="865"/></clipPath></defs>')
            svg.append(f'<polygon points="{pts}" clip-path="url(#{clip})" fill="#00a64b" fill-opacity="0.15" stroke="#00a64b" stroke-width="3"/>')
        else:
            a, b = r['x_support_px']; c, d = r['y_enclosure_px']
            svg.append(f'<rect x="{a}" y="{c}" width="{b-a}" height="{d-c}" fill="#00a64b" fill-opacity="0.15" stroke="#00a64b" stroke-width="3"/>')
        svg.append(f'<text x="{float(r["support_x_px"][0])}" y="{520 if r["kind"] == "persistent_fragment" else r["y_enclosure_px"][0]-10}" font-size="18">{r["id"]}</text>')
        if r['kind'] == 'persistent_fragment':
            for x in r['support_x_px']:
                svg.append(f'<path d="M{float(x)},550 V815" stroke="#00a64b" stroke-dasharray="3 3"/>')
    svg.append('<rect x="1200" y="78" width="439" height="208" fill="red" fill-opacity="0.17" stroke="red"/>')
    svg.append('<rect x="401.5" y="550" width="5" height="265" fill="red" fill-opacity="0.25"><title>Unbridged5-column gap; persistent identity ends</title></rect>')
    svg.append('<rect x="478.5" y="550" width="50" height="265" fill="red" fill-opacity="0.18" stroke="red" stroke-dasharray="5 5"><title>Retired: mixed blue branches and missing intended upper ink; audit readings retained, temporal qualification removed</title></rect>')
    for x in contract['calibration']['x_ticks_px']:
        svg.append(f'<circle cx="{x}" cy="943" r="5" fill="lime"/>')
    for y in contract['calibration']['y_ticks_px']:
        svg.append(f'<circle cx="78" cy="{y}" r="5" fill="lime"/>')
    diagnostics = json.loads((DATA/'regions.json').read_text())['diagnostics']
    for d in diagnostics:
        a, b, c, e = d['box']
        svg.append(f'<rect x="{a}" y="{b}" width="{c-a}" height="{e-b}" fill="none" stroke="#e64a19" stroke-width="2"><title>{d["id"]}: {d["reason"]}</title></rect>')
    svg.extend(['<text x="30" y="1065" font-size="19">Smrke, Eiermann &amp; Yeretzian (2024), Supplementary Fig S1. CC BY 4.0. DOI:10.1038/s41598-024-55831-x.</text>',
        '<text x="30" y="1095" font-size="18">Green: qualified regions/ticks. Red: excluded legend, unbridged gap and retired blue region. Orange: source diagnostics. Graphical support only.</text>', '</svg>'])
    (output/'SOURCE_OVERLAY.svg').write_text('\n'.join(svg)+'\n')
    height = 140+170*len(regions)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}">',
           f'<rect width="1200" height="{height}" fill="white"/>',
           '<text x="25" y="30" font-size="22">S1 window-mean plotted flow: conditional graphical bounds; missingness retained</text>']
    for k, obj in enumerate(regions):
        ybase = 180+k*170
        label = f'{obj["fines_g"]} g replacement, setting {obj["grinder_setting"]}: {obj["id"]}; partial condition support'
        svg.append(f'<text x="20" y="{ybase-125}" font-size="16">{label}</text>')
        for r in detailed.values():
            if r['object_id'] != obj['id']:
                continue
            x = 70+float((r['start_s']+r['end_s'])/2)*12
            offset = 0 if r['lattice'] == 'PRIMARY' else 4
            if r['lower'] is None:
                svg.append(f'<path d="M{x-2},{ybase+offset} l4,4 m-4,0 l4,-4" stroke="#aaa"/>')
            else:
                lo, hi = float(r['lower']), float(r['upper'])
                start, end = float(r['start_s']), float(r['end_s'])
                color = '#005b82' if not offset else '#b54572'
                svg.append(f'<rect x="{70+start*12}" y="{ybase-hi*18}" width="{(end-start)*12}" height="{(hi-lo)*18}" fill="{color}" fill-opacity="0.25" stroke="{color}" stroke-width="2"><title>{r["window_id"]}: mean over {start}–{end} s, {lo:.6f}..{hi:.6f} g/s; not an instantaneous flow band</title></rect>')
        svg.append(f'<path d="M70,{ybase} H1090" stroke="black"/>')
        for t in (0, 20, 40, 60, 80):
            svg.append(f'<text x="{70+t*12}" y="{ybase+23}" font-size="14">{t} s</text>')
        for q in (0, 2, 4, 6):
            svg.append(f'<text x="28" y="{ybase-q*18+5}" font-size="12">{q}</text>')
    svg.extend([f'<text x="25" y="{height-40}" font-size="15">Boxes: window-mean bounds across averaging windows (not instantaneous bands). Blue: primary; magenta: shifted; ×: unsupported. g/s.</text>',
                f'<text x="25" y="{height-15}" font-size="15">Source: Smrke et al. 2024, S1 (CC BY 4.0). Not laboratory uncertainty, shot replicates or physical validation.</text>', '</svg>'])
    (output/'COMPARISON.svg').write_text('\n'.join(svg)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DATA)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--reconstruct', action='store_true')
    args = parser.parse_args()
    if args.reconstruct:
        reconstruct(args.data)
    result = analyze(args.data, args.output)
    print(json.dumps({k: v for k, v in result.items() if k.isupper()}, default=str))


if __name__ == '__main__':
    main()
