from werkzeug.security import generate_password_hash,check_password_hash
from mongoengine import Document,StringField,DoesNotExist,ListField,BooleanField,ReferenceField,DateTimeField, IntField
from flask_login import UserMixin,current_user
import mongoengine
import datetime
import humanize
import uuid
import pytz
import tzlocal

local_timezone = tzlocal.get_localzone()
class DelhiveryHierarchy(Document):
    name = StringField(required=True, max_length=128)
    role = StringField(max_length=128, required=True)
    features = ListField(StringField(max_length=128), default=[])

    def has_permission(self, feature):
        return feature in self.features

    @classmethod
    def get_choices(cls):
        choices = []
        roles = DelhiveryHierarchy.objects.all()
        for role in roles:
            choices.append((role.role, role.name))
        return choices

class DelhiveryUser(Document,UserMixin):
    email = StringField(max_length=128,required=True)
    password = StringField(max_length=128,required=True)
    first_name = StringField(max_length=20,required=True)
    image = StringField(max_length=128,default='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS942xv3bE55-_AwDA31FCNGhfWNDaAmmUXy3a3uxRwrV-lcZu6')
    last_name = StringField(max_length=20,required=True)
    chats = ListField(StringField())
    is_online = BooleanField(default=False)
    role = ReferenceField(DelhiveryHierarchy, reverse_delete_rule=mongoengine.CASCADE)
    def set_password(self,password):
        self.password = generate_password_hash(password,method='sha256')
    
    def verify_password(self,password):
        return check_password_hash(self.password,password)
    
    def become_online(self):
        self.is_online = True
        self.save()
    
    def become_offline(self):
        self.is_online = False
        self.save()
    
    def is_allowed(self, feature):
        return self.role.has_permission(feature)

    def get_current_user_status(self):
        if current_user in self.friends and self in current_user.friends:
            return 'Friends'
        elif current_user in self.received_friend_requests:
            return 'Cancel'
        elif self in current_user.received_friend_requests:
            return 'Accept'
        else:
            return 'Add Friend'

    @classmethod
    def find_user(cls,email):
        try:
            return bool(cls.objects.get(email=email))
        except DoesNotExist:
            return False
    
    @property
    def name(self):
        return self.first_name + ' ' + self.last_name
    
    @property
    def json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'image': self.image,
            'role': self.role.name,
            'status': 'Friends'
        }
    @property
    def my_json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'image': self.image,
        }
    @property
    def online_json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'image': self.image,
            'is_online': self.is_online
        }

class DelhiveryNotification(Document):
    notification_type = StringField(max_length=20,required=True)
    is_read = BooleanField(default=False)
    read_at = DateTimeField()
    notification_message = StringField(max_length=128,required=True)
    user_to_notify = ReferenceField(DelhiveryUser,reverse_delete_rule=mongoengine.CASCADE)
    initiated_by = ReferenceField(DelhiveryUser,reverse_delete_rule=mongoengine.CASCADE)

    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.datetime.now()
        self.save()
        return self.notif_json

    @property
    def json(self):
        return {
            'is_read': self.is_read,
            'notification_message': self.notification_message,
            'user_to_notify': str(self.user_to_notify),
            'initiated_by': str(self.initiated_by)
        }
    
    @property
    def notif_json(self):
        return {
            'message': self.notification_message,
            'is_read': self.is_read,
            'id': str(self.id),
            'image': self.initiated_by.image,
            'name': self.initiated_by.name
        }

class DelhiveryMessages(Document):
    message_text = StringField(max_length=1024,required=True)
    sent_by = ReferenceField(DelhiveryUser)
    sent_to = ReferenceField(DelhiveryUser)
    read_on = DateTimeField()

    def __str__(self):
        return str(self.id)
    
    @classmethod
    def new_message(cls,message_text,sender,receiver):
        return cls.objects.create(
            message_text = message_text,
            sent_by = sender,
            sent_to = receiver
        )
    @property
    def json(self):
        return {
            'message': self.message_text,
            'sent_by_me': self.sent_by.id == current_user.id
        }

