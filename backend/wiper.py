# wiper.py
import sys
import subprocess
from app import app, db, WipeLog # Import from your main app file
from datetime import datetime

def perform_wipe(log_id, device_path):
    with app.app_context():
        # 1. Get the log entry from the database
        log = WipeLog.query.get(log_id)
        if not log:
            print(f"Error: Log ID {log_id} not found.")
            return

        # 2. Update status to 'wiping'
        log.status = 'wiping'
        db.session.commit()
        print(f"Wiping started for {device_path}")

        try:
            # 3. THE CORE WIPE COMMAND: Overwrite with zeros
            # This command writes zeros from /dev/zero to your disk image file
            subprocess.run(
                ['dd', f'if=/dev/zero', f'of={device_path}', 'bs=1M', 'count=100'],
                check=True, # This will raise an exception if dd fails
                capture_output=True # Don't print dd's output to our console
            )

            # 4. If successful, update status to 'completed'
            log.status = 'completed'
            print(f"Wiping completed for {device_path}")
        except subprocess.CalledProcessError as e:
            # 5. If dd fails, update status to 'failed'
            log.status = 'failed'
            print(f"Wiping failed for {device_path}: {e.stderr.decode()}")
        
        log.end_time = datetime.utcnow()
        db.session.commit()

if __name__ == '__main__':
    log_id_from_api = sys.argv[1]
    device_path_from_api = sys.argv[2]
    perform_wipe(int(log_id_from_api), device_path_from_api)