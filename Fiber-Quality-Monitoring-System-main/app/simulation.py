import random
import time
import threading
from datetime import datetime
from flask_socketio import SocketIO

class NetworkSimulator:
    def __init__(self, socketio):
        self.running = False
        self.socketio = socketio
        self.nodes = {
            'Nairobi': {'status': 'online', 'power': -20, 'latency': 5},
            'Mombasa': {'status': 'online', 'power': -18, 'latency': 8},
            'Kisumu': {'status': 'online', 'power': -22, 'latency': 10}
        }
        self.event_handlers = []
        self.simulation_thread = None

    def start(self):
        """Start the simulation background thread"""
        self.running = True
        self.simulation_thread = threading.Thread(target=self.run_simulation)
        self.simulation_thread.start()

    def stop(self):
        """Stop the simulation"""
        self.running = False

    def run_simulation(self):
        """Main simulation loop"""
        while self.running:
            # Random network fluctuations
            for node in self.nodes.values():
                if node['status'] == 'online':
                    node['power'] += random.uniform(-0.5, 0.5)
                    node['latency'] += random.uniform(-0.2, 0.5)
            
            self.socketio.emit('network_update', self.nodes)
            time.sleep(1)

    def trigger_event(self, event_type):
        """Handle manual event triggers"""
        node = random.choice(list(self.nodes.keys()))
        
        if event_type == 'LOS':
            self.nodes[node]['status'] = 'offline'
            self.log_event(f"LOS detected at {node}")
            
        elif event_type == 'high_power':
            self.nodes[node]['power'] += random.uniform(3, 5)
            self.log_event(f"High power at {node} ({self.nodes[node]['power']:.1f}dBm)")
            
        elif event_type == 'fiber_cut':
            for n in self.nodes:
                if n != node:
                    self.nodes[n]['latency'] *= 5
            self.log_event(f"Fiber cut between {node} and hub")

        self.socketio.emit('event_update', {'type': event_type, 'node': node})

    def log_event(self, message):
        """Log simulation events"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.socketio.emit('log_update', f"[{timestamp}] {message}")