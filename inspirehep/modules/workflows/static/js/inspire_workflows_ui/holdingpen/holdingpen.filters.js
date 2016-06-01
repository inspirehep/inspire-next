(function(angular) {

  function abstractFilter() {
    return function(input) {
      if (input === undefined) {
        return;
      }

      var tagsToReplace = {
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;'
      };

      function replaceTag(tag) {
        return tagsToReplace[tag] || tag;
      }

      var abstract = '';
      for (var i=0; i < input.length; i++) {
        if (input[i].source !== 'arXiv' && input[i].value !== undefined) {
          abstract = input[i].value;
        } else {
          if (input[i].value !== undefined) {
            abstract = input[i].value;
          }
        }
      }
      return abstract.replace(/[&<>]/g, replaceTag);
    };
  }
  angular.module('holdingpen.filters.abstract', ['ngSanitize'])
    .filter('abstract', abstractFilter);
})(angular);