class DelhiveryChat(Document):
    chat_id = StringField(required=True)
    chat_created_on = DateTimeField(default=datetime.datetime.now())
    chat_initiated_by = ReferenceField(DelhiveryUser)
    chat_initiated_for = ReferenceField(DelhiveryUser)
    messages = ListField(ReferenceField(DelhiveryMessages,reverse_delete_rule=mongoengine.CASCADE))

    def __str__(self):
        return self.chat_id

    @classmethod
    def get_or_create_chat(cls,sender,receiver):
        friends = [sender,receiver]
        try:
            chat = cls.objects.get(chat_initiated_by__in=friends,chat_initiated_for__in=friends)
            return chat
        except DoesNotExist:
            chat = cls.objects.create(
                    chat_id = str(uuid.uuid4()),
                    chat_initiated_by = sender,
                    chat_initiated_for = receiver
                )
            sender.chats.append(chat.chat_id)
            sender.save()
            receiver.chats.append(chat.chat_id)
            receiver.save()
            return chat
    
    @classmethod
    def get_chat(cls,sender,receiver):
        friends = [sender,receiver]
        try:
            chat = cls.objects.get(chat_initiated_by__in=friends,chat_initiated_for__in=friends)
            return chat,True
        except DoesNotExist:
            return None,False
class DelhiveryTaskTimeline(Document):
    state = StringField(required=True, choices=('New','Accepted','Completed','Declined', 'Cancelled'))
    user_ref = ReferenceField(DelhiveryUser)
    @classmethod
    def create_timeline_entry(cls, state, user):
        timeline_entry = cls(state=state,user_ref=user)
        timeline_entry.save()
        return timeline_entry.id
    
    @property
    def json(self):
        localtime = self.id.generation_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        return {
            'state': self.state,
            'time': self.id.generation_time.isoformat(),
            'user': self.user_ref.name,
            'humanize_time': humanize.naturaltime(localtime.replace(tzinfo=None))
        }
class DelhiveryTask(Document):
    title = StringField(required=True, max_length=256)
    # zero has the hishest priority
    priority =  IntField(required=True,choices=(0,1,2))
    state = StringField(required=True, choices=('New','Accepted','Completed','Declined', 'Cancelled'), default='New')
    archieved = BooleanField(default=False)
    timeline = ListField(ReferenceField(DelhiveryTaskTimeline))
    description = StringField(required=True,max_length=512)
    created_by = ReferenceField(DelhiveryUser, reverse_delete_rule=mongoengine.CASCADE)
    handled_by = ReferenceField(DelhiveryUser, reverse_delete_rule=mongoengine.CASCADE, default=None)

    @property
    def state_timeline(self):
        return [timeline_ref.json for timeline_ref in self.timeline]
    def update_state(self, state):
        self.state = state
        self.timeline.append(DelhiveryTaskTimeline.create_timeline_entry(state, current_user.id))
    @classmethod
    def create_task(cls, data):
        try:
            task = cls(title=data['title'], priority=data['priority'], description=data['description'])
            task.created_by = current_user.id
            task.update_state('New')
            task.save()
            return True
        except:
            return False
    @property
    def json(self):
        localtime = self.id.generation_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
        priorities = ['High','Medium','Low']
        return {
            'id': str(self.id),
            'title': self.title,
            'priority': priorities[self.priority],
            'state': self.state,
            'created_by': self.created_by.json,
            'created_on': self.id.generation_time.isoformat(),
            'handled_by': self.handled_by.name if self.handled_by else 'Not Accepted Yet',
            'humanized_time': humanize.naturaltime(localtime.replace(tzinfo=None))
        }
    @classmethod
    def latest_tasks(cls):
        tasks = cls.objects.filter(state='New',handled_by=None,archieved=False)
        recommended_task = tasks.order_by('priority').first()
        if tasks:
            return {
                'recommended_task': recommended_task.json,
                'available_tasks': [task.json for task in tasks]
            }
        else:
            return {
                'recommended_task': {},
                'available_tasks': [],
                'message': 'No tasks available to Accept'
            }
