from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Report, Alert
from app import socketio

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/pending_reports')
@login_required
def pending_reports():
    if not current_user.is_admin():
        flash('Access denied.')
        return redirect(url_for('alerts.dashboard'))
    reports = Report.query.filter_by(is_approved=False).order_by(Report.timestamp.desc()).all()
    return render_template('admin/pending_reports.html', reports=reports)

@admin_bp.route('/approve_report/<int:id>')
@login_required
def approve_report(id):
    if not current_user.is_admin():
        flash('Access denied.')
        return redirect(url_for('alerts.dashboard'))
    report = Report.query.get_or_404(id)
    report.is_approved = True
    
    # Create an alert from the approved report
    alert = Alert(
        type=report.incident_type,
        source='UserReport',
        location=report.location,
        latitude=report.latitude,
        longitude=report.longitude,
        severity=report.severity,
        description=report.description
    )
    db.session.add(alert)
    db.session.commit()
    
    # Notify all clients via SocketIO
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
    
    flash('Report approved and alert broadcasted!')
    return redirect(url_for('admin.pending_reports'))

@admin_bp.route('/reject_report/<int:id>')
@login_required
def reject_report(id):
    if not current_user.is_admin():
        flash('Access denied.')
        return redirect(url_for('alerts.dashboard'))
    report = Report.query.get_or_404(id)
    db.session.delete(report)
    db.session.commit()
    flash('Report rejected.')
    return redirect(url_for('admin.pending_reports'))
