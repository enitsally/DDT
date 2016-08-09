'use strict';


angular
  .module('ddtApp', [
    'ui.router',
    'ngMaterial',
    'angularFileUpload',
    'ngIdle',
    'angularSpinner'
  ])
  .config(['usSpinnerConfigProvider', function (usSpinnerConfigProvider) {
    usSpinnerConfigProvider.setDefaults({radius:30, width:8, length: 16});
  }])
  .config(['KeepaliveProvider', 'IdleProvider', function(KeepaliveProvider, IdleProvider) {
    IdleProvider.idle(1800);//45mins
    IdleProvider.timeout(5);
    KeepaliveProvider.interval(10);
  }])
  .factory('IdleService', function (Idle, Keepalive) {
    //Here start setting the sidle function
    //--------------------------------------------
    var idleservice = {};
    idleservice.started = false;

    idleservice.start = function() {
      Idle.watch();
      idleservice.started = true;
    };

    idleservice.stop = function() {
      Idle.unwatch();
      idleservice.started = false;

    };
    return idleservice;
  })
  .config(function ($urlRouterProvider) {
    $urlRouterProvider.otherwise('/login');
  })
  .config(function ($stateProvider) {
    $stateProvider
      .state('login', {
        url: '/login',
        templateUrl: 'views/login.html',
        controller: 'loginCtrl',
        controllerAs: 'login'
      })
      .state('query_builder', {
        url: '/query_builder',
        templateUrl: 'views/query_builder.html',
        controller: 'queryBuilderCtrl',
        controllerAs: 'queryBuilder'
      })
      .state('query_status', {
        url: '/query_status',
        templateUrl: 'views/query_status.html',
        controller: 'queryStatusCtrl',
        controllerAs: 'queryStatus'
      })
      .state('user_profile', {
        url: '/user_profile',
        templateUrl: 'views/user_profile.html',
        controller: 'userProfileCtrl',
        controllerAs: 'userProfile'
      })
      .state('pattern_builder', {
        url: '/pattern_builder',
        templateUrl: 'views/pattern_builder.html',
        controller: 'patternBuilderCtrl',
        controllerAs: 'patternBuilder'
      })
      .state('metadata_importing', {
        url: '/metadata_importing',
        templateUrl: 'views/metadata_importing.html',
        controller: 'metadataImportingCtrl',
        controllerAs: 'metadataImporting'
      })
      .state('dataset_importing', {
        url: '/dataset_importing',
        templateUrl: 'views/dataset_importing.html',
        controller: 'datasetImportingCtrl',
        controllerAs: 'datasetImporting'
      })
      .state('help', {
        url: '/help',
        templateUrl: 'views/help.html',
        controller: 'helpCtrl',
        controllerAs: 'help'
      })
      ;
  })
.controller('ApplicationController', function ($rootScope, $scope, $mdSidenav, $mdToast, $http, $state) {
  $rootScope.currentUser = null;
  // $rootScope.userRoles = USER_ROLES;

  /**
   * Build handler to open/close a SideNav; when animation finishes
   * report completion in console
   */
  function buildDelayedToggler(navID) {
    return debounce(function() {
      $mdSidenav(navID)
        .toggle()
        .then(function () {
          $log.debug("toggle " + navID + " is done");
        });
    }, 200);
  }

  /**
    * Supplies a function that will continue to operate until the
    * time is up.
    */
   function debounce(func, wait, context) {
     var timer;

     return function debounced() {
       var context = $scope,
           args = Array.prototype.slice.call(arguments);
       $timeout.cancel(timer);
       timer = $timeout(function() {
         timer = undefined;
         func.apply(context, args);
       }, wait || 10);
     };
   }

  $scope.toggleSidenav = function(menuId) {
      $mdSidenav(menuId).toggle();
    };

  $scope.toggleLeft = buildDelayedToggler('left');

  $scope.isOpenLeft = function(){
      return $mdSidenav('left').isOpen();
    };

  $scope.close = function () {
     $mdSidenav('left').close()
       .then(function () {
       });
     };

  $scope.setCurrentUser = function (user) {
         $rootScope.currentUser = user;
       };

  $scope.doDirectPage = function (api){
          if (api === 'Query Builder'){
            $state.go('query_builder');
            $mdSidenav('left').close();
          }
          else if (api === 'Query Status'){
            $state.go('query_status');
            $mdSidenav('left').close();
          }
          else if (api === 'User Profile'){
            $state.go('user_profile');
            $mdSidenav('left').close();
          }
          else if (api === 'Pattern Builder'){
            $state.go('pattern_builder');
            $mdSidenav('left').close();
          }
          else if (api === 'Meta-data Importing'){
            $state.go('metadata_importing');
            $mdSidenav('left').close();
          }
          else if (api === 'Dataset Importing'){
            $state.go('dataset_importing');
            $mdSidenav('left').close();
          }
    };

       $scope.menu = [
             {
               link : '',
               title: 'Query Builder',
               icon: 'images/icon/getfile.svg'
             },
             {
               link : '',
               title: 'Query Status',
               icon: 'images/icon/settings.svg'
             },
             {
               link : '',
               title: 'User Profile',
               icon: 'images/icon/settings.svg'
             }
       ];
       $scope.admin = [
             {
               link : '',
               title: 'Pattern Builder',
               icon: 'images/icon/settings.svg'
             },
             {
               link : '',
               title: 'Meta-data Importing',
               icon: 'images/icon/settings.svg'
             },
             {
               link : '',
               title: 'Dataset Importing',
               icon: 'images/icon/settings.svg'
             }
       ];

  $scope.doGetHelp = function(){
       $state.go('help');
     };

  $scope.doLogout = function(){

          $http.get('http://localhost:5000/logout').then(function(req){
            $scope.showSimpleToast(req.data.status);
          });
           $rootScope.currentUser = null;
           $state.go('login');
           IdleService.stop();
        };

  $scope.doDirectLogin = function(){
        $rootScope.currentUser = null;
        $state.go('login');
      };
})
.controller('LeftCtrl', function ($scope, $timeout, $mdSidenav, $log) {
    $scope.close = function () {
      $mdSidenav('left').close()
        .then(function () {
          $log.debug("close LEFT is done");
        });

    };
})
.run(function($rootScope, $location, $state, $mdDialog) {
    $rootScope.$on('$stateChangeStart', function(e, toState, toParams, fromState, fromParams) {
       var isLogin = toState.name === "login";
       if(isLogin){
          return; // no need to redirect
       }

       // now, redirect only not authenticated

       if($rootScope.currentUser === null) {
           e.preventDefault(); // stop current execution
           $state.go('login'); // go to login
       }
     });

     $rootScope.$on('IdleTimeout', function() {
       var alert =  $mdDialog.alert()
                    .parent(angular.element(document.querySelector('#popupContainer')))
                    .clickOutsideToClose(true)
                    .title('Time out, Session Expired!.')
                    .ok('Got it!');
        $mdDialog.show(alert);
        $state.go('login');
     });
})

;
