from flask import Blueprint
from flask_restful import Api
from api.resources import FriendRequestHandler,DashboardNotificationsHandler,UserNotificationsHandler,\
                        FriendsHandler,OnlineFriendsHandler,MessagesHandler, TasksResource
api_blueprint = Blueprint('api',__name__)
api = Api(api_blueprint)

api.add_resource(FriendRequestHandler,'/api/friend-request')
api.add_resource(DashboardNotificationsHandler,'/api/notifications')
api.add_resource(UserNotificationsHandler,'/api/user/notifications')
api.add_resource(FriendsHandler,'/api/friends')
api.add_resource(OnlineFriendsHandler,'/api/online-users')
api.add_resource(MessagesHandler,'/api/messages')
api.add_resource(TasksResource, '/api/tasks')