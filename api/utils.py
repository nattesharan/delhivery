from delhivery.models import DelhiveryNotification,DelhiveryUser,DelhiveryTask
from flask_login import current_user
def create_notification(notif_type,notify_to):
    notification = DelhiveryNotification(notification_type=notif_type)
    if notif_type == 'FRIEND_REQUEST':
        notification.notification_message = 'Recieved a Friend request from {}'.format(current_user.name)
    if notif_type == 'CANCEL_REQUEST':
        notification.notification_message = '{} has reverted back his request'.format(current_user.name)
    if notif_type == 'ACCEPT_REQUEST':
        notification.notification_message = '{} has accepted your friend request'.format(current_user.name)
    notification.user_to_notify = notify_to.id
    notification.initiated_by = current_user.id
    notification.save()
    return notification

def create_user_notifications(notif_type, task):
    notification = DelhiveryNotification(notification_type=notif_type)
    if notif_type == 'ACCEPTED_TASK':
        notification.notification_message = '{} accepted by {}'.format(task.title,current_user.name)
    notification.user_to_notify = task.created_by.id
    notification.initiated_by = current_user.id
    notification.save()
    return notification

def get_notifications_sorted_by_date(user_id):
    return DelhiveryNotification.objects.filter(user_to_notify=user_id).order_by('-id')

def get_notifications_for_dashboard(user_id):
    notifications = get_notifications_sorted_by_date(user_id)
    return [notification.notif_json for notification in notifications[:5]]

def get_all_notifications(skip,limit):
    notifications = get_notifications_sorted_by_date(current_user.id)
    user_notifications = notifications.skip(skip).limit(limit)
    return [notification.notif_json for notification in user_notifications]

def get_all_people():
    people = DelhiveryUser.objects.filter(role__ne=current_user.role)
    return [person.json for person in people]

def get_all_online_delhivery_boys(user):
    delhivery_boys = DelhiveryUser.objects.filter(is_online=True, role__ne=user.role)
    return delhivery_boys

def get_all_online_delivery_boys_json():
    online_users = get_all_online_delhivery_boys(current_user)
    return [user.online_json for user in online_users]

def get_all_my_tasks(user_id):
    tasks = DelhiveryTask.objects.filter(handled_by=user_id)
    return {
        'tasks': [task.json for task in tasks]
    }

def get_all_my_pending_tasks(user_id):
    pending_status = ['Accepted']
    pending_tasks = DelhiveryTask.objects.filter(handled_by=user_id, state__in=pending_status)
    return pending_tasks