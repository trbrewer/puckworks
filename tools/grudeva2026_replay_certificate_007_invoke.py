"""Execute only the separately frozen, solver-free 007 replay certificate."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from puckworks.analysis import grudeva2026_replay_certificate_007 as certificate
from tools import grudeva2026_replay_reassessment_007_invoke as controller

if __name__=='__main__':
    raise SystemExit(controller.main(stages={'certify':certificate.certify},
        plan_path=certificate.PLAN,folder_name='replay_certification'))
