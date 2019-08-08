"use strict";

 angular.module('config', [])

.constant('ENV', {name:'integration',apiEndpoint:['http://192.168.122.223/api/v2'],userManagementEnabled:[true],licenseManagementEnabled:[true]})

;