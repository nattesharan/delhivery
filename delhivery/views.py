from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required,current_user
from app.utils import feature_enable
from delhivery.models import DelhiveryUser, DelhiveryTask
delhivery_views = Blueprint('delhivery_views',__name__,template_folder='templates')

@delhivery_views.route('/home')
@login_required
def index():
    return render_template('home.html', user=current_user)

@delhivery_views.route('/notifications')
@login_required
def typography():
    return render_template('typography.html',user=current_user)

@delhivery_views.route('/view-tasks')
@login_required
def view_tasks():
    if current_user.role.role == 'STORE_MANAGER':
        return render_template('view_tasks.html', user=current_user)
    return redirect(url_for('index'))

@delhivery_views.route('/find-tasks')
@login_required
def find_tasks():
    if current_user.role.role == 'DELIVERY_BOY':
        return render_template('find_tasks.html', user=current_user)
    return redirect(url_for('index'))

@delhivery_views.route('/tasks/<task_id>')
@login_required
@feature_enable('features_see_state_transistions')
def view_timeline(task_id):
    task = DelhiveryTask.objects.get(id=task_id)
    return render_template('view_task.html', user=current_user, task=task)