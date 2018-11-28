angular.module('delhivery').controller('DashboardController', DashboardController);

DashboardController.$inject = ['$scope'];

function DashboardController($scope) {
    var vm = this;
    vm.test = test;
    function test() {
        console.log("it worked");
    }
}

angular.module('delhivery').controller('delhiveryController', delhiveryController);
delhiveryController.$inject = ['socket'];

function delhiveryController(socket) {
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
    }
}

angular.module('delhivery').controller('TasksControllerDeliveryAgent', TasksViewController)
TasksViewController.$inject = ['$http','socket', '$mdDialog']
function TasksViewController($http, socket, $mdDialog) {
    var vm = this;
    vm.fetchNewTask = fetchNewTask
    vm.acceptTask = acceptTask;
    vm.fetchMyTasks = fetchMyTasks;
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
angular.module('delhivery').controller('FindFriendsController', FindFriendsController);
FindFriendsController.$inject = ['$http','socket','Notification','$mdDialog'];

function FindFriendsController($http,socket,Notification,$mdDialog){
    var vm = this;
    vm.active = {};
    vm.people = [];
    vm.addFriend = addFriend;
    vm.acceptRequest = acceptRequest;
    vm.cancelRequest = cancelRequest;
    vm.fetchFriends = fetchFriends;
    vm.confirmUnfriend = confirmUnfriend;

    function confirmUnfriend(event,person_id,person_name) {
        var confirm = $mdDialog.confirm()
          .title(`Would you really want to unfriend ${person_name}?`)
          .textContent('This action cannot be reverted.')
          .ariaLabel('confirmUnfriend')
          .targetEvent(event)
          .ok('Unfriend')
          .cancel('Cancel');

        $mdDialog.show(confirm).then(function() {
            $http({
                method: 'PUT',
                url: '/api/friends',
                data: {
                    'person_id': person_id
                }
            }).then(function result(response) {
                if(response.data.success) {
                    vm.people = response.data.friends;
                    Notification.success({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
                }
                else {
                    Notification.error({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
                }
            });
        });
    }
    function fetchFriends() {
        $http({
            method: 'GET',
            url: '/api/friends'
        }).then(function result(response) {
            vm.people = response.data.friends;
        });
    }
    function addFriend(person_id) {
        var data = { 'person_id': person_id };
        $http({
            method: 'POST',
            url: '/api/friend-request',
            data: data
        }).then(function result(response) {
            if(response.data.success) {
                vm.people = response.data.friends;
                Notification.success({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
            }
            else {
                Notification.error({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
            }
        });
    }

    function acceptRequest(person_id) {
        $http({
            method: 'PUT',
            url: '/api/friend-request',
            data: {
                'person_id': person_id
            }
        }).then(function result(response) {
            if(response.data.success) {
                Notification.success({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
                fetchFriends();
            }
            else {
                Notification.error({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
            }
        });
    }

    function cancelRequest(person_id) {
        $http({
            method: 'DELETE',
            url: '/api/friend-request',
            params: {
                'person_id': person_id
            }
        }).then(function result(response) {
            if(response.data.success) {
                vm.people = response.data.friends;
                Notification.success({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
            }
            else {
                Notification.error({message: response.data.message, delay: 1000, positionY: 'bottom', positionX: 'right'});
            }
        });
    }

    socket.on('connected_online',function(data) {
        data.users.forEach(user => {
            vm.active[user] = true;
        });
    });
    
    socket.on('update_people_list',function() {
        fetchFriends();
    });
    
    socket.on('disconnected_offline',function(data) {
        vm.active = {};
        data.users.forEach(user => {
            vm.active[user] = true;
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
