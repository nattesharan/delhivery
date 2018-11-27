# delhivery

Social website built with Flask,Angular,Mongodb and Socket Io

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

```
* MongoDB
* Python
```

### Installing

A step by step series of examples that tell you how to get a development env running

```
git clone https://github.com/nattesharan/delhivery.git
cd delhivery/
virtualenv delhivery
source delhivery/bin/activate
pip install -r requirements.txt
python manage.py dev
check localhost:8080
```
For running in production
```
pip install gunicorn
delhivery/bin/gunicorn -b :8080 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 main:app --reload

```
### Sockets from frontend
Firstly establish a socket connection by specifying the url like host:port

* Socket on successful connection and on successfull connection create personal room for the user by sending the user info
```
    socket.on('connect',function() {
            socket.emit('create_room',data);
    });
```
* Socket on receiving friend request to show the notification
```
    socket.on('received_friend_request',function(data) {
        // Add your funtionality
    });
```
* Socket when someone connects online it sends the user info who has connected online
```
    socket.on('connected_online',function(data) {
        // Add your functionality
    });
```
* When a friend request is sent,cancelled,or accepted refresh the friends state
```
    socket.on('update_people_list',function() {
        // Add your functionality
    });
```
* When someone logs out or disconnects the backend sends the user info who has disconnected
```
    socket.on('disconnected_offline',function(data) {
        // Add your functionality
    });
```
* Emit Socket along with message and receiver info for sending message
```
    socket.emit('send_message',data);
```
* Emit typing event to friend when typing 
```
    socket.emit('typing',friendInfo)
```
* Emit stopped typing event when user stopped typing
```
    socket.emit('no_longer_typing',friendInfo);
```
* When someone goes offline when chatting
```
    socket.on('refresh_online_friends',function() {
            // Add your functionality
        });
```
* When the user gets new message
```
    socket.on('new_message',function() {
            // Add your functionality
        });
```
* When the sender send the message successfully
```
    socket.on('refresh_sender',function() {
        // Add your functionality
    });
```
* When the user receives typing event from the sender
```
    socket.on('sender_is_typing',function(data) {
            // Add your functionality
        });
```
* When the user receives stopped typing event from the sender
```
    socket.on('sender_stopped_typing',function(data) {
            // Add your functionality
    });
```
* When the user sends messge but they are no longer friends
```
    socket.on('not_friends',function() {
            // Add your functionality
        });
```