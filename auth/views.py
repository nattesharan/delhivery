from flask import Blueprint,render_template,request,flash,redirect,url_for
from auth.forms import LoginForm,RegistrationForm
from flask_login import login_user,logout_user,login_required,current_user
from delhivery.models import DelhiveryUser, DelhiveryHierarchy
from mongoengine import DoesNotExist
from app import socketio
auth_views = Blueprint('auth_views',__name__,template_folder='templates')

@auth_views.route('/')
def delhivery_index():
    if current_user.is_authenticated:
        return redirect(url_for('delhivery_views.home'))
    return render_template("delhivery.html",loginform=LoginForm(), registrationform=RegistrationForm())

@auth_views.route('/login',methods=['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
        try:
            user = DelhiveryUser.objects.get(email=form.loginemail.data)
        except DoesNotExist:
            return render_template("delhivery.html", loginform=form,registrationform=RegistrationForm())
        if user and user.verify_password(form.loginpassword.data):
            login_user(user,remember=True)
            return redirect(url_for('delhivery_views.index'))
        form.loginemail.errors.append("Email or password invalid")
    return render_template("delhivery.html", loginform=form,registrationform=RegistrationForm())

@auth_views.route('/register',methods=['POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        if DelhiveryUser.find_user(form.email.data):
            form.email.errors.append("Email address already registered")
            return render_template('delhivery.html',loginform=LoginForm(), registrationform=form)
        else:
            user = DelhiveryUser(email=form.email.data)
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            role = DelhiveryHierarchy.objects.get(role=form.role.data)
            user.role = role
            user.set_password(form.password.data)
            user.save()
            flash('Successfully registered','success')
            return redirect(url_for('auth_views.delhivery_index'))
    return render_template("delhivery.html", loginform=LoginForm(),registrationform=form)

@auth_views.route('/logout')
@login_required
def logout():
    socketio.emit('disconnect')
    logout_user()
    return redirect(url_for('auth_views.delhivery_index'))