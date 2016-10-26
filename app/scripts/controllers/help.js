'use strict';


angular.module('ddtApp')
  .controller('helpCtrl', function ($scope, $rootScope, $http, $state, $mdToast, AUTH_EVENTS, AuthService, IdleService) {

    $scope.doClearDoc = function(){
      $http.post('http://localhost:5000/clearAllDoc').then(function(response){
          console.log('delete file task status: '+response.data.status);
      }, function (){

      });
    }



});
