var robo = angular.module('robo', ['ngRoute', 'btford.socket-io']);

robo.factory('socket', function(socketFactory){
    return socketFactory({
        ioSocket: io.connect('http://localhost:8080')
    });
})

robo.config(function($routeProvider) {
    $routeProvider
    .when('/newtask', {
        templateUrl: 'static/partials/newtask.html',
        controller: 'roboController'
    })
    .when('/report', {
        templateUrl: 'static/partials/report.html',
        controller: 'roboController'
    })
    .when('/history', {
        templateUrl: 'static/partials/history.html',
        controller: 'roboController'
    })
    .when('/slave', {
        templateUrl: 'static/partials/slave.html',
        controller: 'roboController'
    }).otherwise({
        redirectTo: '/'
    });

});

robo.service('roboService', function($http, $rootScope){
    this.startJob = function  (data) {
        var promiss = $http({
            url : '/job',
            method: 'POST',
            data:data
        }).then( function(response){
            console.dir(response)
            return response.data
        })
        return promiss
    }
})

robo.controller('roboController', function($scope, roboService, socket) { 
    $scope.newJob =  {method:"GET", url: "http://localhost:8000/", users:20}
    socket.emit('realTimeData', '')
    socket.on('status', function(data){
        console.dir(data)
        $scope.summary = data.summary
    })
    socket.on('slave', function(data){
        console.dir(data)
        $scope.slaves = data
    })
    socket.on('history', function(data){
        console.dir(data)
        $scope.histories = data
    })
    $scope.submitNewJob = function(){
        roboService.startJob($scope.newJob).then(function(data){
            console.dir(data)
        })
    }

  

});

