var robo = angular.module('robo', ['ngRoute','roboservice']);

robo.config(function($routeProvider) {
    $routeProvider
        .when('/newtask', {
            templateUrl: 'partials/newtask.html',
            controller: 'newtaskController'
        })
        .when('/report', {
            templateUrl: 'partials/report.html',
            controller: 'reportController'
        })
        .when('/slave', {
            templateUrl: 'partials/slave.html',
            controller: 'slaveController'
        }).otherwise({
        redirectTo: '/'
      });

});


