'use strict';


angular.module('ddtApp')
  .controller('queryBuilderCtrl', function ($log, $q, $scope, $rootScope, $mdDialog, $http, $state, $mdToast, AUTH_EVENTS, AuthService, FileUploader, IdleService) {

    $scope.customFullscreen = false;
    $scope.selectedConnKey = [];
    $scope.searchText = '';
    $scope.showPopover=false;


    $scope.newquery = {
      creation_user : $scope.currentUser ? $scope.currentUser.id : '',
      query_text: '',
      conn_key : '',
      query_descr: '',
    }
    $scope.queryUploader = new FileUploader({
      url: 'http://localhost:5000/checkQueryTextFile',
      autoUpload : true,
      removeAfterUpload : true,
      queueLimit: 1
    });


    $http.get('http://localhost:5000/getConnectionFull').then(function (response){
      $scope.conn_keys_respo = response.data.status;
    }, function(){

    });

    $scope.queryUploader.onSuccessItem  = function(item, response){
      $scope.newquery.query_text = response.status ;
    };

    $scope.doClearText = function(){
      $scope.newquery.query_text = '';
      $scope.queryUploader.clearQueue();
    };

    $scope.doTestQuery = function(){
      if ($scope.newquery.conn_key === undefined || $scope.newquery.conn_key === ""){
        $scope.showAlert("Please choose one connection ID");
      }
      else{
        $http.post('http://localhost:5000/testSQLQuery', $scope.newquery).then(function (response){
          $mdDialog.show(
            $mdDialog.alert()
              .parent(angular.element(document.querySelector('#popupContainer')))
              .clickOutsideToClose(true)
              .title('Alter Message')
              .textContent(response.data.status.mgs)
              .ariaLabel('Alert Dialog')
              .ok('Got it!')
              // .targetEvent(ev)
          );
        }, function(){

        });
      }
    };


    $scope.setIndex = function (index){
      $scope.selectedIndex = index;
      //$scope.onShowPeriodChanged();
    };

    $scope.searchTextChange = function(text) {
      $log.info('Text changed to ' + text);
    };

    $scope.selectedConnKeyChange = function(item) {
      $log.info('Conn Key changed to ' + JSON.stringify(item));
    };

    $scope.querySearch  = function(query) {
      var results = query ? $scope.conn_keys_respo.filter( createFilterFor(query) ) : $scope.conn_keys_respo,
          deferred;
      // var simulateQuery = false;
      // if (simulateQuery) {
      //   deferred = $q.defer();
      //   $timeout(function () { deferred.resolve( results ); }, Math.random() * 1000, false);
      //   return deferred.promise;
      // } else {
      //   return results;
      // }
      return results;
    };

    function createFilterFor(query) {
      var uppercaseQuery = angular.uppercase(query);

      return function filterFn(item) {
        return (item.conn_key.indexOf(uppercaseQuery) === 0);
      };

    };

    $scope.showAlert = function(msg) {
   // Appending dialog to document.body to cover sidenav in docs app
   // Modal dialogs should fully cover application
   // to prevent interaction outside of dialog
       $mdDialog.show(
         $mdDialog.alert()
           .parent(angular.element(document.querySelector('#popupContainer')))
           .clickOutsideToClose(true)
           .textContent(msg)
           .ok('Got it!')
       );
    };

});
