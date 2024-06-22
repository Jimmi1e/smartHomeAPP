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
import Adafruit_BMP.BMP085 as BMP085
import logging
import requests
from twilio.rest import Client
import spidev
import sys
from gpiozero import DigitalOutputDevice, InputDevice
import numpy as np
app = Flask(__name__)
#twillio
last_message_time = None
#account_sid = 'SID'
#auth_token = 'TOKEN'
twilio_client = Client(account_sid, auth_token)

"settings"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///settings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Settings(db.Model):
    __tablename__ = 'settings'
    __table_args__ = {'extend_existing': True}  # Add this line
    id = db.Column(db.Integer, primary_key=True)
    notifications = db.Column(db.Boolean, default=True)
    smart_monitoring = db.Column(db.Boolean, default=False)

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
#shanchude
# class Settings(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     smart_monitoring = db.Column(db.Boolean, default=False)

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


#envionment and weather

logging.basicConfig(level=logging.DEBUG)

# Initialize BMP180 sensor
try:
    logging.debug("Initializing BMP180 sensor on I2C bus 1")
    sensor = BMP085.BMP085(busnum=1)
    logging.debug("BMP180 sensor initialized successfully")
except Exception as e:
    logging.error("Error initializing BMP180 sensor: %s", e)
    sensor = None

# Your WeatherAPI key
#API_KEY = '0862402e107d4d40ac152143240506'

def get_weather_data():
    try:
        base_url = "http://api.weatherapi.com/v1"
        location = "Montreal"
        current_url = f"{base_url}/current.json?key={API_KEY}&q={location}"
        forecast_url = f"{base_url}/forecast.json?key={API_KEY}&q={location}&days=3"

        current_response = requests.get(current_url).json()
        forecast_response = requests.get(forecast_url).json()

        today_temp = current_response['current']['temp_c']
        today_uv = current_response['current']['uv']
        today_wind = current_response['current']['wind_kph']

        tomorrow_temp = forecast_response['forecast']['forecastday'][1]['day']['avgtemp_c']
        tomorrow_uv = forecast_response['forecast']['forecastday'][1]['day']['uv']
        tomorrow_wind = forecast_response['forecast']['forecastday'][1]['day']['maxwind_kph']

        day_after_tomorrow_temp = forecast_response['forecast']['forecastday'][2]['day']['avgtemp_c']
        day_after_tomorrow_uv = forecast_response['forecast']['forecastday'][2]['day']['uv']
        day_after_tomorrow_wind = forecast_response['forecast']['forecastday'][2]['day']['maxwind_kph']

        return {
            'today_temp': today_temp,
            'today_uv': today_uv,
            'today_wind': today_wind,
            'tomorrow_temp': tomorrow_temp,
            'tomorrow_uv': tomorrow_uv,
            'tomorrow_wind': tomorrow_wind,
            'day_after_tomorrow_temp': day_after_tomorrow_temp,
            'day_after_tomorrow_uv': day_after_tomorrow_uv,
            'day_after_tomorrow_wind': day_after_tomorrow_wind
        }
    except Exception as e:
        logging.error("Error fetching weather data: %s", e)
        return None
@app.route('/environment')
def environment():
    if sensor is None:
        return "Sensor not initialized", 500
    try:
        temperature = sensor.read_temperature()
        pressure = sensor.read_pressure() / 100.0  # Convert Pa to hPa
        logging.debug("Temperature: %s, Pressure: %s", temperature, pressure)

        weather_data = get_weather_data()
        if weather_data is None:
            return "Error fetching weather data", 500

        return render_template('environment.html', 
                               temperature=temperature, 
                               pressure=pressure,
                               today_temp=weather_data['today_temp'],
                               today_uv=weather_data['today_uv'],
                               today_wind=weather_data['today_wind'],
                               tomorrow_temp=weather_data['tomorrow_temp'],
                               tomorrow_uv=weather_data['tomorrow_uv'],
                               tomorrow_wind=weather_data['tomorrow_wind'],
                               day_after_tomorrow_temp=weather_data['day_after_tomorrow_temp'],
                               day_after_tomorrow_uv=weather_data['day_after_tomorrow_uv'],
                               day_after_tomorrow_wind=weather_data['day_after_tomorrow_wind'])
    except Exception as e:
        logging.error("Error reading sensor data: %s", e)
        return "Error reading sensor data", 500

