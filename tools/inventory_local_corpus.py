#!/usr/bin/env python3
"""Read-only private census and allowlisted public projection; never executes data.

Identity covers entry names, types, sizes, hashes and mappings, not scan times.
Archive members are logical entries, never extra physical files. See the guide.
"""
from __future__ import annotations
import argparse
import collections
import csv
import gzip
import hashlib
import io
import json
import os
import re
from pathlib import Path, PurePosixPath
import stat
import tarfile
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'puckworks/data/LOCAL_CORPUS_FAMILY_INDEX.json'
MAX_BYTES = 64 * 1024**2
ARCHIVE_BYTES = 256 * 1024**2
MAX_MEMBERS = 10000
MAX_DEPTH = 2


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def config_path():
    return Path(os.environ.get('XDG_CONFIG_HOME', Path.home()/'.config'))/'puckworks/data_sources.json'


def resolve_roots(explicit):
    cfg = json.loads(config_path().read_text()) if config_path().exists() else {}
    primary = explicit or os.environ.get('PUCKWORKS_EXTERNAL_DATA_ROOT') or cfg.get('inventory',{}).get('root')
    roots = {'collection': str(Path(primary).absolute())} if primary else {}
    references = []
    for key, entry in sorted(cfg.get('sources', {}).items()):
        if not entry.get('path'):
            continue
        p = Path(entry['path']).absolute()
        covered = next((alias for alias, root in roots.items() if p.is_relative_to(Path(root))), None)
        references.append({'source_id': key, 'path': str(p), 'covered_by': covered,
                           'accessible': p.is_dir()})
        if not covered:
            # Registered roots only; never recursively search home for sources.
            alias='registered_' + str(len(roots))
            roots[alias] = str(p)
            references[-1]['covered_by']=alias
    return roots, references


def entries(roots, excluded):
    out = {}; problems = []
    def visit(alias, root, p):
        rel = p.relative_to(root).as_posix()
        key = (alias, rel)
        try:
            s = p.lstat()
            kind = ('symlink' if stat.S_ISLNK(s.st_mode) else 'directory' if stat.S_ISDIR(s.st_mode)
                    else 'file' if stat.S_ISREG(s.st_mode) else 'special')
            out[key] = {'root_alias': alias, 'relative_path': rel, 'file_type': kind,
                        'bytes': s.st_size if kind == 'file' else 0,
                        'stat': [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns],
                        'mode': stat.S_IMODE(s.st_mode)}
            if kind == 'symlink':
                out[key]['link_target'] = os.readlink(p)
                target=Path(os.path.abspath(p.parent/out[key]['link_target']))
                out[key]['link_scope']='LEXICALLY_WITHIN_DECLARED_ROOT' if any(target.is_relative_to(Path(r)) for r in roots.values()) else 'OUTSIDE_DECLARED_ROOT_NOT_FOLLOWED'
                out[key]['inspection_status'] = 'SYMLINK_NOT_FOLLOWED'
            if kind == 'directory':
                if any(p == e or p.is_relative_to(e) for e in excluded):
                    out[key]['inspection_status'] = 'EXCLUDED_OUTPUT_SUBTREE'
                    return
                try:
                    with os.scandir(p) as it:
                        children = sorted(it, key=lambda x:x.name)
                    for child in children:
                        visit(alias, root, Path(child.path))
                except OSError as exc:
                    out[key]['inspection_status'] = 'UNREADABLE_DIRECTORY'
                    problems.append({'root_alias':alias, 'relative_path':rel, 'error':type(exc).__name__})
        except OSError as exc:
            out[key] = {'root_alias':alias,'relative_path':rel,'file_type':'unreadable','bytes':0,
                        'inspection_status':type(exc).__name__}
    for alias, value in sorted(roots.items()):
        p = Path(value)
        if not p.is_dir():
            problems.append({'root_alias':alias,'error':'MISSING_ROOT'})
        else:
            visit(alias,p,p)
    return out, problems


