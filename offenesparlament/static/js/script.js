/* Author: 

*/

$(document).ready(function() {
  $(".bio-teaser").click(function(e) {
    $(".bio-teaser").hide();
    $(".bio-fulltext").slideDown('slow');
  });
  $(".bio-fulltext").click(function(e) {
    $(".bio-teaser").show();
    $(".bio-fulltext").hide();
  });
});






















