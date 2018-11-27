
var app = angular.module('delhivery', ['ngMaterial', 'ngMessages', 'ui-notification','infinite-scroll']);
app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});