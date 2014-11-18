
robo.controller('slaveController', ['$scope','robofactory',function($scope,robofactory) 
      { 
                  $scope.slaves = robofactory.query();
                  

           
      }]);

