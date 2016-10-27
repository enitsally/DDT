'use strict';


angular.module('ddtApp')
  .controller('patternBuilderCtrl', function ($log, $filter, $timeout, $q, $scope, $rootScope, $http, $state, $mdToast,$mdMedia,$mdDialog, FileUploader, AUTH_EVENTS, AuthService, IdleService) {

    $scope.customFullscreen = false;
    $scope.search = {
      creation_user : $scope.currentUser ? $scope.currentUser.id : '',
      start_date:'',
      end_date:'',
      conn_keys:[],
      pattern_selected: []
    };

    $scope.newcreation = {
      creation_user : $scope.currentUser ? $scope.currentUser.id : '',
      pattern_text : '',
      pattern_type : '',
      conn_key : '',
      pattern_descr: '',
      user_open_list : [],
      extended_func_list : [],
      attach_list: []
    };

    $scope.ShownPeriod = "3";
    $scope.selectedConnKey = [];
    $scope.searchText = '';
    $scope.showPopover=false;

    $scope.selectedConnKey_new = '';
    //$scope.searchText_new = '';
    //$scope.searchUser = null;

    $scope.pattern_type = [];


    var todayDate = new Date();
    $scope.maxDate = new Date(
      todayDate.getFullYear(),
      todayDate.getMonth(),
      todayDate.getDate() + 1
    );
    // var originalsubExpList = [];

    $scope.doResetInput = function(){
      $scope.newcreation.pattern_text = '';
      $scope.newcreation.pattern_type = '';
      $scope.newcreation.conn_key = undefined;
      $scope.newcreation.pattern_descr = '';
      $scope.newcreation.user_open_list = [];
      $scope.newcreation.extended_func_list = [];
      $scope.searchText_new = '';
      $scope.searchUser = '';

      $scope.patternUploader.clearQueue();
    };

    $scope.doClearText = function(){
      $scope.newcreation.pattern_text = '';
      $scope.patternUploader.clearQueue();
    };

    $scope.doClearUser = function(){
      $scope.newcreation.user_open_list = [];
    };

    $scope.doClearAttach = function(){

      for (var i = 0; i < $scope.newcreation.attach_list.length; i ++)
      {
        var attachId = $scope.newcreation.attach_list[i].file_id;
        $http.post('http://localhost:5000/clearAllAttachFile', attachId).then(function(response){
            console.log('delete file:'+ attachId + ', status: '+response.data.status);
        }, function (){

        });
      };

      $scope.newcreation.attach_list = [];
      $scope.attachmentUploader.clearQueue();
    }

    $scope.doAttachFiles = function(){
      var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
      $mdDialog.show({
            controller: DialogController,
            templateUrl: 'views/dialog.attach.pattern.file.html',
            parent: angular.element(document.body),
            clickOutsideToClose:false,
            fullscreen: useFullScreen,
            locals:{
              result: $scope.newcreation
            },
            scope: $scope,
            preserveScope: true
          });
    };

    $scope.doAttachUserGroup = function(){

      var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
      $mdDialog.show({
            controller: DialogController,
            templateUrl: 'views/dialog.assign.pattern.users.html',
            parent: angular.element(document.body),
            clickOutsideToClose:false,
            fullscreen: useFullScreen,
            locals:{
              result: $scope.newcreation
              // user: $scope.user_respo,
              // searchuser: $scope.searchUser,
              // selecteduser: $scope.selectedUser
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

    $scope.onlyLaterDate = function (date) {
      var day = date;
      return day >= $scope.search.start_date;
    };

    $scope.toggle = function (item, list) {
      var idx = list.indexOf(item);
      if (idx > -1) {
        list.splice(idx, 1);
      }
      else {
        list.push(item);
      }
    };

    $scope.exists = function (item, list) {
      return list.indexOf(item) > -1;
    };

    $scope.isIndeterminate = function() {
      return ($scope.search.pattern_selected.length !== 0 &&
          $scope.search.pattern_selected.length !== $scope.pattern_type.length);
    };

    $scope.isChecked = function() {
      return $scope.search.pattern_selected.length === $scope.pattern_type.length;
    };

    $scope.toggleAll = function() {
      if ($scope.search.pattern_selected.length === $scope.pattern_type.length) {
        $scope.search.pattern_selected = [];
      } else if ($scope.search.pattern_selected.length === 0 || $scope.search.pattern_selected.length > 0) {
        $scope.search.pattern_selected = $scope.pattern_type.slice(0);
      }
    };

    $scope.patternUploader = new FileUploader({
      url: 'http://localhost:5000/checkPatternTextFile',
      autoUpload : true,
      removeAfterUpload : true,
      queueLimit: 1
    });

    $scope.attachmentUploader = new FileUploader({
      url:'http://localhost:5000/checkPatternAttachedFile',
      queueLimit: 20
    });

    // $scope.patternUploader.filters.push({
    //   name:'txtFilter',
    //   fn: function(item, options){
    //     var name = item.name.split(".")[0]
    //     var type = item.name.split(".")[1];
    //     return 'txt'=== type;
    //   }
    // });
    //
    // $scope.uploader.filters.push({
    //   name:'txtFilter',
    //   fn: function(item, options){
    //     var name = item.name.split(".")[0]
    //     var type = item.name.split(".")[1];
    //     return 'txt'=== type;
    //   }
    // });

    $scope.patternUploader.onSuccessItem  = function(item, response){
      $scope.newcreation.pattern_text = response.status ;
    };


    $scope.attachmentUploader.onSuccessItem  = function(item, response){
      item.formData.push({descr : response.descr, objectId : response.objectId});

      if (response.status === true){

        var tmp  = {
          file_name: item.file.name,
          file_id : response.objectId,
          file_size : item.file.size,
          description: response.descr
        };

        $scope.newcreation.attach_list.push(tmp);

      } ;

    };

    $scope.doRemoveItem = function(item){

      for (var i = 0; i < $scope.newcreation.attach_list.length; i ++)
      {
        var attachId = $scope.newcreation.attach_list[i].file_id;
        if (item.formData[1].objectId === attachId)
        {
          $http.post('http://localhost:5000/clearAllAttachFile', attachId).then(function(response){
              console.log('delete file:'+ attachId + ', status: '+response.data.status);
          }, function (){

          });
          $scope.newcreation.attach_list.splice(i,1);
          break;
        }
      };
      item.remove();


    };


    $http.get('http://localhost:5000/getPatternType').then(function (response){
      $scope.pattern_type = response.data.status;
    }, function(){

    });

    $scope.onShowPeriodChanged = function (){
      $scope.search.start_date = '';
      $scope.search.end_date = '';
      $scope.search.conn_keys = [];

      var criteria = {
        time_range: $scope.ShownPeriod,
        start_date: $scope.search.start_date,
        end_date: $scope.search.end_date
      };
      $http.post('http://localhost:5000/getPatternSummary', criteria).then(function(response){
          $scope.patternInfo = response.data.status;
      }, function (){

      });
    };

    $scope.doSearchPattern = function(){
      $http.post('http://localhost:5000/getSearchedPatternSummary', $scope.search).then(function(response){
          $scope.patternInfo = response.data.status;
          console.log($scope.patternInfo);
      }, function (){

      });
    };

    $scope.setIndex = function (index){
      $scope.selectedIndex = index;
      $scope.onShowPeriodChanged();
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

    $http.get('http://localhost:5000/getConnectionFull').then(function (response){
      $scope.conn_keys_respo = response.data.status;
    }, function(){

    });

    $http.get('http://localhost:5000/getSystemUser').then(function (response){
      $scope.user_respo = response.data.status;
    }, function(){

    });


    $scope.doSavePattern = function(){
      $http.post('http://localhost:5000/saveQueryPattern', $scope.newcreation).then(function(response){

        var pattern_id = response.data.status;
        var message = "Save Pattern Failed!"
        if (pattern_id !== undefined)
        {
          message = "Pattern Saved, Pattern ID : " + pattern_id
        }
        else {

        }
        $mdDialog.show(
          $mdDialog.alert()
            .parent(angular.element(document.querySelector('#popupContainer')))
            .clickOutsideToClose(true)
            .textContent(message)
            .ok('Got it!')
        );

      }, function(){

      });
    }

    $scope.showPatternText = function (info){
      var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
      $mdDialog.show({
            controller: DialogController,
            templateUrl: 'views/dialog.conn.info.html',
            parent: angular.element(document.body),
            clickOutsideToClose:true,
            fullscreen: useFullScreen,
            locals:{
              result: info
            },
            scope: $scope,
            preserveScope: true
          });

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

    $scope.querySearchUser = function(query){
        var results = query ? $scope.user_respo.filter( createFilterForUser(query)) : $scope.user_respo,
          deferred
        return results;
    };

    $scope.transformChip = function (chip){
      if (angular.isObject(chip)) {
        return chip;
      }

    };

    $scope.searchTextChange = function(text) {
      $log.info('Text changed to ' + text);
    };

    $scope.selectedConnKeyChange = function(item) {
      $log.info('Conn Key changed to ' + JSON.stringify(item));
    };

    function createFilterFor(query) {
      var uppercaseQuery = angular.uppercase(query);

      return function filterFn(item) {
        return (item.conn_key.indexOf(uppercaseQuery) === 0);
      };

    };

    function createFilterForUser(query) {
      var lowercaseQuery = angular.lowercase(query);
      return function filterFnUser(user) {
        return (user.name.toLowerCase().indexOf(lowercaseQuery) === 0);
      };

    };





});
