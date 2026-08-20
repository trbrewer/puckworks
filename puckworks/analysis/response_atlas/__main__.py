import argparse
from .runner import generate_bundle,validate_protocol,verify_bundle
p=argparse.ArgumentParser(); p.add_argument('command',choices=['validate','inventory','run','verify']); a=p.parse_args()
if a.command=='validate': validate_protocol()
elif a.command in ('inventory','run'): generate_bundle()
else: verify_bundle()
print('RP_A_001_'+a.command.upper()+'_OK')