def mapping(rel, families, root_family=None):
    parts = Path(rel).parts
    matches = [parts[0]] if parts and parts[0] in families else [root_family] if root_family in families else []
    if matches:
        fid = matches[0]
        return fid, 'PROVISIONAL_DIRECTORY_MAPPING', families[fid]['manifest_dataset_ids']
    return None, 'UNRESOLVED', []


def role(rel, family, manifest_roles):
    p = Path(rel); low = rel.lower()
    if '-private/' in low or low.startswith('raw_data_assessment_'):
        if any(x in p.parts for x in ('runs','run','fields','model_results')) or p.name in {'p','U','C','phi'}:
            return 'model_output'
        return 'private_analysis'
    if 'normalized' in low:
        return 'normalized_data'
    if p.suffix.lower() in {'.pdf','.xml'}:
        return 'literature'
    if p.suffix.lower() in {'.py','.m','.ipynb','.c','.cpp','.f90'}:
        return 'author_code'
    if family == 'visualizer' or p.suffix == '.shot':
        return 'machine_log'
    if p.suffix.lower() in {'.fig','.png','.tif','.jpg','.svg'}:
        return 'model_output' if 'model' in low or 'prediction' in low else 'unresolved'
    if family == 'pannusch2024' and ('Experimental_data/' in rel or 'Experimental_data_validation/' in rel):
        if p.suffix.lower() in {'.xls','.xlsx','.txt','.mat'}: return 'experimental_measurement'
    if family == 'schmieder2023' and p.suffix.lower() == '.xlsx':
        return 'experimental_measurement' if 'TableS1' in p.name else 'normalized_data'
    if p.suffix.lower() in {'.csv','.tsv'} and family:
        methods = manifest_roles.get((family.lower(), p.stem.lower()), '')
        if 'digitiz' in methods or 'digitis' in methods or 'digitized' in p.stem.lower(): return 'digitized_figure'
        if '_computed' in p.stem.lower() or 'fitted_curve' in p.stem.lower(): return 'model_output'
        if 'simulat' in methods or 'model-generated' in methods: return 'model_output'
        return 'normalized_data'
    if family and p.suffix.lower() in {'.xls','.xlsx','.mat'}:
        return 'unresolved'  # extension alone cannot establish measured versus generated
    return 'unresolved'


def protected(rel):
    low = rel.lower()
    return ('angeloni2023' in low or any(x in low for x in ('holdout','protected','sealed','reserved')))


