from flask_restful import Resource
from flask import request,jsonify
import requests
from flask_login import login_required,current_user
from app.settings import NOTIFICATION_TYPES
from app.utils import feature_enable
from delhivery.models import DelhiveryUser,DelhiveryNotification,DelhiveryChat, DelhiveryMessages, DelhiveryTask
from api.utils import create_notification, get_notifications_for_dashboard, get_all_notifications,\
                        get_all_online_delivery_boys_json, create_user_notifications, get_all_my_tasks,\
                        get_all_my_pending_tasks, get_all_my_created_tasks
from app import notify_user,refresh_online_friends, refresh_tasks_delivery_agent,\
                refresh_store_manager_tasks, hard_notify_user

class TasksResourceStoreManager(Resource):
    @login_required
    @feature_enable('features_create_tasks')
    def post(self):
        data = request.get_json()
        success = DelhiveryTask.create_task(data)
        if success:
            refresh_tasks_delivery_agent('DELIVERY_BOY')
            return jsonify({
                'success': success,
                'message': 'Successfully created the task'
            })
        return jsonify({
            'success': success,
            'message': 'Error occured while creating the task'
        })
    @login_required
    @feature_enable('features_fetch_created_tasks')
    def get(self):
        tasks = get_all_my_created_tasks(current_user.id)
        return tasks
    
    @login_required
    @feature_enable('features_cancel_unaccepted_tasks')
    def put(self):
        data = request.get_json()
        task = DelhiveryTask.objects.get(id=data['task_id'])
        if task.state == 'New':
            task.update_state('Cancelled')
            task.archieved = True
            task.save()
            return {
                'success': True,
                'message': 'Successfully cancelled the task'
            }
        else:
            return {
                'success': False,
                'message': 'Task is too ahead to cancel to cancel a task it must be in accepted state'
            }
class TasksResourceDeliveryAgent(Resource):

    @login_required
    @feature_enable('features_complete_tasks')
    @feature_enable('features_decline_task')
    def post(self):
        data = request.get_json()
        task = DelhiveryTask.objects.get(id=data['task_id'], state='Accepted')
        if data['action_type'] == 'completed':
            task.update_state('Completed')
            task.save()
            notification = create_user_notifications(NOTIFICATION_TYPES['COMPLETED_TASK'], task)
            notify_user(str(task.created_by.id))
            refresh_store_manager_tasks(str(task.created_by.id))
            return {
                'success': True,
                'message': 'Successfully marked the task as completed'
            }
        if data['action_type'] == 'declined':
            task.update_state('Declined')
            task.update_state('New')
            task.save()
            notification = create_user_notifications(NOTIFICATION_TYPES['DECLINED_TASK'], task)
            notify_user(str(task.created_by.id))
            refresh_store_manager_tasks(str(task.created_by.id))
            hard_notify_user(str(task.created_by.id), notification.notification_message )
            return {
                'success': True,
                'message': 'Successfully declined the task'
            }

    @login_required
    @feature_enable('features_view_accepted_tasks')
    @feature_enable('featutes_view_all_tasks')
    @feature_enable("features_view_high_priority_task")
    def get(self):
        me = request.args.get('me') == 'true'
        if me:
            my_tasks = get_all_my_tasks(current_user.id)
            return my_tasks
        else:
            pending_tasks = get_all_my_pending_tasks(current_user.id)
            if len(pending_tasks) >= 3:
                return {
                    'recommended_task': {},
                    'available_tasks': [],
                    'message': 'Maximum of three tasks are accepted by agent please complete and try fetching'
                    }
            latest_tasks = DelhiveryTask.latest_tasks()
            return latest_tasks
    @login_required
    @feature_enable("features_accept_task")
    def put(self):
        data = request.get_json()
        task = DelhiveryTask.objects.get(id=data['task_id'])
        task.update_state('Accepted')
        task.handled_by = current_user.id
        task.save()
        notification = create_user_notifications(NOTIFICATION_TYPES['ACCEPTED_TASK'], task)
        refresh_tasks_delivery_agent('DELIVERY_BOY')
        refresh_store_manager_tasks(str(task.created_by.id))
        notify_user(str(task.created_by.id))

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