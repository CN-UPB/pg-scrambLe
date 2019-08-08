SonataApp.controller('ManoSettingsController',['$rootScope','$scope','$routeParams','$location','$http',function($rootScope,$scope, $routeParams, $location, $http){
	
    (function(w){w = w || window; var i = w.setInterval(function(){},100000); while(i>=0) { w.clearInterval(i--); }})(/*window*/);
        $scope.new_vim = {};
      $scope.new_vim.compute_configuration={};
      $scope.new_mano.compute_configuration={};
      $scope.new_vim.networking_configuration={};
      $scope.new_mano.networking_configuration={};
      $scope.new_wim = {};
      $scope.new_mano = {};
    
      $scope.getVimsTries = 0;
      $scope.getWimsTries = 0;
      $scope.getManosTries = 0;
    
    
    $scope.getVimDetails = function(vim){
      $scope.selected_vim = vim;
      $("#vim_details").openModal();
    }
    
    $scope.getWimDetails = function(wim){
      $scope.selected_wim = wim;
      $('#wim_details').openModal();  
    }
    
    $scope.getManoDetails = function(mano){
      $scope.selected_mano = mano;
      $('#mano_details').openModal();  
    }
    
    
    
        $scope.post_a_vim = function(){
            $http({
              method  : 'POST',
              url     : $scope.apis.vims,
              headers : { 'Content-Type': 'application/json','Accept':'application/json' },
              data    : $scope.new_vim
             })
              .success(function(data) {
                $scope.regetVims();  	        
                $('#new_vim_installed').openModal();  
            });	
      }
    
    
      $scope.post_a_wim = function(){
        $http({
              method  : 'POST',
              url     : $scope.apis.wims,
              headers : { 'Content-Type': 'application/json','Accept':'application/json' },
              data    : $scope.new_wim
             })
              .success(function(data) {
              
              console.log(data);
              $('#new_wim_installed').openModal();
                $scope.regetWims();  
              
            });
      }
    
     $scope.post_a_mano = function(){
        $http({
              method  : 'POST',
              url     : $scope.apis.manos,
              headers : { 'Content-Type': 'application/json','Accept':'application/json' },
              data    : $scope.new_mano
             })
              .success(function(data) {
              
              console.log(data);
              $('#new_mano_installed').openModal();
                $scope.regetManos();  
              
            });
      }
        
    
      $scope.regetVims = function(){
        $scope.loading =1;
          
          $http({
              method  : 'GET',
              url     : $scope.apis.vims,
              headers : { 'Content-Type': 'application/json','Accept':'application/json' }
             }).success(function(data) {
                var uuid = data.items.request_uuid;
                setTimeout(function(){
    
                  $http({
                  method  : 'GET',
                  url     : $scope.apis.vims+'/'+uuid,
                  headers : { 'Content-Type': 'application/json','Accept':'application/json'}
                 })
                  .error(function (data, status, headers, config) {
                      $scope.zero_vims = 1;
                      $scope.loading=0;
    
                      if($scope.getVimsTries<5){
                        
                        $scope.getVimsTries++;
                        $scope.regetVims();
    
                      }
    
                      //EDO
                  })
                  .success(function(datamm) {
                    $scope.vims = new Array();
                    $scope.vims=datamm;
                    
    
                    if($scope.vims.length==0){
                      $scope.zero_vims = 1;
                      $scope.loading=0;
                    }else{
                      $scope.vims.forEach(function(vim,index){
                        $scope.setVimStatus(vim);
                        $scope.zero_vims=0;
                        $scope.loading=0;
                      });  
                    }
    
                  });   
    
    
                }, 2500);
    
    
              });
    
      }
    
        $scope.getVims = function(){
          $scope.zero_vims = 0;
          $scope.loading =1;
              $http({
              method  : 'GET',
              url     : $scope.apis.vims,
              headers : { 'Content-Type': 'application/json','Accept':'application/json' }
             }).success(function(data) {
                
                var uuid = data.items.request_uuid;
                setTimeout(function(){
    
                  $http({
                  method  : 'GET',
                  url     : $scope.apis.vims+'/'+uuid,
                  headers : { 'Content-Type': 'application/json','Accept':'application/json'}
                 })
                  .error(function (data, status, headers, config) {
                      $scope.zero_vims = 1;
                      $scope.loading=0;
                      
                      if($scope.getVimsTries<5){
                        
                        $scope.getVimsTries++;
                        $scope.regetVims();
    
                      }
                  })
                  .success(function(datamm) {
                    
                    $scope.vims = new Array();
                    $scope.vims=datamm;
    
                    if($scope.vims.length==0){
                      $scope.zero_vims = 1;
                      $scope.loading=0;
    
                      if($scope.getVimsTries<5){
                        $scope.getVimsTries++;
                        $scope.regetVims();
                      }
    
                    }else{
                      $scope.vims.forEach(function(vim,index){
                        $scope.setVimStatus(vim);
                        $scope.zero_vims=0;
                        $scope.loading=0;
                      });  
                    }
                    
    
                  });   
    
                },2500);
    
    
    
              });
    
    
        }
    
    
      $scope.regetWims = function(){
        
          $scope.zero_wims = 0;
          $scope.loading_wims =1;
    
        $http({
              method  : 'GET',
              url     : $scope.apis.wims,
              headers : { 'Content-Type': 'application/json','Accept':'application/json' }
             }).success(function(data) {
                var uuid = data.items.request_uuid;
                setTimeout(function(){
    
                  $http({
                  method  : 'GET',
                  url     : $scope.apis.wims+'/'+uuid,
                  headers : { 'Content-Type': 'application/json','Accept':'application/json'}
                 }).error(function (data, status, headers, config) {
                      $scope.zero_wims = 1;
                      $scope.loading_wims=0;
    
                      if($scope.getWimsTries<5){                    
                        
                        $scope.getWimsTries++;
                        $scope.regetWims();                    
                      }
                  })
                  .success(function(datamm) {
                    
                    $scope.wims = new Array();
                    $scope.select = {};
                    $scope.select.wims = new Array();
                    
                    $scope.m=datamm;
    
                     if($scope.m.length==0){
                      $scope.zero_wims = 1;
                      $scope.loading_wims=0;
                    }else{
                      $scope.m.forEach(function(wim,index){
                        
                        var x = {};
                        x.uuid = wim.uuid;
                        x.name = wim.name;
                        x.attached_vims = wim.attached_vims;
                        x.status = "-";
                        $scope.wims.push(x);
                        $scope.select.wims.push(x);
    
                      });  
    
                      $scope.zero_wims=0;
                        $scope.loading_wims=0;
                    }
    
                  });   
    
    
                }, 2500);
    
    
              });
      }
    
      $scope.getWims = function(){
    
            $http({
              method  : 'GET',
              url     : $scope.apis.wims,
              headers : { 'Content-Type': 'application/json','Accept':'application/json' }
             }).success(function(data) {
                var uuid = data.items.request_uuid;
                
    
                  $http({
                  method  : 'GET',
                  url     : $scope.apis.wims+'/'+uuid,
                  headers : { 'Content-Type': 'application/json','Accept':'application/json'}
                 }).error(function (data, status, headers, config) {
                      $scope.zero_wims = 1;
                      $scope.loading_wims=0;
    
                      if($scope.getWimsTries<5){                    
                        $scope.getWimsTries++;
                        $scope.regetWims();
                      }
                  })
                  .success(function(datamm) {
                    
                    $scope.wims = new Array();                
                    $scope.m=(datamm?datamm:[]);
                    
                    if($scope.getWimsTries<5 && datamm.length==0){                    
                        $scope.getWimsTries++;
                        $scope.regetWims();
                        
                    }else{
                      
                      if($scope.m.length>0){
                        
                        $scope.m.forEach(function(wim,index){
                      
                          var x = {};
                          x.uuid = wim.uuid;
                          x.name = wim.name;
                          x.attached_vims = wim.attached_vims;
                          x.status = "-";
                          $scope.wims.push(x);
                        }); 
                      }
                                       
                    }               
                    
                    $('select').material_select();                
    
                  });   
    
              });
    
    
      }
    
    
    $scope.regetManos = function(){
        
          $scope.zero_manos = 0;
          $scope.loading_manos =1;
    
        $http({
              method  : 'GET',
              url     : $scope.apis.manos,
              headers : { 'Content-Type': 'application/json','Accept':'application/json' }
             }).success(function(data) {
                var uuid = data.items.request_uuid;
                setTimeout(function(){
    
                  $http({
                  method  : 'GET',
                  url     : $scope.apis.manos+'/'+uuid,
                  headers : { 'Content-Type': 'application/json','Accept':'application/json'}
                 }).error(function (data, status, headers, config) {
                      $scope.zero_manos = 1;
                      $scope.loading_manos=0;
    
                      if($scope.getManosTries<5){                    
                        
                        $scope.getManosTries++;
                        $scope.regetManos();                    
                      }
                  })
                  .success(function(datamm) {
                    
                    $scope.manos = new Array();
                    $scope.select = {};
                    $scope.select.manos = new Array();
                    
                    $scope.m=datamm;
    
                     if($scope.m.length==0){
                      $scope.zero_manos = 1;
                      $scope.loading_manos=0;
                    }else{
                      $scope.m.forEach(function(mano,index){
                        
                        var x = {};
                        x.uuid = mano.uuid;
                        x.name = mano.name;
                        x.status = "-";
                        $scope.manos.push(x);
                        $scope.select.manos.push(x);
    
                      });  
    
                      $scope.zero_manos=0;
                        $scope.loading_manos=0;
                    }
    
                  });   
    
    
                }, 2500);
    
    
              });
      }
    
    
    $scope.getManos = function(){
    
            $http({
              method  : 'GET',
              url     : $scope.apis.manos,
              headers : { 'Content-Type': 'application/json','Accept':'application/json' }
             }).success(function(data) {
                var uuid = data.items.request_uuid;
                
    
                  $http({
                  method  : 'GET',
                  url     : $scope.apis.manos+'/'+uuid,
                  headers : { 'Content-Type': 'application/json','Accept':'application/json'}
                 }).error(function (data, status, headers, config) {
                      $scope.zero_manos = 1;
                      $scope.loading_manos=0;
    
                      if($scope.getManosTries<5){                    
                        $scope.getManosTries++;
                        $scope.regetManos();
                      }
                  })
                  .success(function(datamm) {
                    
                    $scope.manos = new Array();                
                    $scope.m=(datamm?datamm:[]);
                    
                    if($scope.getManosTries<5 && datamm.length==0){                    
                        $scope.getManosTries++;
                        $scope.regetManos();
                        
                    }else{
                      
                      if($scope.m.length>0){
                        
                        $scope.m.forEach(function(mano,index){
                      
                          var x = {};
                          x.uuid = mano.uuid;
                          x.name = mano.name;
                          
                          x.status = "-";
                          $scope.manos.push(x);
                        }); 
                      }
                                       
                    }               
                    
                    $('select').material_select();                
    
                  });   
    
              });
    
    
      }
    
    
        $scope.setVimStatus = function(vim){
            vim.status = '-';
        }
    
    
        $scope.init = function(){
            $scope.getVims();
          $scope.getWims();
        $scope.getManos();
        }
    
         
         $scope.$on("$destroy", function() {
             $scope.wims = [];
             $scope.vims = [];
        $scope.manos = [];
        });
        
    }]);
    