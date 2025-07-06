from flask import session, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from datetime import datetime, date, timedelta
import logging
from app import app, db
from replit_auth import require_login, make_replit_blueprint
from models import User, Task, TimeEntry, Message, LeaveRequest

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/dashboard')
@require_login
def dashboard():
    user = current_user
    today = date.today()
    
    # Get today's tasks (handle potential database issues gracefully)
    try:
        today_tasks = Task.query.filter_by(assigned_to=user.id).filter(
            Task.due_date == today
        ).order_by(Task.priority.desc()).all()
    except Exception as e:
        logging.error(f"Error fetching tasks: {e}")
        today_tasks = []
    
    # Get recent messages (handle potential database issues gracefully)
    try:
        recent_messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()
    except Exception as e:
        logging.error(f"Error fetching messages: {e}")
        recent_messages = []
    
    # Get current time status (handle potential database issues gracefully)
    try:
        latest_entry = TimeEntry.query.filter_by(user_id=user.id).order_by(
            TimeEntry.timestamp.desc()
        ).first()
    except Exception as e:
        logging.error(f"Error fetching time entries: {e}")
        latest_entry = None
    
    is_clocked_in = False
    is_on_break = False
    if latest_entry:
        if latest_entry.entry_type == 'clock_in':
            is_clocked_in = True
        elif latest_entry.entry_type == 'break_start':
            is_clocked_in = True
            is_on_break = True
    
    return render_template('dashboard.html', 
                         today_tasks=today_tasks,
                         recent_messages=recent_messages,
                         is_clocked_in=is_clocked_in,
                         is_on_break=is_on_break)

@app.route('/tasks')
@require_login
def tasks():
    status_filter = request.args.get('status', 'all')
    user = current_user
    
    query = Task.query.filter_by(assigned_to=user.id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    tasks = query.order_by(Task.due_date.asc()).all()
    
    return render_template('tasks.html', tasks=tasks, status_filter=status_filter)

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
@require_login
def complete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        
        if task.assigned_to != current_user.id:
            return jsonify({
                'success': False, 
                'message': 'Je bent niet bevoegd om deze taak te voltooien.'
            })
        
        task.status = 'completed'
        task.completed_at = datetime.now()
        db.session.commit()
        
        # Check if it's an AJAX request
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            return jsonify({
                'success': True,
                'message': f'Taak "{task.title}" is voltooid!'
            })
        else:
            flash('Taak gemarkeerd als voltooid!', 'success')
            return redirect(url_for('tasks'))
    except Exception as e:
        logging.error(f"Error completing task {task_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Er is een fout opgetreden bij het voltooien van de taak.'
        })

@app.route('/tasks/add', methods=['POST'])
@require_login
def add_task():
    try:
        title = request.form.get('title')
        description = request.form.get('description', '')
        priority = request.form.get('priority', 'medium')
        due_date = request.form.get('due_date')
        location = request.form.get('location', '')
        estimated_hours = request.form.get('estimated_hours')
        scheduled_start = request.form.get('scheduled_start')
        
        if not title:
            return jsonify({
                'success': False,
                'message': 'Taak titel is verplicht.'
            })
        
        # Create new task
        task = Task()
        task.title = title
        task.description = description
        task.priority = priority
        task.location = location
        task.assigned_to = current_user.id
        task.created_by = current_user.id
        task.status = 'pending'
        
        # Handle due date
        if due_date:
            try:
                task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # Handle estimated hours
        if estimated_hours:
            try:
                task.estimated_hours = float(estimated_hours)
            except ValueError:
                pass
        
        # Handle scheduled start
        if scheduled_start:
            try:
                task.scheduled_start = datetime.strptime(scheduled_start, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Taak "{title}" is succesvol toegevoegd!'
        })
        
    except Exception as e:
        logging.error(f"Error adding task: {e}")
        return jsonify({
            'success': False,
            'message': 'Er is een fout opgetreden bij het toevoegen van de taak.'
        })

@app.route('/tasks/<int:task_id>/start', methods=['POST'])
@require_login
def start_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        
        if task.assigned_to != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Je bent niet bevoegd om deze taak te starten.'
            })
        
        task.status = 'in_progress'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Taak "{task.title}" is gestart!'
        })
        
    except Exception as e:
        logging.error(f"Error starting task {task_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Er is een fout opgetreden bij het starten van de taak.'
        })

@app.route('/team')
@require_login
def team():
    team_members = User.query.filter_by(active=True).order_by(User.first_name).all()
    return render_template('team.html', team_members=team_members)

