var roboservice = angular.module('roboservice',['ngResource']);
robo.factory('robofactory',['$resource',
  function($resource)
     {
              return $resource('json/slave.json');  
	                    
	
     }]);