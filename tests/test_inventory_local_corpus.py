"""Synthetic only: never reads the owner's corpus or real shot fixtures."""
import gzip
import io
import json
import os
import zipfile

import pytest
from tools import inventory_local_corpus as inv


@pytest.fixture
def setup(tmp_path, monkeypatch):
    repo=tmp_path/'repo'; (repo/'puckworks/data').mkdir(parents=True)
    (repo/'puckworks/data/MANIFEST.csv').write_text('dataset_id,extraction_method\nalpha/table,transcription\n')
    monkeypatch.setattr(inv,'ROOT',repo)
    root=tmp_path/'data'; root.mkdir()
    (root/'alpha').mkdir()
    index={'families':[{'family_id':'alpha','manifest_dataset_ids':['alpha/table']}]}
    return root,tmp_path/'out',index


def test_duplicates_rename_missing_and_reproducibility(setup):
    root,out,index=setup
    p=root/'alpha/a.csv';p.write_text('time_s,value\n0,1\n')
    (root/'alpha/b.csv').write_bytes(p.read_bytes())
    os.link(p,root/'alpha/hard.csv')
    a=inv.scan({'collection':str(root)},out,index)
    b=inv.scan({'collection':str(root)},out,index)
    assert a['content_identity']==b['content_identity']
    assert inv.project(a,index)['files']==3
    assert inv.project(a,index)['unique_sha256_contents']==1
    p.rename(root/'alpha/new.csv')
    (root/'alpha/b.csv').unlink()
    c=inv.scan({'collection':str(root)},out,index)
    diff=inv.compare(a,c)
    assert len(diff['removed'])==2 and len(diff['added'])==1
    next(r for r in c['entries'] if r['relative_path']=='alpha/hard.csv')['dataset_ids']=['alpha/new']
    assert inv.compare(b,c)['changed_mappings']


def test_unreadable_missing_symlink_protected_and_excluded(setup):
    root,out,index=setup
    (root/'alpha/protected.csv').write_text('target\n42\n')
    p=root/'alpha/unreadable.csv';p.write_text('x\n1\n');p.chmod(0)
    (root/'escape').symlink_to(root.parent,target_is_directory=True)
    nested=root/'output'
    a=inv.scan({'collection':str(root),'missing':str(root/'absent')},nested,index)
    statuses={r['relative_path']:r.get('inspection_status') for r in a['entries']}
    assert statuses['escape']=='SYMLINK_NOT_FOLLOWED'
    assert statuses['alpha/protected.csv']=='PROTECTED_HASH_ONLY'
    assert statuses['alpha/unreadable.csv']=='UNREADABLE'
    assert statuses['output']=='EXCLUDED_OUTPUT_SUBTREE'
    assert inv.project(a,index)['unavailable_root_count']==1
    p.chmod(0o600)


def zipped(items):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        for name,data in items:z.writestr(name,data)
    return b.getvalue()


def test_nested_archives_traversal_limits_and_malformed(monkeypatch):
    inner=zipped([('table.csv','x,y\n1,2\n')])
    outer=zipped([('../escape','bad'),('nested.zip',inner),('bad.json','{')])
    rows=inv.archive_members(outer,'a.zip')
    assert rows[0]['inspection_status']=='UNSAFE_MEMBER_NOT_OPENED'
    assert rows[1]['members'][0]['records']==1
    assert rows[2]['inspection_status']=='PARSE_FAILED'
    assert inv.archive_members(inner,'a.zip',depth=inv.MAX_DEPTH)[0]['inspection_status']=='ARCHIVE_DEPTH_LIMIT'
    monkeypatch.setattr(inv,'MAX_BYTES',2)
    assert inv.archive_members(inner,'a.zip')[0]['inspection_status']=='ARCHIVE_EXPANSION_LIMIT'
    assert inv.archive_members(gzip.compress(b'x'*100),'a.jsonl.gz')[0]['inspection_status']=='ARCHIVE_EXPANSION_LIMIT'


def test_variants_and_no_silent_zero():
    assert inv.structure(b'# comment\na;b\n1;2\n','a.csv')['records']==1
    assert inv.structure(b'a,b\n1\n','a.csv')['inspection_status']=='RAGGED_TABLE'
    assert inv.inspect_bytes(b'a,b\n"broken','a.csv')['inspection_status']=='PARSE_FAILED'
    assert inv.structure(b'# no table\n','a.csv')['records'] is None
    assert inv.inspect_bytes(b'bad','a.mat')['inspection_status']=='PARSE_FAILED'


def test_unstable_file_is_not_certified(setup,monkeypatch):
    root,out,index=setup
    p=root/'alpha/a.csv';p.write_text('a\n1\n')
    original=inv.stream_hash
    def change(path,expected):
        result=original(path,expected)
        path.write_text('a\n2\n')
        return result
    monkeypatch.setattr(inv,'stream_hash',change)
    s=inv.scan({'collection':str(root)},out,index)
    r=next(r for r in s['entries'] if r['file_type']=='file')
    assert r['hash_status']=='UNSTABLE' and r['sha256'] is None