@app.route('/environment_data')
def environment_data():
    if sensor is None:
        return jsonify({"error": "Sensor not initialized"}), 500
    try:
        temperature = sensor.read_temperature()
        pressure = sensor.read_pressure() / 100.0  # Convert Pa to hPa
        return jsonify({"temperature": temperature, "pressure": pressure})
    except Exception as e:
        logging.error("Error reading sensor data: %s", e)
        return jsonify({"error": "Error reading sensor data"}), 500
    
#Message

def send_sms(body):
    global last_message_time
    current_time = datetime.datetime.now()
    if last_message_time is None or (current_time - last_message_time).total_seconds() > 15:
        print("Successfully calling send_sms function!!!")
        try:
            logging.debug("Attempting to send SMS: %s", body)
            message = twilio_client.messages.create(
                from_='+12184007463',
                to='+15149694866',
                body=body
            )
            logging.debug("Sent message SID: %s", message.sid)
            last_message_time = current_time
        except Exception as e:
            logging.error("Error sending SMS: %s", e)

#alert
# Initialize SPI for MCP3008
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

# GPIO setup for buzzers using gpiozero
BUZZER_A_PIN = 26
BUZZER_B_PIN = 20
buzzer_a = DigitalOutputDevice(BUZZER_A_PIN, active_high=False, initial_value=True)  # Ensure buzzer A is off initially
buzzer_b = DigitalOutputDevice(BUZZER_B_PIN, active_high=False, initial_value=True)  # Ensure buzzer B is off initially
buzzer_a.off()
buzzer_b.off()
# Setup flame sensor
FLAME_SENSOR_PIN = 16
flame_sensor = InputDevice(FLAME_SENSOR_PIN, pull_up=True)  # Assuming active_low for low-level trigger

# Ensure the flame sensor stabilizes at startup
time.sleep(2)

# Record the last time buzzer B was triggered due to temperature
last_temperature_buzz_time = None
# Record the last time buzzer B was turned off manually
last_buzzer_off_time = None

# Read ADC data from MCP3008
def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Convert ADC value to voltage
def adc_to_voltage(adc_value):
    return adc_value * (3.3 / 1023)

# Voltage to distance conversion table
voltage_distance_table = {
    0.4: 150,  # 0.4V -> 150cm
    0.5: 120,  # 0.5V -> 120cm
    0.6: 90,   # 0.6V -> 90cm
    0.8: 70,   # 0.8V -> 70cm
    1.0: 50,   # 1.0V -> 50cm
    1.3: 30,   # 1.3V -> 30cm
    1.8: 20,   # 1.8V -> 20cm
    2.5: 10    # 2.5V -> 10cm
}
def voltage_to_distance(voltage):
    voltages = np.array(list(voltage_distance_table.keys()))
    distances = np.array(list(voltage_distance_table.values()))

    if voltage <= voltages.min():
        return distances.max()  # Maximum distance
    elif voltage >= voltages.max():
        return distances.min()  # Minimum distance
    else:
        distance = np.interp(voltage, voltages, distances)
        return distance

# def control_buzzer_a(distance):
#     logging.debug("Controlling buzzer A with distance: %s", distance)
#     if distance <= 30:
#         logging.debug("Distance <= 30 cm, turning buzzer A on")
#         buzzer_a.on()  # Turn on buzzer A
#         time.sleep(5)  # Buzzer A on for 5 seconds
#         buzzer_a.off()  # Turn off buzzer A
#         logging.debug("Buzzer A off after 5 seconds")
#     else:
#         logging.debug("Distance > 30 cm, ensuring buzzer A is off")
#         buzzer_a.off()  # Ensure buzzer A is off
#new
# def control_buzzer_a(distance):
#     logging.debug("Controlling buzzer A with distance: %s", distance)

