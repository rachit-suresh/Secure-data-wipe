from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import subprocess
import os
from datetime import datetime

app = Flask(__name__)
# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wipelogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# The model for our audit log
class WipeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending') # pending -> wiping -> completed/failed
    start_time = db.Column(db.DateTime, server_default=db.func.now())
    end_time = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'device_name': self.device_name,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None
        }

# Endpoint to START a wipe operation
@app.route('/wipe', methods=['POST'])
def start_wipe():
    device_name = request.json.get('device_name') # e.g., "test_drive.img"
    if not os.path.exists(device_name):
        return jsonify({'error': 'Device not found'}), 404

    # Create a new log entry
    new_log = WipeLog(device_name=device_name, status='pending')
    db.session.add(new_log)
    db.session.commit()

    # Launch the wipe script in the background
    subprocess.Popen(['python3', 'wiper.py', str(new_log.id), device_name])

    return jsonify({'message': 'Wipe process started', 'log': new_log.to_dict()}), 202

# Endpoint to CHECK the status of a wipe
@app.route('/status/<int:log_id>', methods=['GET'])
def get_status(log_id):
    log = WipeLog.query.get(log_id)
    if not log:
        return jsonify({'error': 'Log ID not found'}), 404
    return jsonify({'log': log.to_dict()})

if __name__ == '__main__':
    # Create the database and tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)