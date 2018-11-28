angular.module('delhivery').factory('socket', ['$rootScope', function($rootScope){
    $rootScope.server_ip = 'http://192.168.1.18:8080/';  
  
    var socket = io.connect($rootScope.server_ip);
    return {
      on: function(eventName, callback) {
          function wrapper() {
              var args = arguments;
              $rootScope.$apply(function() {
                  callback.apply(socket, args);
              });
          }
          socket.on(eventName, wrapper);
          return function() {
              socket.removeListener(eventName, wrapper);
          };
      },
      emit: function(eventName, data, callback) {        
          socket.emit(eventName, data, function() {
              var args = arguments;
              $rootScope.$apply(function() {
                  if (callback) {
                      callback.apply(socket, args);
                  }
              });
          });
      }    
    };  
  }]);