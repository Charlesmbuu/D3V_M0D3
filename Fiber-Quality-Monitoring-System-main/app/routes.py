from flask import Blueprint, render_template
from flask_socketio import SocketIO
from .simulation import NetworkSimulator

main_bp = Blueprint('main', __name__)
socketio = SocketIO()
simulator = None

@main_bp.route('/')
def control_panel():
    return render_template('control.html')

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    global simulator
    if not simulator:
        simulator = NetworkSimulator(socketio)
        simulator.start()

@socketio.on('trigger_event')
def handle_event(event):
    simulator.trigger_event(event['type'])