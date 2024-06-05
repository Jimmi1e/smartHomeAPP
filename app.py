from flask import Flask, render_template, request, jsonify, Response,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import psutil
import subprocess
import platform
from picamera2 import Picamera2
import cv2
import time
import os
import torch
import datetime
app = Flask(__name__)
"settings"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///settings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#Notifications
detection_logs = []
image_save_dir = 'static/detections'
os.makedirs(image_save_dir, exist_ok=True)

@app.route('/get_logs', methods=['GET'])
def get_logs():
    return jsonify(detection_logs)

@app.route('/get_detection_images', methods=['GET'])
def get_detection_images():
    image_files = sorted(os.listdir(image_save_dir), reverse=True)
    return jsonify(image_files)
#Settings
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
        'smart_monitoring': settings.smart_monitoring
    })

@app.route('/set_settings', methods=['POST'])
def set_settings():
    data = request.get_json()
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
    settings.smart_monitoring = data.get('smart_monitoring', False)
    db.session.add(settings)
    db.session.commit()
    return jsonify({'status': 'success'})
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
    smart_monitoring = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

"monitor"
# def release_camera():
#     os.system('sudo fuser -k /dev/video0')
#     os.system('sudo fuser -k /dev/video1')

# def initialize_camera():
#     attempts = 3
#     for i in range(attempts):
#         try:
#             release_camera()
#             picam2 = Picamera2()
#             config = picam2.create_video_configuration(main={"size": (640, 480)})
#             picam2.configure(config)
#             picam2.start()
#             return picam2
#         except Exception as e:
#             print(f"Attempt {i+1} to initialize camera failed: {e}")
#             time.sleep(2)
#     raise RuntimeError("Failed to initialize camera after multiple attempts")

# picam2 = initialize_camera()

# def gen_frames():
#     while True:
#         frame = picam2.capture_array()
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/monitor')
# def monitor():
#     return render_template('monitor.html')
#///////////////////////////
# Camera and YOLOv5 setup
# def release_camera():
#     os.system('sudo fuser -k /dev/video0')
#     os.system('sudo fuser -k /dev/video1')

# def initialize_camera():
#     attempts = 3
#     for i in range(attempts):
#         try:
#             release_camera()
#             picam2 = Picamera2()
#             config = picam2.create_video_configuration(main={"size": (640, 480)})
#             picam2.configure(config)
#             picam2.start()
#             return picam2
#         except Exception as e:
#             print(f"Attempt {i+1} to initialize camera failed: {e}")
#             time.sleep(2)
#     raise RuntimeError("Failed to initialize camera after multiple attempts")

# picam2 = initialize_camera()

# # Load YOLOv5 model
# model_path = 'static/best.pt'  # ??????
# model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
# model.conf = 0.5  # confidence threshold

# # Global variable to store intrusion status
# intrusion_detected = False

# def detect_pedestrians(frame):
#     global intrusion_detected
#     results = model(frame)
#     boxes = results.xyxy[0].cpu().numpy()
    
#     num_people = 0
#     for box in boxes:
#         x1, y1, x2, y2, conf, cls = box
#         if int(cls) in [0, 1, 2, 3 ,4]:  # class_id == 0 ? person, class_id == 1 ? person&bike
#             num_people += 1
#             color = (0, 255, 0) if int(cls) == 0 else (0, 0, 255)
#             cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
    
#     intrusion_detected = num_people > 0
#     return frame, num_people

# def gen_frames():
#     while True:
#         frame = picam2.capture_array()
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         frame, num_people = detect_pedestrians(frame)
#         now = datetime.datetime.now()
#         current_time = now.strftime("%H:%M:%S")
#         cv2.putText(frame, f'Time: {current_time}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#         cv2.putText(frame, f'People: {num_people}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#         ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/monitor')
# def monitor():
#     return render_template('monitor.html')

# @app.route('/check_intrusion')
# def check_intrusion():
#     return jsonify({'intrusion': intrusion_detected})
# Camera and YOLOv5 setup
def release_camera():
    os.system('sudo fuser -k /dev/video0')
    os.system('sudo fuser -k /dev/video1')

def initialize_camera():
    attempts = 3
    for i in range(attempts):
        try:
            release_camera()
            picam2 = Picamera2()
            config = picam2.create_video_configuration(main={"size": (640, 480)})
            picam2.configure(config)
            picam2.start()
            return picam2
        except Exception as e:
            print(f"Attempt {i+1} to initialize camera failed: {e}")
            time.sleep(2)
    raise RuntimeError("Failed to initialize camera after multiple attempts")

picam2 = initialize_camera()

# Load YOLOv5 model
model_path = 'static/best.pt'
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
model.conf = 0.5  # confidence threshold

# Global variable to store intrusion status
intrusion_detected = False
last_log_time = time.time()

def detect_pedestrians(frame):
    global intrusion_detected, last_log_time
    results = model(frame)
    boxes = results.xyxy[0].cpu().numpy()
    
    num_people = 0
    for box in boxes:
        x1, y1, x2, y2, conf, cls = box
        if int(cls) in [0, 1, 2, 3, 4]:  # class_id == 0 ? person, class_id == 1 ? person&bike
            num_people += 1
            color = (0, 255, 0) if int(cls) == 0 else (0, 0, 255)
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
    
    current_time = time.time()
    if num_people > 0:
        intrusion_detected = True
        if current_time - last_log_time > 30:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            detection_logs.append(f'Detection at {timestamp}')
            image_path = os.path.join(image_save_dir, f'Human_{timestamp}.jpg')
            cv2.putText(frame, f'Time: {timestamp}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, 'Human Detected', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imwrite(image_path, frame)
            last_log_time = current_time
    else:
        intrusion_detected = False

    return frame, num_people

def gen_frames():
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame, num_people = detect_pedestrians(frame)
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        cv2.putText(frame, f'Time: {current_time}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f'People: {num_people}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/check_intrusion')
def check_intrusion():
    return jsonify({'intrusion': intrusion_detected})

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
