'use strict';


angular.module('ddtApp')
  .controller('patternBuilderCtrl', function ($log, $timeout, $q, $scope, $rootScope, $http, $state, $mdToast, FileUploader, AUTH_EVENTS, AuthService, IdleService) {

    $scope.search = {
      exp_user : $scope.currentUser ? $scope.currentUser.id : '',
      start_date:'',
      end_date:'',
      conn_keys:[],
      pattern_selected: []
    };

    $scope.ShownPeriod = "3";
    $scope.selectedConnItem = null;
    $scope.selectedConnKey = '';
    $scope.searchText = '';
    $scope.showPopover=false;

    $scope.pattern_type = [];

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
      queueLimit: 1
    }
    );

    $scope.uploader = new FileUploader({
      url:'http://localhost:5000/checkPatternAttachedFile',
      queueLimit: 20
    });

    $scope.patternUploader.filters.push({
      name:'txtFilter',
      fn: function(item, options){
        var name = item.name.split(".")[0]
        var type = item.name.split(".")[1];
        return 'txt'=== type;
      }
    });

    $scope.uploader.filters.push({
      name:'txtFilter',
      fn: function(item, options){
        var name = item.name.split(".")[0]
        var type = item.name.split(".")[1];
        return 'txt'=== type;
      }
    });

    $scope.patternUploader.onSuccessItem  = function(item, response){
      $scope.patternText = response.status ;
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

    $scope.querySearch  = function(query) {
      console.log(query);
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
      console.log(results);
      return results;
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


});
