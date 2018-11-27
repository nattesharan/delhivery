MONGODB_SETTINGS = {
    'db': 'delhivery',
    'host': '127.0.0.1',
    'port': 27017
}

NOTIFICATION_TYPES = {
    'FRIENDLY': 'FRIEND_REQUEST',
    'CANCEL_REQUEST': 'CANCEL_REQUEST',
    'ACCEPT_REQUEST': 'ACCEPT_REQUEST'
}

ROLES = [
    {"name": 'Store Manager', 'role': 'STORE_MANAGER'},
    {"name": 'Delivery Boy', 'role': 'DELIVERY_BOY'}
]

FEATURES = {
    'features_create_tasks': {
        'title': "Features for creating tasks",
        'enabled': True
    },
    'featutes_view_all_tasks': {
        'title': "Features for viewing all tasks",
        'enabled': True
    },
    'features_cancel_unaccepted_tasks': {
        'title': "Features for cancelling unaccepted tasks",
        'enabled': True
    },
    'features_see_state_transistions': {
        'title': "Features for seeing the task transistions",
        'enabled': True
    },
    'features_view_accepted_tasks': {
        'title': 'Features for viewing his current accepted tasks',
        'enabled': True
    },
    'features_complete_tasks': {
        'title': "Features for completing the tasks",
        'enabled': True
    },
    'features_view_high_priority_task': {
        'title': "Features to view single high priority task if any",
        'enabled': True
    },
    'features_accept_task': {
        'title': "Features to accept task",
        'enabled': True
    }
}