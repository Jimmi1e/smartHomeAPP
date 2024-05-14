from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///settings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
