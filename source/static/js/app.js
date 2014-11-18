var robo = angular.module('robo', ['ngRoute']);

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

robo.controller('roboController', function($scope, roboService) { 
    $scope.newJob =  {}

    $scope.submitNewJob = function(){
        roboService.startJob($scope.newJob).then(function(data){
            console.dir(data)
        })
    }

  

});

