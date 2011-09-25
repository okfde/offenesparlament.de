/* Author: 

*/

$(document).ready(function() {
  $(".teaser").click(function(e) {
    $(".teaser").hide();
    $(".teaser-fulltext").slideDown('slow');
  });
  $(".teaser-fulltext").click(function(e) {
    $(".teaser").show();
    $(".teaser-fulltext").hide();
  });
});






















