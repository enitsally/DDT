'use strict';


angular.module('ddtApp')
  .controller('datasetImportingCtrl', function ($scope, $http, $state, $mdDialog, $mdToast, $mdMedia,FileUploader) {
    $scope.exp_files = {
      exp_user : $scope.currentUser ? $scope.currentUser.id : '',
      program : '',
      record_mode : '',
      read_only : '',
      exp_type : '',
      project : '',
      tester : '',
      comment : '',
      files: []
    };

    $scope.add_exp_files = {
      exp_user : '',
      exp_no: '',
      files: []
    };

    $scope.search = {
      exp_user : $scope.currentUser ? $scope.currentUser.id : '',
      start_date:'',
      end_date:'',
      s_y: '',
      s_m: '',
      s_d: '',
      e_y: '',
      e_m: '',
      e_d: ''
    };

    $scope.file_log = [];
    $scope.file_user_id = [];
    $scope.add_file_log = [];
    $scope.add_file_user_id = [];
    $scope.ShownPeriod = "3";
    $scope.workFileInfo = [];
    $scope.subExpList = [];
    $scope.delsubExpList = [];

    $scope.showFlag = true;

    var todayDate = new Date();
    $scope.maxDate = new Date(
      todayDate.getFullYear(),
      todayDate.getMonth(),
      todayDate.getDate() + 1
    );
    var originalsubExpList = [];

    $scope.onlyLaterDate = function (date) {
      var day = date;
      return day >= $scope.search.start_date;
    };


    $scope.uploader = new FileUploader({
      url:'http://localhost:5000/checkConnJsonFile',
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

    $scope.add_uploader = new FileUploader({
      url:'/upload$work$file',
      queueLimit: 20
    });

    // $scope.uploader.onBeforeUploadItem = function(item) {
    //   item.formData.push({file_user_id: $scope.file_user_id[item.index-1]});
    //   console.log($scope.file_user_id[item.index-1]);
    //   if ($scope.file_user_id[item.index-1] === undefined){
    //       $scope.uploader.cancelItem(item);
    //   }
    // };

    $scope.add_uploader.onBeforeUploadItem = function(item) {
      item.formData.push({file_user_id: $scope.add_file_user_id[item.index-1]});
    };

    $scope.uploader.onSuccessItem  = function(item, response){
      item.formData.push({format:response.status.format, conn: response.status.conn, msg: response.status.error_msg, conn_key: response.status.conn_key});
      if (response.status.format === true && response.status.conn === true){
        var tmp  = {
          file_name: response.status.file_name,
          file_id : response.status.file_id,
          file_size : item.file.size,
          conn_key : response.status.conn_key
        };
        $scope.file_log.push(tmp);
      } ;

    };

    $scope.add_uploader.onSuccessItem  = function(item, response){
      var tmp  = {
        file_name: response.status.file_name,
        file_id : response.status.file_id,
        file_size : item.file.size,
        file_user_id : item.formData[0].file_user_id
      };
      $scope.add_file_log.push(tmp);
    };

    $scope.uploader.onCompleteAll = function (item, response, status, headers){

      // var confirm = $mdDialog.confirm()
      //     .title('Would you like to confirm your upload')
      //     .ariaLabel('Confirm Dialog')
      //     .ok('Confirm')
      //     .cancel('Cancel');
      // $mdDialog.show(confirm).then(function() {
      //   //Confirm Upload
      //   $scope.exp_files.files = [];
      //   for (var i = 0; i < $scope.file_log.length; i ++){
      //     $scope.exp_files.files.push($scope.file_log[i]);
      //   }
      //
      //   $http.post('/confirm$work$file$upload', $scope.exp_files).then (function (response) {
      //     var msg = response.data.status;
      //     $scope.showSimpleToast(msg);
      //
      //     $scope.doResetInput();
      //
      //   }, function () {
      //   });
      //
      // }, function() {
      //   //Cancal Upload
      //
      //   $http.post('/cancel$work$file$upload', $scope.file_log).then (function (response) {
      //     var msg = response.data.status;
      //     $scope.showSimpleToast(msg);
      //   }, function () {
      //   });
      // });

    };

    $scope.add_uploader.onCompleteAll = function (item, response, status, headers){
      var confirm = $mdDialog.confirm()
          .title('Would you like to confirm adding files to experiment?')
          .ariaLabel('Confirm Dialog')
          .ok('Confirm')
          .cancel('Cancel');
      $mdDialog.show(confirm).then(function() {
        //Confirm Upload
        $scope.add_exp_files.files = [];
        for (var i = 0; i < $scope.add_file_log.length; i ++){
          $scope.add_exp_files.files.push($scope.add_file_log[i]);
        }

        $http.post('/confirm$add$work$file', $scope.add_exp_files).then (function (response) {
          var msg = response.data.status;
          $scope.showSimpleToast(msg);
          $scope.doResetInput();

        }, function () {
        });
        $scope.showFlag = true;
        $scope.onShowPeriodChanged();

      }, function() {
        //Cancal Upload

        $http.post('/cancel$work$file$upload', $scope.add_file_log).then (function (response) {
          var msg = response.data.status;
          $scope.showSimpleToast(msg);
        }, function () {
        });
      });
    };

    $scope.clearAll = function(){
      $scope.uploader.clearQueue();
      $scope.file_log = [];
    };

    $scope.add_clearAll = function(){
      $scope.add_uploader.clearQueue();
      $scope.add_file_log = [];
    };

    $scope.doResetInput = function(){

      $scope.showFlag = true;
      $scope.subExpList = [];
      $scope.uploader.clearQueue();
      $scope.file_user_id = [];
      $scope.file_log = [];

      $scope.add_uploader.clearQueue();
      $scope.add_file_user_id = [];
      $scope.add_file_log = [];

      $scope.exp_files.program = '';
      $scope.exp_files.record_mode = '';
      $scope.exp_files.read_only = '';
      $scope.exp_files.exp_type = '';
      $scope.exp_files.project = '';
      $scope.exp_files.tester = '';
      $scope.exp_files.comment = '';
      $scope.exp_files.files = [];

      $scope.add_exp_files.exp_user = '';
      $scope.add_exp_files.exp_no = '';
      $scope.add_exp_files.files = [];

      $scope.search.start_date = '';
      $scope.search.end_date = '';
      $scope.search.s_y = '';
      $scope.search.s_m = '';
      $scope.search.s_d = '';
      $scope.search.e_y = '';
      $scope.search.e_m = '';
      $scope.search.e_d = '';

    };

    $scope.setIndex = function (index){
      $scope.selectedIndex = index;
    };

    $scope.onShowPeriodChanged = function (){
      $scope.search.start_date = '';
      $scope.search.end_date = '';
      $scope.search.s_y = '';
      $scope.search.s_m = '';
      $scope.search.s_d = '';
      $scope.search.e_y = '';
      $scope.search.e_m = '';
      $scope.search.e_d = '';

      var criteria = {
        shownPeriod: $scope.ShownPeriod,
        exp_user: $scope.currentUser ? $scope.currentUser.id : ''
      };
      $http.post('/get$work$file$summary', criteria).then(function(response){
          $scope.workFileInfo = response.data.status;
      }, function (){

      });
    };

    $scope.doSearchWorkFile = function (){
      if ($scope.search.start_date !== '') {
        $scope.search.s_y = $scope.search.start_date.getFullYear();
        $scope.search.s_m = $scope.search.start_date.getMonth() + 1;
        $scope.search.s_d = $scope.search.start_date.getDate();
      }

      if ($scope.search.end_date !== '') {
        $scope.search.e_y = $scope.search.end_date.getFullYear();
        $scope.search.e_m = $scope.search.end_date.getMonth() + 1;
        $scope.search.e_d = $scope.search.end_date.getDate();
      }
      $http.post('/search$work$file$summary', $scope.search).then(function(response){
          $scope.workFileInfo = response.data.status;
      }, function (){

      });

    };
    $scope.doSaveDataSet = function(){
      //import json tab
      if ($scope.selectedIndex === 1){
        $http.post('http://localhost:5000/saveConnJsonFile', $scope.file_log).then(function(response){
            $scope.result_msg = response.data.status;
            console.log($scope.result_msg);

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


          }, function (){
        });
      };
    };



    $scope.deleteExp = function(exp_user, exp_no){

      var confirm = $mdDialog.confirm()
          .title('Are you sure to delete the entire experiment?')
          .ariaLabel('Confirm Dialog')
          .ok('Confirm')
          .cancel('Cancel');
      $mdDialog.show(confirm).then(function() {
        //Confirm Upload
        var selectedExp = {
          'exp_user': exp_user,
          'exp_no': exp_no
        };

        $http.post('/del$experiment', selectedExp).then(function (response) {
          var msg = response.data.status;
          $scope.onShowPeriodChanged();
          $scope.showSimpleToast(msg);
        }, function(){

        });

      }, function() {
        //Cancal Upload
      });

    };

    $scope.doResetWorkFile = function(){
      $scope.subExpList = originalsubExpList.splice(0);
    };

    $scope.clearDetail = function(){
      if ($scope.showFlag === true){
        originalsubExpList = [];
        $scope.subExpList = [];
      }
    };

    $scope.editSubFile = function(exp_user, exp_no){
      var selectedExp = {
        'exp_user': exp_user,
        'exp_no': exp_no
      };
      $scope.add_exp_files.exp_user = exp_user;
      $scope.add_exp_files.exp_no = exp_no;

      $http.post('/get$sub$exp$detail', selectedExp).then(function (response) {
        $scope.showFlag = false;
        $scope.subExpList = response.data.status;
        originalsubExpList = $scope.subExpList.slice(0);
      }, function(){

      });
    };


    $scope.delFromExp = function(index, exp_user, exp_no, sub_exp){
      var tmp = {
        'exp_user': exp_user,
        'exp_no': exp_no,
        'sub_exp': sub_exp
      };
      if (index >=-1){
        $scope.subExpList.splice(index, 1);
      }
      $scope.delsubExpList.push(tmp);
    }

    $http.get('/get$record$mode').then (function (response) {
      $scope.recordmode_list = response.data.status;
    }, function () {
    });

    $http.get('/get$program').then (function (response) {
      $scope.program_list = response.data.status;
    }, function () {
    });

    $http.get('/get$exp$type').then (function (response) {
      $scope.exp_type = response.data.status;
    }, function () {
    });


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
});
