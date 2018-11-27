from app import app,socketio
from flask_script import Manager,Server
manager = Manager(app)
manager.add_command("runserver", Server(
    use_debugger=True,
    use_reloader=True,
    host="0.0.0.0", port=9000))
manager.add_command("dev", socketio.run(app,debug=True,host="0.0.0.0",port=8080))
if __name__ == '__main__':
    manager.run()