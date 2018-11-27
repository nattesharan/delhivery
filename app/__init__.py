from flask import Flask,session,redirect,render_template
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from fakebook.models import FakeBookUser
from api.utils import get_notifications_for_dashboard
from settings import MONGODB_SETTINGS
import main_sockets
app = Flask(__name__)
app.secret_key = 'FAKEBOOKSECRET'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MONGODB_SETTINGS'] = MONGODB_SETTINGS
app.config['WTF_CSRF_SECRET_KEY']="SECRETCSRFKEY"
CORS(app)
socketio = SocketIO(manage_session=False)
socketio.init_app(app,message_queue='redis://')
login_manager = LoginManager(app)
db = MongoEngine(app)
socketio.on_event('connect',main_sockets.connect)
socketio.on_event('create_room',main_sockets.create_room)
socketio.on_event('disconnect',main_sockets.disconnect)
socketio.on_event('send_message',main_sockets.send_message)
socketio.on_event('typing',main_sockets.typing_message)
socketio.on_event('no_longer_typing',main_sockets.no_longer_typing)
def notify_user(person_id):
    notifications = get_notifications_for_dashboard(person_id)
    socketio.emit('received_friend_request',notifications,room=person_id)

def update_friends_list_for_receiver(user_id):
    socketio.emit('update_people_list',room=user_id)

def refresh_online_friends(user_id):
    socketio.emit('refresh_online_friends',room = user_id)

@login_manager.user_loader
def loaduser(user_id):
    user = FakeBookUser.objects.get(id=user_id)
    return user
@login_manager.unauthorized_handler
def unauthorized():
    session.clear()
    return redirect("/")
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
def load_blueprints():
    from auth.views import auth_views
    app.register_blueprint(auth_views)
    from fakebook.views import fakebook_views
    app.register_blueprint(fakebook_views)
    from api.api import api_blueprint
    app.register_blueprint(api_blueprint)
load_blueprints()