def test_public_allowlist_blocks_private_payloads(setup):
    root,out,index=setup
    (root/'alpha/a.csv').write_text('name,email,token\nSynthetic,private@example.invalid,SECRET\n')
    s=inv.scan({'collection':str(root)},out,index)
    for r in s['entries']:
        r['permission_email']='PRIVATE_CORRESPONDENCE'
        r['raw_shot']={'name':'PERSONAL_IDENTIFIER','token':'CREDENTIAL'}
    text=json.dumps(inv.project(s,index))
    for secret in [str(root),'permission_email','PRIVATE_CORRESPONDENCE','PERSONAL_IDENTIFIER','CREDENTIAL','private@example','raw_shot','a.csv']:
        assert secret not in text
    s['started']='2026-01-01PRIVATE_CORRESPONDENCE'
    with pytest.raises(ValueError):inv.project(s,index)


def test_missing_root_is_partial(setup):
    root,out,index=setup
    s=inv.scan({'collection':str(root/'missing')},out,index)
    assert inv.project(s,index)['status']=='PARTIAL_NOT_SCANNED'
    assert inv.reconcile(s,index)['families'][0]['status']=='REGISTERED_UNAVAILABLE'


def test_symlink_hash_refused(tmp_path):
    p=tmp_path/'real';p.write_text('x');q=tmp_path/'link';q.symlink_to(p)
    with pytest.raises(OSError):inv.stream_hash(q,[])


def test_registered_source_specific_root_retains_family(setup,monkeypatch,tmp_path):
    root,out,index=setup
    index['families'][0]['external_corpus_id']='REGISTERED_ALPHA'
    config=tmp_path/'config.json'
    config.write_text(json.dumps({'sources':{'REGISTERED_ALPHA':{'path':str(root/'alpha')}}}))
    monkeypatch.setattr(inv,'config_path',lambda:config)
    monkeypatch.delenv('PUCKWORKS_EXTERNAL_DATA_ROOT',raising=False)
    (root/'alpha/a.csv').write_text('x\n1\n')
    roots,refs=inv.resolve_roots(None)
    s=inv.scan(roots,out,index,refs)
    row=next(r for r in s['entries'] if r['file_type']=='file')
    assert row['family_id']=='alpha'
    assert inv.reconcile(s,index)['families'][0]['status']=='REGISTERED_AND_FOUND'


def test_output_cannot_replace_source_root(setup):
    root,out,index=setup
    with pytest.raises(ValueError):inv.scan({'collection':str(root)},root,index)


def test_same_path_is_not_identity(setup):
    root,out,index=setup
    packaged=inv.ROOT/'puckworks/data/alpha';packaged.mkdir()
    (packaged/'a.csv').write_text('x\n1\n')
    (root/'alpha/a.csv').write_text('x\n2\n')
    s=inv.scan({'collection':str(root)},out,index)
    assert inv.project(s,index)['canonical_same_path_mismatches']==1
    assert inv.reconcile(s,index)['families'][0]['remaining_identity']=='PROVISIONAL_UNTIL_SOURCE_ADAPTER_VERIFICATION'


def test_registered_collection_root_does_not_relabel_all_sources(setup,monkeypatch,tmp_path):
    root,out,index=setup
    index['families'][0]['external_corpus_id']='REGISTERED_ALPHA'
    config=tmp_path/'config.json';config.write_text(json.dumps({'sources':{'REGISTERED_ALPHA':{'path':str(root)}}}))
    monkeypatch.setattr(inv,'config_path',lambda:config)
    (root/'alpha/a.csv').write_text('x\n1\n');(root/'unregistered.txt').write_text('source unknown')
    roots,refs=inv.resolve_roots(str(root));s=inv.scan(roots,out,index,refs)
    assert next(r for r in s['entries'] if r['relative_path']=='unregistered.txt')['family_id'] is None
    assert next(r for r in s['entries'] if r['relative_path']=='alpha/a.csv')['family_id']=='alpha'


def test_manifest_schema_rejects_unknown_ids_and_duplicate_entries(setup):
    root,out,index=setup
    (root/'alpha/a.csv').write_text('x\n1\n');s=inv.scan({'collection':str(root)},out,index)
    assert inv.validate_snapshot(s,index)
    row=next(r for r in s['entries'] if r['file_type']=='file')
    row['dataset_ids']=['unknown/id']
    with pytest.raises(ValueError,match='dataset ID'):inv.validate_snapshot(s,index)
    row['dataset_ids']=['alpha/table'];s['entries'].append(dict(row))
    with pytest.raises(ValueError,match='Duplicate'):inv.validate_snapshot(s,index)
