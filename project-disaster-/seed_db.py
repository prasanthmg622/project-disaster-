from app import create_app, db
from models import User, Alert, Report
from datetime import datetime

app = create_app()

def seed_data():
    with app.app_context():
        # Create database
        db.create_all()
        
        # Check if users exist
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            user = User(username='demo_user', email='user@example.com', role='user')
            user.set_password('user123')
            db.session.add(user)
            
            # Add some sample alerts
            alerts = [
                Alert(type='earthquake', source='USGS', location='Caspian Sea', latitude=40.0, longitude=50.0, severity='medium', description='Magnitude 4.5 earthquake detected.'),
                Alert(type='flood', source='OpenWeather', location='Miami, FL', latitude=25.7617, longitude=-80.1918, severity='high', description='Severe coastal flooding expected.'),
                Alert(type='fire', source='UserReport', location='Central Park, NY', latitude=40.7851, longitude=-73.9683, severity='critical', description='Brush fire spreading rapidly.')
            ]
            for a in alerts:
                db.session.add(a)
            
            db.session.commit()
            print("Database seeded successfully!")
        else:
            print("Database already seeded.")

if __name__ == '__main__':
    seed_data()
