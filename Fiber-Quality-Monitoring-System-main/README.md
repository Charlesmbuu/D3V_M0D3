# FiberQMS - Fiber Network Quality Monitoring System ![MIT License](https://img.shields.io/badge/license-MIT-blue)

A comprehensive monitoring solution for fiber network ISPs and subscribers

## Features

- Real-time network visualization
- Automated speed testing
- Outage detection and alerts
- Interactive simulation controls
- Performance analytics dashboard
- SMS/Email notifications
- Multi-user support (Subscribers & ISP Admins)

## Installation

```bash
# Clone repository
git clone https://github.com/Charlesmbuu/Fiber-Quality-Monitoring-System.git
cd fiberqms

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
