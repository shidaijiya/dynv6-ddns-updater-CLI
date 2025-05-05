# 警告此依赖仅可以运行在windows
import os
import sys
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
import tempfile
from pathlib import Path
import portalocker
import psutil
from lib.log_utils import log_print



LOCK_FILE = "dynv6-update.lock"
LOCK_FILE_PATH = os.path.join(tempfile.gettempdir(), LOCK_FILE)



def pid_exists(pid):
    return psutil.pid_exists(pid)



def make_lock_file():
    try:
        lock_file = open(LOCK_FILE_PATH, 'w+')
        portalocker.lock(lock_file, portalocker.LOCK_EX | portalocker.LOCK_NB)
        lock_file.seek(0)
        lock_file.truncate()
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        return True
    except portalocker.LockException:
        return False



def process_does_not_exist():
    if Path(LOCK_FILE_PATH).exists():
        try:
            with open(LOCK_FILE_PATH, 'r') as f:
                content = f.read().strip()
                lock_file_pid = int(content)
        except Exception as e:
            log_print(f"Can't read lock file: {e}", "WARNING")
            exit(0)


        if pid_exists(lock_file_pid):
            log_print("Process already exists...Exiting current process", "INFO")
            exit(0)
        else:
            log_print("Previous process exited unexpectedly...lock file has been removed.", "WARNING")
            try:
                os.remove(LOCK_FILE_PATH)
            except Exception as e:
                log_print(f"Failed to remove lock file: {e}", "WARNING")
                exit(1)


    if not make_lock_file():
        log_print("Anther instance is running, can't unlock lock file", "INFO")
        exit(0)


