from __future__ import annotations
import subprocess,time
from pathlib import Path
from typing import Sequence

def run_capture(command: Sequence[str], cwd: Path, timeout_seconds: float) -> dict:
    started=time.time()
    try:
        cp=subprocess.run(list(command),cwd=cwd,text=True,capture_output=True,timeout=timeout_seconds)
        return {'command':list(command),'cwd':str(cwd),'exit_code':cp.returncode,'timed_out':False,'wall_seconds':time.time()-started,'stdout':cp.stdout,'stderr':cp.stderr}
    except subprocess.TimeoutExpired as exc:
        return {'command':list(command),'cwd':str(cwd),'exit_code':124,'timed_out':True,'wall_seconds':time.time()-started,'stdout':exc.stdout or '', 'stderr':exc.stderr or ''}
