from bson import ObjectId
from flask import jsonify
from delhivery.models import DelhiveryUser
from functools import wraps
from app.settings import FEATURES
from flask_login import current_user

def get_id_from_rooms(rooms):
    for room in rooms:
        try:
            return ObjectId(room)
        except:
            pass

def get_active_user_ids():
    active_users = DelhiveryUser.objects.filter(is_online=True).only('id')
    return [str(active_user.id) for active_user in active_users]


def feature_enable(feature):
    def decorator(view_function):
        @wraps(view_function)
        def decorated(*args, **kwargs):
            enabled = FEATURES[feature]["enabled"]
            allowed = current_user.is_allowed(feature)
            if enabled and allowed:
                return view_function(*args, **kwargs)
            return jsonify({
                'success': False,
                'message': 'You dont have permission to do this'
            })
        return decorated
    return decorator