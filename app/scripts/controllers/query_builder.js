'use strict';


angular.module('ddtApp')
  .controller('queryBuilderCtrl', function ($log, $q, $scope, $rootScope, $mdDialog, $http, $state, $mdToast, $mdMedia, AUTH_EVENTS, AuthService, FileUploader, IdleService) {

    $scope.customFullscreen = false;
    $scope.selectedConnKey = [];
    $scope.searchText = '';
    $scope.searchText_new = '';
    $scope.searchText_descr = '';
    $scope.showPopover = false;
    $scope.query_user = $scope.currentUser ? $scope.currentUser.id : '',


    $scope.newquery = {
      creation_user : $scope.currentUser ? $scope.currentUser.id : '',
      query_text: '',
      conn_key : '',
      query_descr: '',
    }

    $scope.newquerybypattern = {
      creation_user : $scope.currentUser ? $scope.currentUser.id : '',
      query_text: '',
      conn_key : '',
      query_descr: '',
      condition_list : [],
      selection_list : [],
      pattern_id: '',
      pattern_descr: ''
    }
    $scope.queryUploader = new FileUploader({
      url: '/checkQueryTextFile',
      autoUpload : true,
      removeAfterUpload : true,
      queueLimit: 1
    });


    $http.get('/getConnectionFull').then(function (response){
      $scope.conn_keys_respo = response.data.status;
    }, function(){

    });

    $scope.queryUploader.onSuccessItem  = function(item, response){
      $scope.newquery.query_text = response.status ;
    };



    $http.post('/getPatternSummaryByUser', $scope.query_user).then(function(response){
        $scope.patternInfo = response.data.status;
    }, function (){

    });


    $scope.setIndex = function (index){
      $scope.selectedIndex = index;
    };

    $scope.doClearQueryText = function(){
      $scope.newquery.query_text = '';
      $scope.newquery.conn_key = '';
      $scope.newquery.query_descr = '';
      $scope.searchText_new = '';

      $scope.queryUploader.clearQueue();
    };

    $scope.doClearQueryTextByPattern = function(){
      $scope.newquerybypattern.query_text = '';
      $scope.newquerybypattern.conn_key = '';
      $scope.newquerybypattern.query_descr = '';
      $scope.newquerybypattern.condition_list = [];
      $scope.newquerybypattern.selection_list = [];
      $scope.newquerybypattern.pattern_id = '';
      $scope.newquerybypattern.pattern_descr = '';

      $scope.searchText_descr = '';
      $scope.searchText = '';

    };

    $scope.doTestQuery = function(){
      var sql = {
        query_text : '',
        conn_key : ''
      };

      if ($scope.selectedIndex === 0){
        if ($scope.newquery.conn_key === undefined || $scope.newquery.conn_key === null || $scope.newquery.conn_key === "" || $scope.newquery.conn_key.conn_key === "") {
          $scope.showAlert("Please choose one connection ID");
          return;
        }
        else{
          sql.query_text = $scope.newquery.query_text;
          sql.conn_key = $scope.newquery.conn_key.conn_key;
        }
      }
      else {
        if ($scope.newquerybypattern.conn_key === undefined || $scope.newquerybypattern.conn_key === null || $scope.newquerybypattern.conn_key.conn_key === "" || $scope.newquerybypattern.conn_key === "") {
          $scope.showAlert("Please choose one connection ID");
          return;
        }
        else if ($scope.newquerybypattern.selection_list.length === 0) {
          if ($scope.newquerybypattern.query_text === ""){
            $scope.showAlert("Query is empty.");
            return;
          }
          else{
            var selected_column = [];
            angular.forEach($scope.newquerybypattern.selection_list, function(item){
              if (item.value !== undefined){
                selected_column.push(item);
              }
            });

            if (selected_column.length === 0 && selected_column.length !== $scope.newquerybypattern.selection_list.length){
              $scope.showAlert("Must have at least one selected column");
              return;
            }
          }
        }

        sql.query_text = $scope.newquerybypattern.query_text;
        if (typeof $scope.newquerybypattern.conn_key === "string")
        {
          sql.conn_key = $scope.newquerybypattern.conn_key ;
        }
        else{
          sql.conn_key = $scope.newquerybypattern.conn_key.conn_key ;
        }

      }

      if (sql.query_text !== "" && sql.conn_key !== ""){
        $http.post('/testSQLQuery', sql).then(function (response){
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
      else{
        $scope.showAlert("Query is empty.");
      }

    };

    $scope.doSendQuerytoPool = function(){

    };

    $scope.doCreateQueryTextByPattern = function(){
      if ($scope.newquerybypattern.conn_key === null || $scope.newquerybypattern.conn_key === "" ){
        $scope.showAlert("Please choose one connection ID");
        return;
      }
      else if ($scope.newquerybypattern.query_text === null || $scope.newquerybypattern.query_text === "" ) {
        $scope.showAlert("Query text is empty.");
        return;
      }
      else{
        $http.post('/createSQLByPattern', $scope.newquerybypattern).then(function(response){
            $scope.newquerybypattern.query_text  = response.data.status;
        })

      }
    };


    $scope.searchTextChange = function(text) {
      $log.info('Text changed to ' + text);
    };

    $scope.selectedConnKeyChange = function(item) {
      $log.info('Conn Key changed to ' + JSON.stringify(item));
    };

    $scope.selectedPatternChange = function(item) {
      if (item !== undefined){
        $scope.newquerybypattern.query_text = item.pattern_text;
        $scope.newquerybypattern.selection_list = item.selection_subArea;
        $scope.newquerybypattern.condition_list = item.condition_subArea;
        $scope.newquerybypattern.conn_key = item.connection_key;
        $scope.newquerybypattern.pattern_id = item._id;
        $scope.newquerybypattern.pattern_descr = item.pattern_descr;
      }

    };

    $scope.doSetCondition = function(){

      var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
      $mdDialog.show({
            controller: DialogController,
            templateUrl: 'views/dialog.set.pattern.condition.html',
            parent: angular.element(document.body),
            clickOutsideToClose: false,
            fullscreen: useFullScreen,
            locals:{
              result: $scope.newquerybypattern

            },
            scope: $scope,
            preserveScope: true
          });

    };

    $scope.doSetSelection = function(){

      var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
      $mdDialog.show({
            controller: DialogController,
            templateUrl: 'views/dialog.set.pattern.selection.html',
            parent: angular.element(document.body),
            clickOutsideToClose: false,
            fullscreen: useFullScreen,
            locals:{
              result: $scope.newquerybypattern

            },
            scope: $scope,
            preserveScope: true
          });

    };

    function DialogController($scope, $mdDialog, result) {
      $scope.save_result = result;
      $scope.hide = function() {
        $mdDialog.hide();
      };
      $scope.cancel = function() {
        $mdDialog.cancel();
      };
      $scope.answer = function(answer) {
        $mdDialog.hide(answer);
      };
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

    $scope.querySearchByPattern  = function(query) {
      var results = query ? $scope.patternInfo.filter( createFilterForPattern(query) ) : $scope.patternInfo,
          deferred;

      return results;
    };

    function createFilterFor(query) {
      var uppercaseQuery = angular.uppercase(query);

      return function filterFn(item) {
        return (item.conn_key.indexOf(uppercaseQuery) === 0);
      };

    };

    function createFilterForPattern(query) {

      var uppercaseQuery = angular.uppercase(query);

      return function filterFn(item) {
        return (item.pattern_descr.indexOf(uppercaseQuery) === 0);
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

})
.filter('searchFor', function(){
    return function(arr, searchString){
        if(!searchString){
            return arr;
        }
        var result = [];
        searchString = searchString.toLowerCase();
        angular.forEach(arr, function(item){
            if(item.pattern_descr.toLowerCase().indexOf(searchString) !== -1){
            result.push(item);
        }
        });
        return result;
    };
});