#     settings = Settings.query.first()
#     if not settings.smart_monitoring: 
#         logging.debug("Sentry Mode is disabled, Buzzer A will not work")
#         buzzer_a.off()
#         return
    
#     if distance <= 30:
#         logging.debug("Distance <= 30 cm, turning buzzer A on")
#         buzzer_a.on()  # Turn on buzzer A
#         time.sleep(5)  # Buzzer A on for 5 seconds
#         buzzer_a.off()  # Turn off buzzer A
#         logging.debug("Buzzer A off after 5 seconds")
#         send_sms("Alert! There is a stranger approaching. Please check the surveillance.")
#     else:
#         logging.debug("Distance > 30 cm, ensuring buzzer A is off")
#         buzzer_a.off()  # Ensure buzzer A is off
def control_buzzer_a(distance):
    
    settings = Settings.query.first()
    if not settings.smart_monitoring: 
        # logging.debug("Sentry Mode is disabled, Buzzer A will not work")
        buzzer_a.off()
        return
    if distance <= 30:
        send_sms("Alert! There is a stranger approaching. Please check the surveillance.")
        # logging.debug("Distance <= 30 cm, turning buzzer A on")
        buzzer_a.on()  # Turn on buzzer A
        time.sleep(5)  # Buzzer A on for 5 seconds
        buzzer_a.off()  # Turn off buzzer A
        
        # logging.debug("Buzzer A off after 5 seconds")
        
    else:
        # logging.debug("Distance > 30 cm, ensuring buzzer A is off")
        buzzer_a.off()  # Ensure buzzer A is off

# def control_buzzer_b(temperature, fire_detected):
#     global last_temperature_buzz_time, last_buzzer_off_time
#     logging.debug("Controlling buzzer B with temperature: %s and fire_detected: %s", temperature, fire_detected)

#     current_time = datetime.datetime.now()

#     if fire_detected:
#         if last_buzzer_off_time is None or current_time - last_buzzer_off_time > datetime.timedelta(seconds=40):
#             logging.debug("Fire detected, turning buzzer B on continuously")
#             buzzer_b.on()
#             send_sms("Alert: Fire detected. Please check your house appliances and call 911 immediately.")
#         else:
#             logging.debug("Fire detected but buzzer B was manually turned off within the last 4 hours")
#             buzzer_b.off()
#     elif temperature >= 28 and not fire_detected:
#         if last_temperature_buzz_time is None or current_time - last_temperature_buzz_time > datetime.timedelta(seconds=40):
#             logging.debug("Temperature >= 28�C, turning buzzer B on and off 3 times")
#             last_temperature_buzz_time = current_time
#             for _ in range(3):
#                 buzzer_b.on()
#                 time.sleep(1)
#                 buzzer_b.off()
#                 time.sleep(1)
#             send_sms("Alert: Ambient temperature anomaly detected, potential fire hazard.")
#         else:
#             logging.debug("Temperature >= 28�C, but buzzer B has already been triggered within the last 4 hours")
#     else:
#         logging.debug("No fire and temperature < 28�C, ensuring buzzer B is off")
#         buzzer_b.off()

def control_buzzer_b(temperature, fire_detected):
    global last_temperature_buzz_time, last_buzzer_off_time
    # logging.debug("Controlling buzzer B with temperature: %s and fire_detected: %s", temperature, fire_detected)

    current_time = datetime.datetime.now()

    if fire_detected:
        if last_buzzer_off_time is None or current_time - last_buzzer_off_time > datetime.timedelta(seconds=40):
            #logging.debug("Fire detected, turning buzzer B on continuously")
            buzzer_b.on()
            send_sms("Alert: Fire detected. Please check your house appliances and call 911 immediately.")
        else:
            #logging.debug("Fire detected but buzzer B was manually turned off within the last 4 hours")
            buzzer_b.off()
    elif temperature >= 27 and not fire_detected:
        if last_temperature_buzz_time is None or current_time - last_temperature_buzz_time > datetime.timedelta(seconds=40):
            #logging.debug("Temperature >= 28�C, turning buzzer B on and off 3 times")
            last_temperature_buzz_time = current_time
            send_sms("Alert: Ambient temperature anomaly detected, potential fire hazard.") 
            for _ in range(3):
                buzzer_b.on()
                time.sleep(1)
                buzzer_b.off()
                time.sleep(1)
            
        #else:
            #logging.debug("Temperature >= 28�C, but buzzer B has already been triggered within the last 4 hours")
    else:
        #logging.debug("No fire and temperature < 28�C, ensuring buzzer B is off")
        buzzer_b.off()

