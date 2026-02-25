from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from models import db, Alert, Report
from forms import ReportForm
from app import socketio
import os
from werkzeug.utils import secure_filename
from datetime import datetime

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/')
@alerts_bp.route('/dashboard')
def dashboard():
    alerts = Alert.query.filter_by(status='active').order_by(Alert.timestamp.desc()).all()
    return render_template('dashboard.html', title='Dashboard', alerts=alerts)

@alerts_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            f = form.image.data
            filename = secure_filename(f"{datetime.now().timestamp()}_{f.filename}")
            f.save(os.path.join('static/uploads', filename))
        
        new_report = Report(
            author=current_user,
            incident_type=form.incident_type.data,
            location=form.location.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            severity=form.severity.data,
            description=form.description.data,
            image_path=filename
        )
        db.session.add(new_report)
        db.session.commit()
        flash('Your report has been submitted and is awaiting administrator approval.')
        return redirect(url_for('alerts.dashboard'))
    return render_template('report.html', title='Report Incident', form=form)

@alerts_bp.route('/api/alerts')
def get_alerts():
    alerts = Alert.query.filter_by(status='active').all()
    return jsonify([{
        'id': a.id,
        'type': a.type,
        'location': a.location,
        'latitude': a.latitude,
        'longitude': a.longitude,
        'severity': a.severity,
        'description': a.description,
        'timestamp': a.timestamp.isoformat()
    } for a in alerts])
