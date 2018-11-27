from flask_restful import Resource
from flask import request,jsonify
import requests
from flask_login import login_required,current_user
from app.settings import NOTIFICATION_TYPES
from delhivery.models import DelhiveryUser,DelhiveryNotification,DelhiveryChat, DelhiveryMessages
from api.utils import create_notification, get_notifications_for_dashboard, get_all_notifications,\
                        get_all_people,get_all_online_delivery_boys_json
from app import notify_user,update_friends_list_for_receiver,refresh_online_friends
class FriendRequestHandler(Resource):
    @login_required
    def post(self):
        data = request.get_json()
        user = DelhiveryUser.objects.get(id=data['person_id'])
        sending_user = DelhiveryUser.objects.get(id=current_user.id)
        if sending_user not in user.received_friend_requests and sending_user not in user.sent_friend_requests \
            and user not in sending_user.received_friend_requests and user not in sending_user.sent_friend_requests:
            user.received_friend_requests.append(current_user.id)
            sending_user.sent_friend_requests.append(user.id)
            user.save()
            sending_user.save()
            notification = create_notification(NOTIFICATION_TYPES['FRIENDLY'],user)
            notify_user(str(user.id))
            update_friends_list_for_receiver(str(user.id))
            return jsonify({
                'success': True,
                'friends': get_all_people(),
                'message': 'Friend Request Sent to {}'.format(user.name)
            })
        elif current_user in user.friends:
            return jsonify({
                'success': False,
                'message': 'Already Friends'
            })
        else:
            return jsonify({
                'status': False,
                'message': 'Request to connect already in progress'
            })
    
    @login_required
    def delete(self):
        person_id = request.args.get('person_id')
        user = DelhiveryUser.objects.get(id=person_id)
        sending_user = DelhiveryUser.objects.get(id=current_user.id)
        if sending_user in user.received_friend_requests:
            user.received_friend_requests.remove(sending_user)
            sending_user.sent_friend_requests.remove(user)
            user.save()
            sending_user.save()
            notification = create_notification(NOTIFICATION_TYPES['CANCEL_REQUEST'],user)
            notify_user(str(user.id))
            update_friends_list_for_receiver(str(user.id))
            return jsonify({
                'success': True,
                'friends': get_all_people(),
                'message': 'Friend Request Successfully Cancelled'
            })
        elif sending_user in user.friends:
            return jsonify({
                'success': False,
                'message': 'Cannot Cancel as the request is accepted'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Please send friend request'
            })
    @login_required
    def put(self):
        data = request.get_json()
        accepting_user = DelhiveryUser.objects.get(id=current_user.id)
        sending_user = DelhiveryUser.objects.get(id=data['person_id'])
        if accepting_user in sending_user.sent_friend_requests:
            try:
                accepting_user.received_friend_requests.remove(sending_user)
                accepting_user.friends.append(sending_user)
                sending_user.sent_friend_requests.remove(accepting_user)
                sending_user.friends.append(accepting_user)
                accepting_user.save()
                sending_user.save()
                notification = create_notification(NOTIFICATION_TYPES['ACCEPT_REQUEST'],sending_user)
                notify_user(str(sending_user.id))
                update_friends_list_for_receiver(str(sending_user.id))
                return jsonify({
                    'success': True,
                    'message': 'You are now friends with {}'.format(sending_user.name)
                })
            except Exception as E:
                print(E)
            finally:
                if sending_user.is_online:
                    refresh_online_friends(str(sending_user.id))
                    refresh_online_friends(str(accepting_user.id))
        elif sending_user in accepting_user.friends:
            return jsonify({
                'success': False,
                'message': 'Already Friends'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Please send friend request'
            })
class DashboardNotificationsHandler(Resource):
    @login_required
    def get(self):
        notifications = get_notifications_for_dashboard(current_user.id)
        return jsonify({
            'notifications': notifications
        })
    @login_required
    def put(self):
        notifications = request.get_json()['read_notifications']
        read_notifications = []
        for notification in notifications:
            notif = DelhiveryNotification.objects.get(id=notification['id'])
            read_notifications.append(notif.mark_as_read())
        return jsonify({
            'notifications': read_notifications
        })

class UserNotificationsHandler(Resource):
    @login_required
    def get(self):
        limit = request.args.get('limit')
        skip = request.args.get('skip')
        notifications = get_all_notifications(int(skip),int(limit))
        return jsonify({
            'notifications': notifications
        })

class FriendsHandler(Resource):
    @login_required
    def get(self):
        people = get_all_people()
        return jsonify({
            'friends': people
        })
    @login_required
    def put(self):
        data = request.get_json()
        user = DelhiveryUser.objects.get(id=current_user.id)
        friend = DelhiveryUser.objects.get(id=data['person_id'])
        if user in friend.friends:
            try:
                user.friends.remove(friend)
                friend.friends.remove(user)
                user.save()
                friend.save()
                update_friends_list_for_receiver(str(friend.id))
                return jsonify({
                    'success': True,
                    'friends': get_all_people(),
                    'message': 'Successfully unfriended'
                })
            except Exception as E:
                print(E)
            finally:
                if friend.is_online:
                    refresh_online_friends(str(friend.id))
                    refresh_online_friends(str(user.id))
        else:
            return jsonify({
                'success': False,
                'message': 'Not friends Yet'
            })

class OnlineFriendsHandler(Resource):
    @login_required
    def get(self):
        online_delhivery_boys = get_all_online_delivery_boys_json()
        return jsonify({
            'online_friends': online_delhivery_boys,
            'me': current_user.my_json
        })

class MessagesHandler(Resource):
    def get_messages_ordered_by_date(self,messages):
        return DelhiveryMessages.objects.filter(id__in=messages).order_by('-id')
    
    def fetch_messages_by_skip_limit(self,messages,skip,limit):
        sorted_messages = self.get_messages_ordered_by_date(messages)
        limited_messages = sorted_messages.skip(skip).limit(limit)
        return limited_messages

    @login_required
    def get(self):
        me = current_user.id
        friend = DelhiveryUser.objects.get(id=request.args.get('friend_id')).id
        skip = int(request.args.get('skip'))
        limit = int(request.args.get('limit'))
        chat,status = DelhiveryChat.get_chat(me,friend)
        if status:
            messages = chat.messages
            limited_messages = self.fetch_messages_by_skip_limit(messages,skip,limit)
            messages = [message.json for message in limited_messages]
            return jsonify({
                'messages': messages
            })
        return jsonify({
            'messages': []
        })