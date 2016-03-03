(function(angular) {
  // Configuration

  /**
   * @ngdoc interface
   * @name inspireSearchConfiguration
   * @namespace inspireSearchConfiguration
   * @param {service} $provide - Register components with the $injector.
   * @description
   *     Configuration of inspireSearch
   */
  function inspireSearchConfiguration($provide) {
    $provide.decorator('invenioSearchAPI', ['$delegate', function($delegate) {
      // Save the default function
      var searchFn = $delegate.search;
      $delegate.search = function(args) {
        /*
         * Args Object look like:
         *
         *   {
         *      url: ....
         *      method: ....
         *      params: ....
         *   }
         *
         */
        args["headers"] = {
            'Accept': 'application/vnd+inspire.brief+json'
          }
          // Call the original function with the enchanced parameters
        return searchFn(args);
      };
      return $delegate;
    }]);
  }

  // Inject the necessary angular services
  inspireSearchConfiguration.$inject = ['$provide'];

  // Setup configuration
  angular.module('inspireSearch.configuration', [])
    .config(inspireSearchConfiguration);

  // Setup everyhting
  angular.module('inspireSearch', [
    'inspireSearch.configuration',
    'invenioSearch'
  ]);


})(angular);