
var app = angular.module('fakebook', ['ngMaterial', 'ngMessages', 'ui-notification','infinite-scroll']);
app.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});