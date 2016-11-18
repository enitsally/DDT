'use strict';


angular.module('ddtApp')
  .controller('datasetImportingCtrl', function ($scope, $http, $state, $mdDialog, $mdToast, $mdMedia,FileUploader, $window) {

    $scope.customFullscreen = false;
    $scope.showPopover=false;
    $scope.mapped = false;
    $scope.selectedConnItem = null;
    $scope.selectedConnKey = [];
    // $scope.exp_files = {
    //   exp_user : $scope.currentUser ? $scope.currentUser.id : '',
    //   program : '',
    //   record_mode : '',
    //   read_only : '',
    //   exp_type : '',
    //   project : '',
    //   tester : '',
    //   comment : '',
    //   files: []
    // };

    // $scope.add_exp_files = {
    //   exp_user : '',
    //   exp_no: '',
    //   files: []
    // };

    $scope.search = {
      exp_user : $scope.currentUser ? $scope.currentUser.id : '',
      start_date:'',
      end_date:'',
      conn_keys:[]
    };

    $scope.ShownPeriod = "3";
    $scope.file_log = [];

    // $scope.file_user_id = [];
    // $scope.add_file_log = [];
    // $scope.add_file_user_id = [];
    //
    // $scope.workFileInfo = [];
    // $scope.subExpList = [];
    // $scope.delsubExpList = [];

    $scope.showFlag = true;

    var todayDate = new Date();
    $scope.maxDate = new Date(
      todayDate.getFullYear(),
      todayDate.getMonth(),
      todayDate.getDate() + 1
    );
    // var originalsubExpList = [];

    $scope.onlyLaterDate = function (date) {
      var day = date;
      return day >= $scope.search.start_date;
    };


    $scope.uploader = new FileUploader({
      url:'/checkConnJsonFile',
      queueLimit: 20
    });

    $scope.uploader.filters.push({
      name:'jsonFilter',
      fn: function(item, options){
        var name = item.name.split(".")[0]
        var type = item.name.split(".")[1];
        return 'json'=== type;
      }
    });

    // $scope.add_uploader = new FileUploader({
    //   url:'/upload$work$file',
    //   queueLimit: 20
    // });

    // $scope.uploader.remove = function(item){
    //
    // };

    // $scope.uploader.onBeforeUploadItem = function(item) {
    //   item.formData.push({file_user_id: $scope.file_user_id[item.index-1]});
    //   console.log($scope.file_user_id[item.index-1]);
    //   if ($scope.file_user_id[item.index-1] === undefined){
    //       $scope.uploader.cancelItem(item);
    //   }
    // };

    // $scope.add_uploader.onBeforeUploadItem = function(item) {
    //   item.formData.push({file_user_id: $scope.add_file_user_id[item.index-1]});
    // };

    $scope.uploader.onSuccessItem  = function(item, response){
      item.formData.push({format:response.status.format, conn: response.status.conn, msg: response.status.error_msg, conn_key: response.status.conn_key, key_exist: response.status.key_exist});
      if (response.status.format === true && response.status.conn === true){
        var tmp  = {
          file_name: response.status.file_name,
          file_id : response.status.file_id,
          file_size : item.file.size,
          conn_key : response.status.conn_key,
          key_exist : response.status.key_exist
        };
        $scope.file_log.push(tmp);
      } ;
      if ($scope.save_result === response.status.conn_key ){
        $scope.mapped = true;
      }
    };

    // $scope.add_uploader.onSuccessItem  = function(item, response){
    //   var tmp  = {
    //     file_name: response.status.file_name,
    //     file_id : response.status.file_id,
    //     file_size : item.file.size,
    //     file_user_id : item.formData[0].file_user_id
    //   };
    //   $scope.add_file_log.push(tmp);
    // };

    // $scope.uploader.onCompleteAll = function (item, response, status, headers){
    // };

    // $scope.add_uploader.onCompleteAll = function (item, response, status, headers){
    //   var confirm = $mdDialog.confirm()
    //       .title('Would you like to confirm adding files to experiment?')
    //       .ariaLabel('Confirm Dialog')
    //       .ok('Confirm')
    //       .cancel('Cancel');
    //   $mdDialog.show(confirm).then(function() {
    //     //Confirm Upload
    //     $scope.add_exp_files.files = [];
    //     for (var i = 0; i < $scope.add_file_log.length; i ++){
    //       $scope.add_exp_files.files.push($scope.add_file_log[i]);
    //     }
    //
    //     $http.post('/confirm$add$work$file', $scope.add_exp_files).then (function (response) {
    //       var msg = response.data.status;
    //       $scope.showSimpleToast(msg);
    //       $scope.doResetInput();
    //
    //     }, function () {
    //     });
    //     $scope.showFlag = true;
    //     $scope.onShowPeriodChanged();
    //
    //   }, function() {
    //     //Cancal Upload
    //
    //     $http.post('/cancel$work$file$upload', $scope.add_file_log).then (function (response) {
    //       var msg = response.data.status;
    //       $scope.showSimpleToast(msg);
    //     }, function () {
    //     });
    //   });
    // };

    $scope.clearAll = function(){
      $scope.uploader.clearQueue();
      $scope.file_log = [];
    };

    // $scope.add_clearAll = function(){
    //   $scope.add_uploader.clearQueue();
    //   $scope.add_file_log = [];
    // };

    $scope.doResetInput = function(){

      // $scope.showFlag = true;
      // $scope.subExpList = [];
      $scope.uploader.clearQueue();
      // $scope.file_user_id = [];
      $scope.file_log = [];

      // $scope.add_uploader.clearQueue();
      // $scope.add_file_user_id = [];
      // $scope.add_file_log = [];
      //
      // $scope.exp_files.program = '';
      // $scope.exp_files.record_mode = '';
      // $scope.exp_files.read_only = '';
      // $scope.exp_files.exp_type = '';
      // $scope.exp_files.project = '';
      // $scope.exp_files.tester = '';
      // $scope.exp_files.comment = '';
      // $scope.exp_files.files = [];
      //
      // $scope.add_exp_files.exp_user = '';
      // $scope.add_exp_files.exp_no = '';
      // $scope.add_exp_files.files = [];

      $scope.search.start_date = '';
      $scope.search.end_date = '';
      $scope.search.conn_keys = [];

      $scope.selectedConnKey = [];
      $scope.onShowPeriodChanged();

      $scope.fulllist = [];

      $http.get('/getConnectionShort').then(function (response){
        $scope.fulllist = response.data.status;
      }, function(){

      });



    };

    $scope.setIndex = function (index){
      $scope.selectedIndex = index;
      $scope.onShowPeriodChanged();
    };

    $scope.onShowPeriodChanged = function (){
      $scope.search.start_date = '';
      $scope.search.end_date = '';
      $scope.search.conn_keys = [];

      var criteria = {
        time_range: $scope.ShownPeriod,
        start_date: $scope.search.start_date,
        end_date: $scope.search.end_date
      };
      $http.post('/getConnectionSummary', criteria).then(function(response){
          $scope.connInfo = response.data.status;
      }, function (){

      });
    };

    $scope.doSearchDataSet = function (){
      // if ($scope.search.start_date !== '') {
      //   $scope.search.s_y = $scope.search.start_date.getFullYear();
      //   $scope.search.s_m = $scope.search.start_date.getMonth() + 1;
      //   $scope.search.s_d = $scope.search.start_date.getDate();
      // }
      //
      // if ($scope.search.end_date !== '') {
      //   $scope.search.e_y = $scope.search.end_date.getFullYear();
      //   $scope.search.e_m = $scope.search.end_date.getMonth() + 1;
      //   $scope.search.e_d = $scope.search.end_date.getDate();
      // }
      $scope.search.conn_keys = $scope.selectedConnKey;
      $http.post('/getSearchedConnectionSummary', $scope.search).then(function(response){
          $scope.connInfo = response.data.status;
      }, function (){

      });

    };
    $scope.doSaveDataSet = function(){
      //import json tab
      if ($scope.selectedIndex === 1){
        $http.post('/saveConnJsonFile', $scope.file_log).then(function(response){
            $scope.result_msg = response.data.status;

            var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
            $mdDialog.show({
                  controller: DialogController,
                  templateUrl: 'views/dialog.save.status.html',
                  parent: angular.element(document.body),
                  clickOutsideToClose:true,
                  fullscreen: useFullScreen,
                  locals:{
                    result: $scope.result_msg
                  },
                  scope: $scope,
                  preserveScope: true
                });

            $scope.onShowPeriodChanged();
            $scope.uploader.clearQueue();
            $scope.file_log = [];
            $scope.doResetInput();

          }, function (){
        });
      };
    };

    $scope.doUpdateDataSet = function(){
      //import json tab
      $http.post('/saveConnJsonFile', $scope.file_log).then(function(response){
          $scope.result_msg = response.data.status;
          $scope.mapped = false;
          if ($scope.result_msg){
            $scope.showAlert("Update Succeed.");
            $scope.onShowPeriodChanged();
          }
          else {
            $scope.showAlert("Update Failed.");
          }

          $scope.uploader.clearQueue();
          $scope.file_log = [];

        }, function (){
      });

    };

    $scope.showConnDetail = function (info){
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

    $scope.deleteDS = function(conn_key){

      var confirm = $mdDialog.confirm()
          .title('Are you sure to delete the dataset connection?')
          .ariaLabel('Confirm Dialog')
          .ok('Confirm')
          .cancel('Cancel');
      $mdDialog.show(confirm).then(function() {

        $http.post('/deleteConnectionKey', conn_key).then(function (response) {
          var msg = response.data.status.message;
          $scope.onShowPeriodChanged();
          $scope.showSimpleToast(msg);
        }, function(){

        });

        $scope.doResetInput();

      }, function() {
        //Cancal Upload
      });

    };

    $scope.testDS = function(conn_key){

      $http.post('/testConnectionKey', conn_key).then(function(response){

          if (response.data.status.conn){
            $scope.showAlert("Connection test passed.");
          }
          else{
            $scope.showAlert(response.data.status.error_msg);
          }
      }, function (){

      });

    };

    // $scope.doResetWorkFile = function(){
    //   $scope.subExpList = originalsubExpList.splice(0);
    // };
    //
    // $scope.clearDetail = function(){
    //   if ($scope.showFlag === true){
    //     originalsubExpList = [];
    //     $scope.subExpList = [];
    //   }
    // };

    $scope.editDS = function(conn_key){
      var useFullScreen = ($mdMedia('sm') || $mdMedia('xs'))  && $scope.customFullscreen;
      $mdDialog.show({
            controller: DialogController,
            templateUrl: 'views/dialog.update.conn.info.html',
            parent: angular.element(document.body),
            clickOutsideToClose:false,
            fullscreen: useFullScreen,
            locals:{
              result: conn_key
            },
            scope: $scope,
            preserveScope: true
          });
      $scope.doResetInput();
    };


    // $scope.delFromExp = function(index, exp_user, exp_no, sub_exp){
    //   var tmp = {
    //     'exp_user': exp_user,
    //     'exp_no': exp_no,
    //     'sub_exp': sub_exp
    //   };
    //   if (index >=-1){
    //     $scope.subExpList.splice(index, 1);
    //   }
    //   $scope.delsubExpList.push(tmp);
    // }

    // $http.get('/get$record$mode').then (function (response) {
    //   $scope.recordmode_list = response.data.status;
    // }, function () {
    // });
    //
    // $http.get('/get$program').then (function (response) {
    //   $scope.program_list = response.data.status;
    // }, function () {
    // });
    //
    // $http.get('/get$exp$type').then (function (response) {
    //   $scope.exp_type = response.data.status;
    // }, function () {
    // });


    $scope.showSimpleToast = function(showmgs) {
      $mdToast.show($mdToast.simple().content(showmgs).position('bottom right').hideDelay(1000));
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

    $http.get('/getConnectionShort').then(function (response){
      $scope.fulllist = response.data.status;
    }, function(){

    });

    $scope.transformChip = function (chip){
      if (angular.isObject(chip)) {
        return chip;
      }

    };

    function createFilterFor(query) {
        var lowercaseQuery = angular.lowercase(query);

        return function filterFn(colName) {
          // return (colName.name.toLowerCase().indexOf(lowercaseQuery) === 0) ||
          //     (colName.type.toLowerCase().indexOf(lowercaseQuery) === 0);
          return (colName.toLowerCase().indexOf(lowercaseQuery) === 0);
        };
    };

    $scope.querySearch = function (query) {
        var results = query ?  $scope.fulllist.filter(createFilterFor(query)) : [];
        return results;
      };


});
