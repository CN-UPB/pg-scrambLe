SonataApp.controller('ManoSettingsController',['$rootScope','$scope','$routeParams','$location','$http',function($rootScope,$scope, $routeParams, $location, $http){
	
(function(w){w = w || window; var i = w.setInterval(function(){},100000); while(i>=0) { w.clearInterval(i--); }})(/*window*/);
  $scope.new_mano = {};

$scope.post_a_mano = function(){
	var newdata = $scope.new_mano;
	var host = window.location.hostname;
	$http({
          method  : 'POST',
          url     : 'http://'+host+':7001/mano_create',
	  dataType : 'json',	
          headers : { 'Content-Type': 'application/json','Accept':'application/json'},
          data    : newdata
         })
          .then(function successCallback(result){
		$scope.checkmano = result.data;
		$('#new_mano_installed').openModal();
	 });

	},

$scope.getmano = function(){
	var host = window.location.hostname;
	$http({
          method  : 'GET',
          url     : 'http://'+host+':7001/mano',
	  dataType : 'json',	
          headers : {'Content-Type': 'application/json','Accept':'application/json'}
         })
          .then(function successCallback(result){
		$scope.checkmano = result.data;
	 });
   },

$scope.clear = function() {
    $scope.new_mano = null;
}


}]);
