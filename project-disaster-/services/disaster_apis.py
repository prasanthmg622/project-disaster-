import requests
from datetime import datetime
from models import db, Alert
from app import socketio

def fetch_usgs_earthquakes():
    """Fetch recent earthquakes from USGS API."""
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=" + datetime.utcnow().strftime('%Y-%m-%d')
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        new_alerts = []
        for feature in data['features'][:10]: # Process top 10 recent
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            
            # Use place as unique identifier to avoid duplicates for now (simple approach)
            existing = Alert.query.filter_by(location=props['place'], type='earthquake').first()
            if not existing:
                alert = Alert(
                    type='earthquake',
                    source='USGS',
                    location=props['place'],
                    latitude=coords[1],
                    longitude=coords[0],
                    severity='high' if props['mag'] >= 5.0 else 'medium' if props['mag'] >= 3.0 else 'low',
                    description=f"Magnitude: {props['mag']} | Depth: {coords[2]}km | Time: {datetime.fromtimestamp(props['time']/1000)}"
                )
                db.session.add(alert)
                new_alerts.append(alert)
        
        if new_alerts:
            db.session.commit()
            for alert in new_alerts:
                socketio.emit('new_alert', {
                    'id': alert.id,
                    'type': alert.type,
                    'location': alert.location,
                    'latitude': alert.latitude,
                    'longitude': alert.longitude,
                    'severity': alert.severity,
                    'description': alert.description,
                    'timestamp': alert.timestamp.isoformat()
                })
        return len(new_alerts)
    except Exception as e:
        print(f"Error fetching USGS data: {e}")
        return 0

def fetch_weather_alerts(app_key):
    """Fetch weather alerts from OpenWeatherMap (simplified example)."""
    # OpenWeather typically needs coordinates. We'll simulate a global check or 
    # specific regions. For this project, we'll focus on USGS as primary automated source.
    # OpenWeather alerts API requires a paid plan or One Call API.
    # We will implement a placeholder for weather or use generic weather data.
    pass