@app.route('/schedule')
@require_login
def schedule():
    view = request.args.get('view', 'week')
    user = current_user
    
    if view == 'week':
        # Get current week's tasks
        today = date.today()
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        
        tasks = Task.query.filter_by(assigned_to=user.id).filter(
            Task.due_date >= start_week,
            Task.due_date <= end_week
        ).order_by(Task.due_date).all()
    else:
        # Get today's tasks
        today = date.today()
        tasks = Task.query.filter_by(assigned_to=user.id).filter(
            Task.due_date == today
        ).order_by(Task.scheduled_start).all()
    
    return render_template('schedule.html', tasks=tasks, view=view)

@app.route('/messages')
@require_login
def messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template('messages.html', messages=messages)

@app.route('/time-tracking')
@require_login
def time_tracking():
    user = current_user
    today = date.today()
    
    # Get today's time entries
    today_entries = TimeEntry.query.filter_by(user_id=user.id).filter(
        db.func.date(TimeEntry.timestamp) == today
    ).order_by(TimeEntry.timestamp.desc()).all()
    
    # Get current status
    latest_entry = TimeEntry.query.filter_by(user_id=user.id).order_by(
        TimeEntry.timestamp.desc()
    ).first()
    
    current_status = 'clocked_out'
    if latest_entry:
        if latest_entry.entry_type == 'clock_in':
            current_status = 'clocked_in'
        elif latest_entry.entry_type == 'break_start':
            current_status = 'on_break'
    
    return render_template('time_tracking.html', 
                         today_entries=today_entries,
                         current_status=current_status)

@app.route('/time-tracking/clock-in', methods=['POST'])
@require_login
def clock_in():
    user = current_user
    location = request.form.get('location', '')
    notes = request.form.get('notes', '')
    
    entry = TimeEntry()
    entry.user_id = user.id
    entry.entry_type = 'clock_in'
    entry.location = location
    entry.notes = notes
    db.session.add(entry)
    db.session.commit()
    
    flash('Succesvol ingeklokt!', 'success')
    return redirect(url_for('time_tracking'))

@app.route('/time-tracking/clock-out', methods=['POST'])
@require_login
def clock_out():
    user = current_user
    notes = request.form.get('notes', '')
    
    entry = TimeEntry()
    entry.user_id = user.id
    entry.entry_type = 'clock_out'
    entry.notes = notes
    db.session.add(entry)
    db.session.commit()
    
    flash('Succesvol uitgeklokt!', 'success')
    return redirect(url_for('time_tracking'))

@app.route('/time-tracking/break-start', methods=['POST'])
@require_login
def break_start():
    user = current_user
    notes = request.form.get('notes', '')
    
    entry = TimeEntry()
    entry.user_id = user.id
    entry.entry_type = 'break_start'
    entry.notes = notes
    db.session.add(entry)
    db.session.commit()
    
    flash('Pauze gestart!', 'success')
    return redirect(url_for('time_tracking'))

@app.route('/time-tracking/break-end', methods=['POST'])
@require_login
def break_end():
    user = current_user
    notes = request.form.get('notes', '')
    
    entry = TimeEntry()
    entry.user_id = user.id
    entry.entry_type = 'break_end'
    entry.notes = notes
    db.session.add(entry)
    db.session.commit()
    
    flash('Pauze beëindigd!', 'success')
    return redirect(url_for('time_tracking'))

@app.route('/leave-request')
@require_login
def leave_request():
    user = current_user
    
    # Get user's leave requests
    leave_requests = LeaveRequest.query.filter_by(user_id=user.id).order_by(
        LeaveRequest.created_at.desc()
    ).all()
    
    return render_template('leave_request.html', leave_requests=leave_requests)

@app.route('/leave-request/submit', methods=['POST'])
@require_login
def submit_leave_request():
    user = current_user
    
    leave_type = request.form.get('leave_type')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    if not start_date_str or not end_date_str:
        flash('Start- en einddatum zijn verplicht.', 'error')
        return redirect(url_for('leave_request'))
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    reason = request.form.get('reason', '')
    
    if start_date > end_date:
        flash('Startdatum kan niet na einddatum zijn.', 'error')
        return redirect(url_for('leave_request'))
    
    leave_req = LeaveRequest()
    leave_req.user_id = user.id
    leave_req.leave_type = leave_type
    leave_req.start_date = start_date
    leave_req.end_date = end_date
    leave_req.reason = reason
    
    db.session.add(leave_req)
    db.session.commit()
    
    flash('Verlofaanvraag succesvol ingediend!', 'success')
    return redirect(url_for('leave_request'))
