#!/usr/bin/env python3
"""Refresh only observed/generated guide blocks; retain hand-curated prose."""
from __future__ import annotations
import csv
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GUIDE=ROOT/'docs/data/ESPRESSO_DATA_GUIDE.md'


def cell(value):
    return str(value).replace('|','\\|').replace('\n',' ')


def render(text=None):
    text=GUIDE.read_text() if text is None else text
    snap=json.loads((ROOT/'puckworks/data/LOCAL_CORPUS_SNAPSHOT.json').read_text())
    index=json.loads((ROOT/'puckworks/data/LOCAL_CORPUS_FAMILY_INDEX.json').read_text())
    rows={r['dataset_id']:r for r in csv.DictReader((ROOT/'puckworks/data/MANIFEST.csv').open())}
    family_counts={f['family_id']:f for f in snap['families']}
    overview=(f"**Checked {snap['snapshot_date']} UTC** (local evening may be the preceding date): "
              f"{snap['root_count']} declared root, **{snap['files']:,} regular files / {snap['bytes']:,} bytes** "
              f"({snap['bytes']/1e9:.3f} GB apparent file bytes), {snap['unique_sha256_contents']:,} unique byte contents; "
              f"{sum(f['access']=='FOUND' for f in snap['families'])}/{len(snap['families'])} registered source families found. "
              f"Status: `{snap['status']}`. Full hash census; bounded structural inspection and sampled semantic review. "
              "Protected sources and private generated outputs are hash-only. No corpus-wide observation count is established.\n\n"
              f"Snapshot identity: `{snap['content_identity']}`. "
              "[Machine-readable snapshot](../../puckworks/data/LOCAL_CORPUS_SNAPSHOT.json).")
    reconciliation=[f"{snap['entry_count']:,} entries: {snap['files']:,} regular files, {snap['symlinks']} symlinks; "
                    f"{snap['hashed']:,}/{snap['files']:,} files hashed, {snap['unreadable_entries']} unreadable entries, "
                    f"{snap['unstable_files']} unstable files, {snap['concurrent_entry_changes']} concurrent entry changes, "
                    f"{snap['excluded_subtrees']} excluded output subtrees, {snap['unavailable_root_count']} unavailable roots. "
                    f"Hardlink extra entries: {snap['hardlink_extra_entries']}.",
                    f"{snap['structured_files']} physical files received full lightweight structured parsing; "
                    f"{snap['archive_files']} physical archives/compressed streams yielded {snap['archive_member_entries']:,} logical member entries "
                    f"({snap['archive_member_structures']:,} parsed structures, {snap['archive_member_parse_failures']} parse failures). "
                    f"{snap['archive_members_matching_physical_files']} archive members match physical file hashes. "
                    f"Physical parse failures: {snap['parse_failures']}; ragged tables: {snap['ragged_tables']}. "
                    "These are inspection denominators, not experimental observation totals.",
                    f"{snap['repository_identical_files']:,} files match inspected repository bytes; {snap['canonical_same_path_mismatches']} same-path canonical comparisons differ. "
                    f"{snap['unmapped']['files']:,} files do not map to a registered source-family directory; "
                    "private reconciliation retains every group and locator. Other registered datasets absent from this external root may still be packaged in Git. "
                    "A found family does not certify every registered subset or every source supplement.",
                    '| Provisional content role | Physical files | Apparent bytes |','|---|---:|---:|']
    for role, count in snap['by_content_role'].items():
        reconciliation.append(f"| {role} | {count['files']:,} | {count['bytes']:,} |")
    represented={did for f in index['families'] for did in f['manifest_dataset_ids']}
    outside=sorted(set(rows)-represented)
    reconciliation.append('\nThe canonical MANIFEST contains '+str(len(rows))+' dataset rows; '+str(len(represented))+
                          ' IDs route through the reviewed family index. Remaining canonical rows: '+
                          ', '.join('`'+did+'`' for did in outside)+'. These are reconciled below, not silently omitted.')
    reconciliation.append('\nRoles are conservative routing classifications; mixed/unknown files remain unresolved. '
                          'Duplicate groups are an orthogonal field in the private manifest, not a second experiment class.')
    family_text=[]
    for f in index['families']:
        counts=family_counts[f['family_id']]
        family_text.extend([f"### {f['family_id']}",
            f"**Access:** {counts['access']} on {snap['snapshot_date']}; {counts['files']} files / {counts['bytes']:,} bytes; "
            f"{counts['structured_files']} structured files, {counts['repository_identical_files']} exact repository byte matches. "
            "Remaining mappings are provisional at family level; source adapters establish subset identity.",
            f['discovery']['observed_structure'],f['discovery']['practical_use_and_limits'],
            '| Dataset / source locator | Directness and units | Rights; use limits |','|---|---|---|'])
        for did in f['manifest_dataset_ids']:
            if did not in rows:raise ValueError(f'Unknown dataset ID {did}')
            r=rows[did]; card=r['source_card']; path=ROOT/f'docs/cards/{card}.md'
            source=f'[{card}](../cards/{card}.md)' if path.exists() else f'`{card}`'
            family_text.append(f"| `{did}` — {source}; {cell(r['source_artifact'])} | {cell(r['extraction_method'])}; "
                               f"published: {cell(r['units_as_published'])}; registry: {cell(r['units_in_registry'])} | "
                               f"{cell(r['license_access'])}; {cell(r['caveat'])} |")
        family_text.append('Prior authority: `'+f['last_qualified_task']+'`; scientific labels and additional uncertainty/use metadata remain in '
                           '[AVAILABLE_DATA_REGISTER](../../puckworks/data/AVAILABLE_DATA_REGISTER.json).')
    for name,body in [('snapshot',overview),('reconciliation','\n\n'.join(reconciliation[:3])+'\n\n'+'\n'.join(reconciliation[3:])),('families','\n\n'.join(family_text))]:
        pattern=rf'<!-- {name}:start -->.*?<!-- {name}:end -->'
        if len(re.findall(pattern,text,flags=re.S))!=1:raise ValueError('Missing/duplicate generated block '+name)
        text=re.sub(pattern,lambda _:f'<!-- {name}:start -->\n{body}\n<!-- {name}:end -->',text,flags=re.S)
    return re.sub(r'\|\n\n(?=\|)', '|\n', text)


if __name__=='__main__':
    GUIDE.write_text(render())