# @app.route('/')
# def home():
#     return render_template('index.html')

@app.route('/securitysystem', methods=['GET', 'POST'])
def securitysystem():
    global last_buzzer_off_time
    if sensor is None:
        return "Sensor not initialized", 500
    try:
        adc_value = read_adc(0)  # Read channel 0
        voltage = adc_to_voltage(adc_value)
        distance = voltage_to_distance(voltage)
        temperature = sensor.read_temperature()
        fire_detected = flame_sensor.is_active  # Corrected logic: active means fire detected

        #logging.debug("Fire sensor state (is_active): %s", flame_sensor.is_active)
        #logging.debug("Fire detected (corrected): %s", fire_detected)

        # Control buzzers based on sensor data
        control_buzzer_a(distance)
        control_buzzer_b(temperature, fire_detected)

        if request.method == 'POST':
            if 'turn_off_buzzer' in request.form:
                buzzer_b.off()
                last_buzzer_off_time = datetime.datetime.now()

        alert_message = f"The surroundings are normal: Temperature {temperature:.2f} �C"
        if temperature >= 27 and not fire_detected:
            alert_message = f"Level 1 Alert: The temperature exceeds {temperature:.2f} �C"
        elif fire_detected:
            alert_message = f"Alert 2: There is a fire: Temperature {temperature:.2f} �C"

        return render_template('securitysystem.html', distance=distance, alert_message=alert_message, fire_detected=fire_detected)
    except Exception as e:
        #logging.error("Error reading sensor data: %s", e)
        return "Error reading sensor data", 500

@app.route('/securitysystem/data')
def securitysystem_data():
    global last_buzzer_off_time
    if sensor is None:
        return jsonify({"error": "Sensor not initialized"}), 500
    try:
        adc_value = read_adc(0)  # Read channel 0
        voltage = adc_to_voltage(adc_value)
        distance = voltage_to_distance(voltage)
        temperature = sensor.read_temperature()
        fire_detected = flame_sensor.is_active  # Corrected logic: active means fire detected

        #logging.debug("Fire sensor state (is_active): %s", flame_sensor.is_active)
        #logging.debug("Fire detected (corrected): %s", fire_detected)

        # Ensure buzzers are controlled here as well
        control_buzzer_a(distance)
        control_buzzer_b(temperature, fire_detected)

        alert_message = f"The surroundings are normal: Temperature {temperature:.1f} °C"
        if temperature >= 27 and not fire_detected:
            alert_message = f"Level 1 Alert: The temperature exceeds {temperature:.1f} °C"
        elif fire_detected:
            alert_message = f"Alert 2: There is a fire: Temperature {temperature:.1f} °C"

        data = {
            "distance": f"{distance:.1f}",
            "alert_message": alert_message,
            "fire_detected": fire_detected
        }
        return jsonify(data)
    except Exception as e:
        #logging.error("Error reading sensor data in /securitysystem/data route: %s", e)
        return jsonify({"error": "Error reading sensor data"}), 500
if __name__ == '__main__':
    try:
        # Ensure buzzers are off at startup
        buzzer_a.off()
        buzzer_b.off()
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        spi.close()
        buzzer_a.off()  # Ensure buzzer A is turned off when the program exits
        buzzer_b.off()  # Ensure buzzer B is turned off when the program exits
