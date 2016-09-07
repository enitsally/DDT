'use strict';


angular.module('ddtApp')
  .controller('patternBuilderCtrl', function ($scope, $rootScope, $http, $state, $mdToast, AUTH_EVENTS, AuthService, IdleService) {

    $scope.search = {
      exp_user : $scope.currentUser ? $scope.currentUser.id : '',
      start_date:'',
      end_date:'',
      conn_keys:[],
      pattern_selected: []
    };

    $scope.ShownPeriod = "3";
    $scope.selectedConnItem = null;
    $scope.selectedConnKey = [];

    $scope.pattern_type = ['SQL','JMP','SAS'];

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
});
