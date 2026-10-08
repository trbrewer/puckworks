"""External serial numerical controller; append-only task ledger."""
import datetime,fcntl,hashlib,json,os,pathlib,resource,signal,subprocess,sys,time
folder=pathlib.Path(__file__).parent
name,kind,phase,*command=sys.argv[1:]
assert kind in ('short','full') and phase in ('development','final','correction')
lock=(folder/'controller.lock').open('a')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
ledger=folder/'invocations.jsonl'
rows=[json.loads(s) for s in ledger.read_text().splitlines()] if ledger.exists() else []
starts={r['name']:r for r in rows if r['event']=='start'}
ends={r['name']:r for r in rows if r['event']=='end'}
assert starts.keys()==ends.keys(), 'unresolved invocation; reconcile before continuation'
assert name not in starts, 'attempt names cannot be reused'
full=sum(r['kind']=='full' for r in starts.values())
used=sum(r['seconds'] for r in ends.values())
assert used<3600 and (kind!='full' or full<24)
# Protect 8 slots / 1800 seconds. Final allocation may reserve more.
cap={'development':1800.,'final':2100.,'correction':3600.}[phase]
assert used<cap and (phase!='development' or kind!='full' or full<16)
ceiling=min(900.,cap-used)
root=pathlib.Path.cwd()
source={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root/'puckworks/analysis').glob('grudeva2026_*.py'))}
record={'name':name,'kind':kind,'phase':phase,'event':'start','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':command,'source_hashes':source,'time_ceiling':ceiling,'memory_bytes':2*1024**3}
def append(x):
 with ledger.open('a') as f:
  f.write(json.dumps(x,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
append(record)
start=time.perf_counter()
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONPATH=str(root),PYTHONHASHSEED='0')
code=None
with (folder/(name+'.log')).open('w') as log:
 try:
  p=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits,start_new_session=True)
  try: code=p.wait(timeout=ceiling)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
 except Exception as exc:
  log.write(repr(exc));code=125
elapsed=time.perf_counter()-start
finish={'event':'end','name':name,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':elapsed,'exit_code':code,'log_sha256':hashlib.sha256((folder/(name+'.log')).read_bytes()).hexdigest()}
finish['peak_rss_bytes']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024
if '--output' in command:
 artifact=pathlib.Path(command[command.index('--output')+1])
 finish['artifact_sha256']=hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.exists() else None
append(finish)
print(json.dumps(finish));print((folder/(name+'.log')).read_text()[-2500:])
sys.exit(0 if code in (0,2) else code)
