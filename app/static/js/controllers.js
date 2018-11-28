angular.module('delhivery').controller('delhiveryController', delhiveryController);
delhiveryController.$inject = ['socket', 'Notification'];

function delhiveryController(socket, Notification) {
    var vm = this;
    vm.establishConnection = establishConnection;
    function establishConnection(user_id) {
        var data = { 'user_id': user_id};
        socket.on('connect',function() {
            socket.emit('create_room',data);
        });
        socket.on('disconnect',function() {
            console.log("disconnected");
        });
        socket.on('hard_notify_users', function(data) {
            Notification.error({message: data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
        })
    }
}

angular.module('delhivery').controller('ViewTaskController', ViewTaskController)
ViewTaskController.$inject = ['$http','$mdDialog', 'Notification']
function ViewTaskController($http, $mdDialog, Notification) {
    var vm = this;
    vm.showcancel = true;
    vm.cancelTask = cancelTask;
    function cancelTask(event, task_id, task_title) {
        var confirm = $mdDialog.confirm()
        .title(`Would you really want to accept ${task_title}?`)
        .textContent('This action cannot be reverted.')
        .ariaLabel('confirmCancel')
        .targetEvent(event)
        .ok('Yes, I understand')
        .cancel('Close');
        $mdDialog.show(confirm).then(function() {
            $http({
                'method': 'PUT',
                'url': '/api/storemanager/tasks',
                'data': {
                    'task_id': task_id
                }
            }).then(function result(response) {
                if(response.data.success) {
                    Notification.success({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
                    vm.showcancel = false;
                }
                else {
                    Notification.error({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
                }
            });
        });
    }
}
angular.module('delhivery').controller('TasksControllerDeliveryAgent', TasksViewController)
TasksViewController.$inject = ['$http','socket', '$mdDialog', 'Notification']
function TasksViewController($http, socket, $mdDialog, Notification) {
    var vm = this;
    vm.fetchNewTask = fetchNewTask
    vm.acceptTask = acceptTask;
    vm.fetchMyTasks = fetchMyTasks;
    vm.submitAction = submitAction;
    vm.task = {};
    vm.tasks = [];
    vm.my_tasks = [];
    socket.on('refresh_tasks', function() {
        fetchNewTask();
    });
    function acceptTask(event,task_id, task_title) {
        var confirm = $mdDialog.confirm()
          .title(`Would you really want to accept ${task_title}?`)
          .textContent('This action cannot be reverted.')
          .ariaLabel('confirmAccept')
          .targetEvent(event)
          .ok('Accept')
          .cancel('Cancel');

        $mdDialog.show(confirm).then(function() {
            $http({
                'method': 'PUT',
                'url': '/api/deliveryagent/tasks',
                'data': {
                    'task_id': task_id
                }
            })
        });
    }
    function submitAction(action_type, task_id) {
        $http({
            'method': 'POST',
            'url': '/api/deliveryagent/tasks',
            'data': {
                'action_type': action_type,
                'task_id': task_id
            }
        }).then(function result(response) {
            if(response.data.success) {
                Notification.success({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
                fetchMyTasks();
            }
        })
    }
    function fetchMyTasks() {
        $http({
            'method': 'GET',
            'url': '/api/deliveryagent/tasks',
            'params': {
                'me': true
            }
        }).then(function result(response) {
            vm.my_tasks = response.data.tasks;
        })
    }
    function fetchNewTask() {
        $http({
            'method': 'GET',
            'url': '/api/deliveryagent/tasks',
            'params': {
                'me': false
            }
        }).then(function result(response) {
            vm.task = response.data.recommended_task;
            vm.tasks = response.data.available_tasks;
            if(!vm.tasks.length) {
                vm.message = response.data.message;
            }
        });
    }
}
angular.module('delhivery').controller('TasksControllerStoreManager', TasksController);
TasksController.$inject = ['$http','Notification','socket'];
function TasksController($http,Notification, socket) {
    var vm = this;
    vm.title = '';
    vm.priorityOptions = ['High','Medium','Low'];
    vm.priority = 0;
    vm.description = '';
    vm.my_tasks = [];
    vm.createTask = createTask;
    vm.fetchMyTasks = fetchMyTasks;
    vm.viewTimeline = viewTimeline;
    socket.on('refresh_tasks_store_manager', function() {
        fetchMyTasks();
    });
    function viewTimeline(task_id){
        console.log('show timeline now')
        window.location.href = `tasks/${task_id}`;
    }
    function fetchMyTasks() {
        $http({
            'method':'GET',
            'url': '/api/storemanager/tasks'
        }).then(function result(response) {
            vm.my_tasks = response.data.tasks;
        });
    }
    function createTask() {
        var data = {
            'title': vm.title,
            'description': vm.description,
            'priority': vm.priority
        }
        $http({
            method: 'POST',
            url: '/api/storemanager/tasks',
            data: data
        }).then(function result(response) {
            if(response.data.success) {
                Notification.success({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
                vm.title = '';
                vm.priority = vm.priorityOptions[0];
                vm.description = '';
            }
            else {
                Notification.error({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
            }
        });
    }
}
angular.module('delhivery').controller('NotificationController', NotificationController);
NotificationController.$inject = ['socket','$http'];
function NotificationController(socket,$http) {
    var vm = this;
    vm.unreadNotifCount = 0;
    vm.notifications = []
    vm.fetchNotifications = fetchNotifications;
    vm.notificationsOpened = notificationsOpened;

    function notificationsOpened() {
        $http({
            method: 'PUT',
            url: '/api/notifications',
            data: {
                'read_notifications': vm.notifications
            }
        }).then(function result(response) {
            vm.unreadNotifCount = 0;
            vm.notifications = response.data.notifications;
            vm.notifications.forEach(notification => {
                if(!notification.is_read) {
                    vm.unreadNotifCount += 1;
                }
            });
        });
    }
    function fetchNotifications() {
        $http({
            method: 'GET',
            url: '/api/notifications'
        }).then(function result(response) {
            vm.notifications = response.data.notifications;
            vm.notifications.forEach(notification => {
                if(!notification.is_read) {
                    vm.unreadNotifCount += 1;
                }
            });
        });
    }
    
    socket.on('received_friend_request',function(data) {
        vm.unreadNotifCount = 0;
        vm.notifications = data;
        vm.notifications.forEach(notification => {
            if(!notification.is_read) {
                vm.unreadNotifCount += 1;
            }
        });
    });
}

angular.module('delhivery').controller('UserNotificationsController', UserNotificationsController);
UserNotificationsController.$inject = ['$http','socket'];

function UserNotificationsController($http,socket) {
    var vm = this;
    vm.notifications = [];
    vm.loadNextPageNotifications = loadNextPageNotifications;
    vm.endOfPage = false;
    vm.busy = false;
    vm.limit = 10;
    vm.skip = 0;
    function loadNextPageNotifications() {
        vm.busy = true;
        $http({
            method: 'GET',
            url: '/api/user/notifications',
            params: {
                'skip': vm.skip,
                'limit': vm.limit
            }
        }).then(function result(response) {
            vm.busy = false;
            response.data.notifications.forEach(notification => {
                vm.notifications.push(notification);
            });
            if(response.data.notifications.length < vm.limit) {
                vm.endOfPage = true;
            }
            vm.skip += vm.limit;
        });
    }
}

angular.module('delhivery').controller('OnlineWindowController', OnlineWindowController);
OnlineWindowController.$inject = ['$http','socket'];

function OnlineWindowController($http,socket) {
    var vm = this;
    vm.onlineUsers = [];
    vm.messages = [];
    vm.typing = false;
    vm.loadingMessages = false;
    vm.senderTyping = false;
    vm.timeout = undefined;
    vm.message = '';
    vm.chatUser = {};
    vm.me = {};
    vm.fetchOnlineUsers = fetchOnlineUsers;
    vm.showChatWindow = showChatWindow;
    vm.closeChatWindow = closeChatWindow;
    vm.typingMessage = typingMessage;
    vm.loadMoreMessages = loadMoreMessages;
    vm.limit = 10;
    vm.skip = 0;
    vm.endOfPageMessages = false;
    function timeoutFunction(){
        vm.typing = false;
        socket.emit('no_longer_typing',{'friend': vm.chatUser.id });
    }
    function fetchCurrentChatMessages(chat_user_id,skip,limit) {
        if(chat_user_id) {
            vm.loadingMessages = true;
            $http({
                method: 'GET',
                url: '/api/messages',
                params: {
                    'friend_id': chat_user_id,
                    'skip': skip,
                    'limit': limit
                }
            }).then(function result(response) {
                vm.loadingMessages = false;
                response.data.messages.forEach(message => {
                    vm.messages.push(message);
                });
                if(response.data.messages.length < vm.limit) {
                    vm.endOfPageMessages = true;
                }
            });
        }
    }

    function loadMoreMessages() {
        vm.skip += 10;
        fetchCurrentChatMessages(vm.chatUser.id,vm.skip,vm.limit)
    }
    function sendMessage(message) {
        var data = {
            'message': message,
            'sent_to': vm.chatUser.id,
        }
        socket.emit('send_message',data);
    }
    function typingMessage(event) {
        var key = event.which || event.keyCode;
        if(key===13) {
            event.preventDefault();
            sendMessage(vm.message);
            vm.message = '';
        } else {
            if(vm.typing == false) {
                vm.typing = true
                socket.emit('typing',{'friend': vm.chatUser.id })
                vm.timeout = setTimeout(timeoutFunction, 1000);
              } else {
                clearTimeout(vm.timeout);
                vm.timeout = setTimeout(timeoutFunction, 1000);
              }
        }
    }

    function closeChatWindow() {
        var myEl = angular.element(document.querySelector('#qnimate'));
        myEl.removeClass('popup-box-on');
    }

    function fetchOnlineUsers() {
        $http({
            method: 'GET',
            url: '/api/online-users'
        }).then(function result(response) {
            vm.onlineUsers = response.data.online_friends;
            vm.me = response.data.me;
            if(vm.onlineUsers.length) {
                vm.onlineUsers.forEach(onlineUser => {
                    if(JSON.stringify(onlineUser) === JSON.stringify(vm.chatUser)) {
                        vm.chatUser.is_online = true;
                    } else {
                        vm.chatUser.is_online = false;
                    }
                });
            } else {
                vm.chatUser.is_online = false;
            }
        });
    }

    socket.on('refresh_online_friends',function() {
        fetchOnlineUsers();
    });
    socket.on('new_message',function() {
        vm.messages = [];
        fetchCurrentChatMessages(vm.chatUser.id,0,10);
    });

    socket.on('refresh_sender',function() {
        vm.messages = [];
        fetchCurrentChatMessages(vm.chatUser.id,0,10);
    });

    socket.on('sender_is_typing',function(data) {
        if(data.typing_user === vm.chatUser.id) {
            vm.senderTyping = true;
        }
    });

    socket.on('sender_stopped_typing',function(data) {
        if(data.typing_user === vm.chatUser.id) {
        vm.senderTyping = false;
        }
    });

    socket.on('not_friends',function() {
        console.log('NO longer friends');
    });

    function showChatWindow(onlineUser) {
        vm.endOfPageMessages = false;
        vm.messages = [];
        vm.senderTyping = false;
        vm.message = '';
        vm.skip = 0;
        if(onlineUser !== vm.chatUser) {
            closeChatWindow();
        }
        var myEl = angular.element(document.querySelector('#qnimate'));
        myEl.addClass('popup-box-on');
        vm.chatUser = onlineUser;
        fetchCurrentChatMessages(vm.chatUser.id,0,10);
    };
}
