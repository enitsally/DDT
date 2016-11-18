'use strict';


angular.module('ddtApp')
  .controller('helpCtrl', function ($scope, $rootScope, $http, $state, $mdToast, $mdDialog,AUTH_EVENTS, AuthService, IdleService) {

    $scope.doClearDoc = function(){
      $http.post('/clearAllDoc').then(function(response){

          var message = 'Deleted file number: ' + response.data.status.length;
          console.log('delete file id: '+response.data.status);
          $mdDialog.show(
            $mdDialog.alert()
              .parent(angular.element(document.querySelector('#popupContainer')))
              .clickOutsideToClose(true)
              .textContent(message)
              .ok('Got it!')
          );
      }, function (){

      });
    }



});
