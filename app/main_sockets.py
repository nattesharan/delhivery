from flask_socketio import join_room,rooms,leave_room,emit
from flask import request
from flask_login import current_user
from delhivery.models import DelhiveryUser, DelhiveryChat, DelhiveryMessages
from app.utils import get_id_from_rooms, get_active_user_ids
from api.utils import get_all_online_delhivery_boys
def connect():
    join_room('main')
    print("Successfully connected")

def disconnect():
    user_rooms = rooms()
    for user_room in user_rooms:
        leave_room(user_room)
    user_id = get_id_from_rooms(user_rooms)
    user = DelhiveryUser.objects.get(id=user_id)
    user.become_offline()
    active_users = get_active_user_ids()
    online_friends = get_all_online_delhivery_boys(user)
    for friend in online_friends:
        emit('refresh_online_friends',room = str(friend.id))
    emit('disconnected_offline',{'users':active_users},room='main')
    

def create_room(data):
    user_id = data['user_id']
    user = DelhiveryUser.objects.get(id=user_id)
    user.become_online()
    if user_id not in rooms():
        join_room(data['user_id'])
    active_users = get_active_user_ids()
    online_friends = get_all_online_delhivery_boys(user)
    for friend in online_friends:
        emit('refresh_online_friends',room = str(friend.id))
    emit('connected_online',{'users':active_users},room='main')

def send_message(data):
    sender_rooms = rooms()
    sender_id = get_id_from_rooms(sender_rooms)
    receiver = DelhiveryUser.objects.get(id=data['sent_to'])
    sender = DelhiveryUser.objects.get(id=sender_id)
    if sender in receiver.friends and receiver in sender.friends:
        chat = DelhiveryChat.get_or_create_chat(sender,receiver)
        message = DelhiveryMessages.new_message(data['message'],sender,receiver)
        chat.messages.insert(0,message)
        chat.save()
        if receiver.is_online:
            emit('new_message',room=str(receiver.id))
        emit('refresh_sender',room=str(sender.id))
    else:
        emit('not_friends',room=str(sender.id))

def typing_message(data):
    typing_user_rooms = rooms()
    typing_user_id = get_id_from_rooms(typing_user_rooms)
    typing_user = DelhiveryUser.objects.get(id=typing_user_id)
    friend = DelhiveryUser.objects.get(id=data['friend'])
    if friend in typing_user.friends and typing_user in friend.friends and friend.is_online:
        emit('sender_is_typing',{'typing_user': str(typing_user_id)},room=str(friend.id))

def no_longer_typing(data):
    typing_user_rooms = rooms()
    typing_user_id = get_id_from_rooms(typing_user_rooms)
    typing_user = DelhiveryUser.objects.get(id=typing_user_id)
    friend = DelhiveryUser.objects.get(id=data['friend'])
    if friend in typing_user.friends and typing_user in friend.friends and friend.is_online:
        emit('sender_stopped_typing',{'typing_user': str(typing_user_id)},room=str(friend.id))