def stream_hash(path, expected):
    h = hashlib.sha256()
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as f:
        s = os.fstat(f.fileno())
        before = [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
        if before != expected:
            return None, 'UNSTABLE'
        for block in iter(lambda:f.read(1024**2), b''):
            h.update(block)
        s = os.fstat(f.fileno())
        after = [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
    s = path.lstat()
    final = [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
    return (h.hexdigest(), 'HASHED') if before == after == final else (None, 'UNSTABLE')


def structure(data, name):
    """Non-scoring structure only. Headers remain private; no real fixture exports."""
    suffix = Path(name).suffix.lower()
    if suffix in {'.csv','.tsv'}:
        text = data.decode('utf-8-sig')
        lines = [line for line in text.splitlines() if not line.lstrip().startswith('#')]
        if not lines:
            return {'kind':'table','inspection_status':'NO_TABLE_AFTER_COMMENTS','records':None}
        delimiter = '\t' if suffix == '.tsv' else ';' if lines[0].count(';') > lines[0].count(',') else ','
        rows = csv.reader(io.StringIO('\n'.join(lines)), delimiter=delimiter, strict=True)
        header = next(rows, [])
        widths = collections.Counter(); n = 0
        for row in rows:
            if row:
                n += 1; widths[len(row)] += 1
        return {'kind':'table','columns':header,'records':n,'row_widths':dict(widths),
                'delimiter':delimiter, 'schema_signature':digest(header),
                'inspection_status':'STRUCTURE_FULL' if all(w == len(header) for w in widths) else 'RAGGED_TABLE',
                'records_are_observations':False}
    if suffix in {'.json','.jsonl'}:
        records = [json.loads(line) for line in data.splitlines() if line.strip()] if suffix == '.jsonl' else json.loads(data)
        if isinstance(records, dict):
            return {'kind':'json','keys':sorted(records),'schema_signature':digest(sorted(records)),
                    'inspection_status':'STRUCTURE_FULL','records':None}
        keys = collections.Counter()
        for item in records if isinstance(records,list) else []:
            if isinstance(item,dict): keys[tuple(sorted(item))] += 1
        return {'kind':'json','records':len(records) if isinstance(records,list) else None,
                'schemas':[{'keys':list(k),'records':v} for k,v in sorted(keys.items())],
                'schema_signature':digest(sorted(keys)), 'inspection_status':'STRUCTURE_FULL'}
    if suffix in {'.xlsx','.xls'}:
        sheets=[]
        if suffix == '.xlsx':
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if sum(x.file_size for x in z.infolist()) > ARCHIVE_BYTES:
                    raise ValueError('WORKBOOK_EXPANSION_LIMIT')
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(data),read_only=True,data_only=False,keep_links=False)
            try:
                for ws in wb:
                    n=0; width=0; headers=[]
                    for row in ws.iter_rows(values_only=True):
                        n+=1; width=max(width,len(row))
                        if n<=4: headers.append([str(x)[:160] if x is not None else None for x in row[:30]])
                    sheets.append({'sheet':ws.title,'rows':n,'columns':width,'header_preview':headers})
            finally: wb.close()
        else:
            import xlrd
            wb=xlrd.open_workbook(file_contents=data,on_demand=True)
            try:
                for ws in wb.sheets():
                    sheets.append({'sheet':ws.name,'rows':ws.nrows,'columns':ws.ncols,
                                   'header_preview':[ws.row_values(i)[:30] for i in range(min(4,ws.nrows))]})
            finally: wb.release_resources()
        return {'kind':'workbook','sheets':sheets,'inspection_status':'STRUCTURE_FULL',
                'schema_signature':digest([(s['sheet'],s['columns']) for s in sheets])}
    if suffix == '.mat':
        from scipy.io import whosmat
        arrays=whosmat(io.BytesIO(data))
        return {'kind':'array','variables':arrays,'schema_signature':digest(arrays),'inspection_status':'STRUCTURE_FULL'}
    if suffix in {'.npz','.npy'}:
        if suffix == '.npz':
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if sum(x.file_size for x in z.infolist()) > ARCHIVE_BYTES:
                    raise ValueError('ARRAY_EXPANSION_LIMIT')
        import numpy as np
        obj=np.load(io.BytesIO(data),allow_pickle=False)
        if suffix == '.npz':
            with obj:
                arrays=[(k,list(obj[k].shape),str(obj[k].dtype)) for k in sorted(obj.files)]
        else: arrays=[('array',list(obj.shape),str(obj.dtype))]
        return {'kind':'array','variables':arrays,'schema_signature':digest(arrays),'inspection_status':'STRUCTURE_FULL'}
    if suffix in {'.md','.txt','.m','.py','.xml','.shot'}:
        text=data.decode('utf-8')
        return {'kind':'text','lines':len(text.splitlines()),'inspection_status':'TEXT_DECODED_NOT_SEMANTICALLY_REVIEWED'}
    return {'inspection_status':'FORMAT_NOT_PARSED'}


def inspect_bytes(data, name):
    try: return structure(data,name)
    except Exception as exc:
        return {'inspection_status':'PARSE_FAILED','diagnostic':type(exc).__name__}


def archive_members(data, name, depth=0, budget=None):
    budget = budget if budget is not None else [ARCHIVE_BYTES, MAX_MEMBERS]
    if depth >= MAX_DEPTH:
        return [{'member':'','inspection_status':'ARCHIVE_DEPTH_LIMIT'}]
    result=[]
    try:
        if name.lower().endswith('.gz') and not name.lower().endswith(('.tar.gz','.tgz')):
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as f: payload=f.read(min(MAX_BYTES,budget[0])+1)
            if len(payload)>min(MAX_BYTES,budget[0]):
                return [{'member':Path(name).name[:-3],'inspection_status':'ARCHIVE_EXPANSION_LIMIT'}]
            budget[0]-=len(payload);budget[1]-=1
            return [{'member':Path(name).name[:-3], 'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),
                     **inspect_bytes(payload,name[:-3])}]
        iszip=zipfile.is_zipfile(io.BytesIO(data))
        container=zipfile.ZipFile(io.BytesIO(data)) if iszip else tarfile.open(fileobj=io.BytesIO(data),mode='r:*')
        with container:
            members=container.infolist() if iszip else container
            for m in members:
                if budget[1]<=0:
                    result.append({'member':'','inspection_status':'ARCHIVE_MEMBER_LIMIT'});break
                budget[1]-=1
                member=m.filename if iszip else m.name
                size=m.file_size if iszip else m.size
                row={'member':member,'bytes':size}
                unsafe=PurePosixPath(member).is_absolute() or '..' in PurePosixPath(member).parts or '\\' in member
                link=stat.S_ISLNK(m.external_attr >> 16) if iszip else m.issym() or m.islnk()
                directory=m.is_dir() if iszip else m.isdir()
                if unsafe or link:row['inspection_status']='UNSAFE_MEMBER_NOT_OPENED'
                elif directory:row['inspection_status']='DIRECTORY'
                elif protected(member):row['inspection_status']='PROTECTED_METADATA_ONLY'
                elif size>MAX_BYTES or size>budget[0]:row['inspection_status']='ARCHIVE_EXPANSION_LIMIT'
                else:
                    f=container.open(m) if iszip else container.extractfile(m)
                    if f is None:row['inspection_status']='SPECIAL_MEMBER_NOT_OPENED'
                    else:
                        with f:payload=f.read(min(MAX_BYTES,budget[0])+1)
                        if len(payload)>min(MAX_BYTES,budget[0]):row['inspection_status']='ARCHIVE_EXPANSION_LIMIT'
                        else:
                            budget[0]-=len(payload)
                            row['sha256']=hashlib.sha256(payload).hexdigest()
                            row.update(inspect_bytes(payload,member))
                            if member.lower().endswith(('.zip','.tar','.tgz','.gz')):
                                row['members']=archive_members(payload,member,depth+1,budget)
                result.append(row)
        return result
    except Exception as exc:
        return result + [{'member':'','inspection_status':'ARCHIVE_PARSE_FAILED','diagnostic':type(exc).__name__}]


def scan(roots, output, index, references=(), comparison_repos=()):
    output=Path(output).absolute()
    if any(Path(value).absolute() == output or Path(value).absolute().is_relative_to(output) for value in roots.values()):
        raise ValueError('Output must not be a source root or its ancestor')
    output.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(output,0o700)
    start=now(); initial,problems=entries(roots,[output])
    families={f['family_id']:f for f in index['families']}
    source_families={f.get('external_corpus_id'):f['family_id'] for f in index['families'] if f.get('external_corpus_id')}
    root_families={ref['covered_by']:source_families[ref['source_id']] for ref in references
                   if ref.get('covered_by') and ref['source_id'] in source_families
                   and ref['path']==roots.get(ref['covered_by'])
                   and not any((Path(ref['path'])/fid).is_dir() for fid in families)}
    methods={}
    with (ROOT/'puckworks/data/MANIFEST.csv').open() as f:
        for m in csv.DictReader(f):
            a,b=m['dataset_id'].split('/',1) if '/' in m['dataset_id'] else (m['dataset_id'],'')
            methods[(a.lower(),b.lower())]=m['extraction_method'].lower()
    # Repository matches establish exact file identity, never independent experiments.
    packaged=collections.defaultdict(list)
    canonical_paths={}
    for p in sorted((ROOT/'puckworks/data').rglob('*')):
        if p.is_file() and not p.is_symlink() and p.stat().st_size<=MAX_BYTES:
            h=hashlib.sha256(p.read_bytes()).hexdigest();packaged[h].append(p.relative_to(ROOT).as_posix())
            canonical_paths[p.relative_to(ROOT/'puckworks/data').as_posix()]=h
    for repo in comparison_repos:
        repo=Path(repo)
        for p in sorted(repo.rglob('*')):
            if p.is_file() and not p.is_symlink() and '.git' not in p.parts and p.stat().st_size<=MAX_BYTES:
                h=hashlib.sha256(p.read_bytes()).hexdigest();packaged[h].append(repo.name+':'+p.relative_to(repo).as_posix())
    records=[]
    for key,r in sorted(initial.items()):
        rel=r['relative_path'];fid,ms,ids=mapping(rel,families,root_families.get(r['root_alias']))
        r.update(family_id=fid,mapping_status=ms,dataset_ids=ids,subset_id=None,
                 dataset_mapping_status='FAMILY_CANDIDATE_IDS_NOT_VERIFIED_SUBSET_JOINS',
                 content_role=role(rel,fid,methods),content_role_status='PROVISIONAL_ROUTING_NOT_SCIENTIFIC_QUALIFICATION',hash_status='NOT_REGULAR_FILE')
        if r['file_type']=='file':
            path=Path(roots[r['root_alias']])/rel
            try:
                if not r['mode'] & 0o444: raise PermissionError('no read bits')
                r['sha256'],r['hash_status']=stream_hash(path,r['stat'])
                r['repository_matches']=packaged.get(r['sha256'],[])
                r['canonical_same_path_identity']=('MATCH' if canonical_paths[rel]==r['sha256'] else 'MISMATCH') if rel in canonical_paths else 'NO_SAME_PATH_COMPARAND'
                if r['repository_matches']:
                    r['mapping_status']='EXACT_BYTES_PACKAGED_FILE_FAMILY' if fid else ms
                if r['hash_status']!='HASHED':r['inspection_status']=r['hash_status']
                elif protected(rel):r['inspection_status']='PROTECTED_HASH_ONLY'
                elif '-private/' in rel or rel.startswith('raw_data_assessment_') or not fid:
                    r['inspection_status']='HASH_ONLY_GENERATED_OR_UNRESOLVED'
                elif r['bytes']>MAX_BYTES:r['inspection_status']='SIZE_LIMIT_HASH_ONLY'
                else:
                    data=path.read_bytes()
                    if hashlib.sha256(data).hexdigest()!=r['sha256']:
                        r['hash_status']='UNSTABLE';r['sha256']=None;r['inspection_status']='UNSTABLE'
                    else:
                        r.update(inspect_bytes(data,rel))
                        if rel.lower().endswith(('.zip','.tar','.tgz','.gz')):
                            r['members']=archive_members(data,rel)
                            r['inspection_status']='ARCHIVE_LISTED_BOUNDED_CONTENT'
            except OSError as exc:
                r.update(hash_status='UNREADABLE',inspection_status='UNREADABLE',diagnostic=type(exc).__name__)
        records.append(r)
    final,final_problems=entries(roots,[output]);changes=[]
    for key in sorted(set(initial)|set(final)):
        if key not in initial:
            changes.append({'entry':key,'change':'ADDED'})
            extra=final[key]
            extra.update(hash_status='NOT_HASHED_CONCURRENT_ADDITION',inspection_status='ADDED_DURING_SCAN',
                         family_id=None,mapping_status='UNRESOLVED',dataset_ids=[],content_role='unresolved')
            records.append(extra)
        elif key not in final:
            changes.append({'entry':key,'change':'REMOVED'})
            initial[key]['sha256']=None;initial[key]['hash_status']='UNSTABLE';initial[key]['inspection_status']='REMOVED_DURING_SCAN'
        elif initial[key].get('stat')!=final[key].get('stat'):
            changes.append({'entry':key,'change':'CHANGED'})
            initial[key]['sha256']=None;initial[key]['hash_status']='UNSTABLE';initial[key]['inspection_status']='UNSTABLE'
    records.sort(key=lambda r:(r['root_alias'],r['relative_path']))
    hashes=collections.Counter(r.get('sha256') for r in records if r.get('sha256'))
    for r in records:
        if r.get('sha256') and hashes[r['sha256']]>1:r['duplicate_group']=r['sha256']
    def link_members(members):
        for member in members:
            member['physical_duplicate_count'] = hashes.get(member.get('sha256'),0)
            if member.get('members'): link_members(member['members'])
    for r in records:
        if r.get('members'): link_members(r['members'])
    identity=[{k:r.get(k) for k in ('root_alias','relative_path','file_type','bytes','sha256','hash_status','family_id','mapping_status','dataset_ids')} for r in records]
    snapshot={'schema_version':1,'started':start,'finished':now(),'roots':roots,'registered_references':list(references),
              'content_identity':digest(identity),'entries':records,'problems':problems+final_problems,'concurrent_changes':changes,
              'inspection_contract':{'protected':'HASH_ONLY_NO_VALUES','private_outputs':'HASH_ONLY',
               'structured':'FULL_LIGHTWEIGHT_STRUCTURE_WITH_SIZE_LIMITS','semantic':'SEPARATE_CURATED_REVIEW',
               'max_bytes':MAX_BYTES,'archive_expansion_bytes':ARCHIVE_BYTES,'archive_depth':MAX_DEPTH,'archive_members':MAX_MEMBERS}}
    (output/'reconciliation.json').write_text(json.dumps(reconcile(snapshot,index),sort_keys=True,indent=2)+'\n')
    (output/'manifest.json').write_text(json.dumps(snapshot,sort_keys=True,indent=2)+'\n')
    return snapshot


def validate_snapshot(snapshot, index):
    """Validate private manifest structure and canonical IDs without target access."""
    if snapshot.get('schema_version') != 1:
        raise ValueError('Unsupported manifest schema')
    known={f['family_id']:set(f['manifest_dataset_ids']) for f in index['families']}
    seen=set()
    for row in snapshot['entries']:
        key=(row['root_alias'],row['relative_path'])
        if key in seen: raise ValueError('Duplicate physical entry identity')
        seen.add(key)
        if row['root_alias'] not in snapshot['roots']:
            raise ValueError('Unknown root alias')
        rel=PurePosixPath(row['relative_path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('Invalid relative entry path')
        if row['file_type'] not in {'file','directory','symlink','special','unreadable'}:
            raise ValueError('Invalid file type')
        if type(row['bytes']) is not int or row['bytes'] < 0:
            raise ValueError('Invalid byte count')
        fid=row.get('family_id')
        if fid is not None and fid not in known:
            raise ValueError('Unknown family ID')
        if not set(row.get('dataset_ids',[])) <= known.get(fid,set()):
            raise ValueError('Unknown family dataset ID')
        if row.get('hash_status') == 'HASHED' and not re.fullmatch(r'[0-9a-f]{64}',row.get('sha256') or ''):
            raise ValueError('Missing stable SHA-256')
    return True


def project(snapshot,index):
    """Explicit allowlist: no path/hash/schema/header/free-text from entries exported."""
    validate_snapshot(snapshot,index)
    def totals(rows):
        files=[r for r in rows if r['file_type']=='file']
        return {'files':len(files),'bytes':sum(r['bytes'] for r in files),
                'hashed':sum(r.get('hash_status')=='HASHED' for r in files),
                'unique_sha256_contents':len({r['sha256'] for r in files if r.get('sha256')}),
                'structured_files':sum(r.get('inspection_status')=='STRUCTURE_FULL' for r in files),
                'archive_files':sum('members' in r for r in files),
                'repository_identical_files':sum(bool(r.get('repository_matches')) for r in files),
                'canonical_same_path_mismatches':sum(r.get('canonical_same_path_identity')=='MISMATCH' for r in files)}
    if not re.fullmatch(r'[0-9a-f]{64}', snapshot['content_identity']):
        raise ValueError('Invalid content identity')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T[0-9:.+Z-]+', snapshot['started']):
        raise ValueError('Invalid scan timestamp')
    rows=snapshot['entries']; known={f['family_id'] for f in index['families']}
    families=[]
    for fid in sorted(known):
        found=[r for r in rows if r.get('family_id')==fid]
        families.append({'family_id':fid,'access':'FOUND' if found else 'NOT_FOUND_IN_SCANNED_ROOTS',**totals(found)})
    def flatten(members):
        for member in members:
            yield member
            yield from flatten(member.get('members',[]))
    members=[m for r in rows for m in flatten(r.get('members',[]))]
    roles=('experimental_measurement','machine_log','literature','author_code','digitized_figure','normalized_data','model_output','private_analysis','unrelated','unresolved')
    return {'schema_version':1,'snapshot_date':snapshot['started'][:10],
            'content_identity':snapshot['content_identity'],
            'status':'SCANNED_WITH_DECLARED_LIMITS' if any(r['file_type']=='file' for r in rows) else 'PARTIAL_NOT_SCANNED',
            'root_count':len(snapshot['roots']), 'unavailable_root_count':len({p['root_alias'] for p in snapshot['problems'] if p['error']=='MISSING_ROOT'}),
            'archive_member_entries':len(members),
            'archive_member_structures':sum(m.get('inspection_status')=='STRUCTURE_FULL' for m in members),
            'archive_member_parse_failures':sum(m.get('inspection_status') in ('PARSE_FAILED','ARCHIVE_PARSE_FAILED') for m in members),
            'archive_members_matching_physical_files':sum(bool(m.get('physical_duplicate_count')) for m in members),
            'parse_failures':sum(r.get('inspection_status')=='PARSE_FAILED' for r in rows),
            'ragged_tables':sum(r.get('inspection_status')=='RAGGED_TABLE' for r in rows),
            'hardlink_extra_entries':sum(n-1 for n in collections.Counter(tuple(r['stat'][:2]) for r in rows if r['file_type']=='file').values()),
            'entry_count':len(rows),'symlinks':sum(r['file_type']=='symlink' for r in rows),
            'unreadable_entries':sum(r.get('inspection_status') in ('UNREADABLE','UNREADABLE_DIRECTORY') for r in rows),
            'unstable_files':sum(r.get('hash_status')=='UNSTABLE' for r in rows),
            'concurrent_entry_changes':len(snapshot['concurrent_changes']),
            'excluded_subtrees':sum(r.get('inspection_status')=='EXCLUDED_OUTPUT_SUBTREE' for r in rows),
            **totals(rows),'by_content_role':{role:totals([r for r in rows if r.get('content_role')==role]) for role in roles},
            'families':families,'unmapped':totals([r for r in rows if not r.get('family_id')]),
            'registered_dataset_id_count':len({did for f in index['families'] for did in f['manifest_dataset_ids']}),
            'observation_count':'UNKNOWN_NOT_A_FILE_COUNT'}


def reconcile(snapshot, index):
    known = {f['family_id']: f for f in index['families']}
    result = {'families': [], 'unregistered_groups': [], 'claims': []}
    for fid, family in sorted(known.items()):
        rows = [r for r in snapshot['entries'] if r.get('family_id') == fid and r['file_type'] == 'file']
        matched = [r for r in rows if r.get('repository_matches')]
        result['families'].append({'family_id': fid, 'status': 'REGISTERED_AND_FOUND' if rows else 'REGISTERED_UNAVAILABLE',
            'files': len(rows), 'exact_repository_matches': len(matched),
            'same_path_identity_mismatches':sum(r.get('canonical_same_path_identity')=='MISMATCH' for r in rows),
            'remaining_identity': 'PROVISIONAL_UNTIL_SOURCE_ADAPTER_VERIFICATION',
            'dataset_ids': family['manifest_dataset_ids']})
    groups = collections.defaultdict(list)
    for row in snapshot['entries']:
        if not row.get('family_id') and row['file_type'] == 'file':
            groups[(row['root_alias'], Path(row['relative_path']).parts[0])].append(row)
    for i, ((alias, path), rows) in enumerate(sorted(groups.items()), 1):
        result['unregistered_groups'].append({'private_group_id': f'UNRESOLVED-{i:03}', 'root_alias': alias,
            'relative_path': path, 'files': len(rows), 'bytes': sum(r['bytes'] for r in rows),
            'status': 'FOUND_NOT_A_REGISTERED_SOURCE_FAMILY',
            'next_step': 'Review source versus generated lineage before assigning any new dataset ID'})
    return result


def compare(before,after):
    a={(r['root_alias'],r['relative_path']):r for r in before['entries']};b={(r['root_alias'],r['relative_path']):r for r in after['entries']}
    return {'added':sorted(set(b)-set(a)),'removed':sorted(set(a)-set(b)),
            'changed_hashes':[k for k in sorted(set(a)&set(b)) if a[k].get('sha256')!=b[k].get('sha256')],
            'changed_mappings':[k for k in sorted(set(a)&set(b)) if [a[k].get(x) for x in ('family_id','dataset_ids','mapping_status')]!=[b[k].get(x) for x in ('family_id','dataset_ids','mapping_status')]]}


def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('scan');s.add_argument('--root');s.add_argument('--output',required=True);s.add_argument('--compare-repo',action='append',default=[])
    s=sub.add_parser('project');s.add_argument('manifest');s.add_argument('--output',required=True)
    s=sub.add_parser('compare');s.add_argument('before');s.add_argument('after');s.add_argument('--output',required=True)
    s=sub.add_parser('validate');s.add_argument('manifest')
    s=sub.add_parser('query');s.add_argument('manifest');s.add_argument('--family',required=True)
    a=p.parse_args();index=json.loads(INDEX.read_text())
    if a.command=='scan':
        roots,refs=resolve_roots(a.root)
        if not roots:raise SystemExit('No explicit, environment or registered root; provide --root')
        snapshot=scan(roots,a.output,index,refs,a.compare_repo);print(json.dumps(project(snapshot,index),indent=2))
    elif a.command=='project':
        result=project(json.loads(Path(a.manifest).read_text()),index)
        Path(a.output).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    elif a.command=='validate':
        validate_snapshot(json.loads(Path(a.manifest).read_text()),index);print('Manifest schema and canonical IDs valid')
    elif a.command=='compare':
        Path(a.output).write_text(json.dumps(compare(json.loads(Path(a.before).read_text()),json.loads(Path(a.after).read_text())),indent=2)+'\n')
    else:
        snapshot=json.loads(Path(a.manifest).read_text()); selected=[r for r in snapshot['entries'] if r.get('family_id')==a.family and r['file_type']=='file']
        if not selected:raise SystemExit('Known external family unavailable in this snapshot')
        for r in selected:
            path=Path(snapshot['roots'][r['root_alias']])/r['relative_path']
            try:
                s=path.lstat();h,status=stream_hash(path,[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns])
                verified=status=='HASHED' and h==r.get('sha256')
            except OSError:verified=False
            print(json.dumps({'local_path':str(path),'identity_matches_snapshot':verified,'inspection_status':r.get('inspection_status'),'records':r.get('records'),'lines':r.get('lines'),'schema_signature':r.get('schema_signature'),'sheets':[{k:s[k] for k in ('sheet','rows','columns')} for s in r.get('sheets',[])]}))

if __name__=='__main__':main()
