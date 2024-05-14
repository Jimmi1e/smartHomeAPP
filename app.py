from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import psutil
import subprocess
import platform
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///settings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
"Admin Centre"
def get_temperature():
    temp = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True).stdout
    return temp.replace("temp=", "").strip()

def get_system_info():
    system_info = {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'platform_release': platform.release(),
        'platform_architecture': platform.machine(),
        'external_devices': [disk.device for disk in psutil.disk_partitions()]
    }
    return system_info
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notifications = db.Column(db.Boolean, default=True)
    smart_monitoring = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/get_settings', methods=['GET'])
def get_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings(notifications=True, smart_monitoring=False)
        db.session.add(settings)
        db.session.commit()
    return jsonify({
        'notifications': settings.notifications,
        'smart_monitoring': settings.smart_monitoring
    })

@app.route('/set_settings', methods=['POST'])
def set_settings():
    data = request.get_json()
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
    settings.notifications = data.get('notifications', True)
    settings.smart_monitoring = data.get('smart_monitoring', False)
    db.session.add(settings)
    db.session.commit()
    return jsonify({'status': 'success'})


"Admin Centre"
@app.route('/admin_centre')
def admin_centre():
    return render_template('admin_centre.html')


@app.route('/system_info')
def system_info():
    temperature = get_temperature()
    cpu_usage = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')
    system_info = get_system_info()

    data = {
        'temperature': temperature,
        'cpu_usage': cpu_usage,
        'memory_total': memory_info.total,
        'memory_used': memory_info.used,
        'memory_free': memory_info.free,
        'disk_total': disk_info.total,
        'disk_used': disk_info.used,
        'disk_free': disk_info.free,
        'system_version': system_info['platform_version'],
        'external_devices': system_info['external_devices']
    }
    return jsonify(data)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
