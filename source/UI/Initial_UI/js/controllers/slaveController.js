
robo.controller('reportController', ['$scope','robofactory',function($scope,robofactory) 
      { 
          $scope.slaves = robofactory.query();
      
       }]);
