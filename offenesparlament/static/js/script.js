/* Author: 

*/

$(document).ready(function() {
  $(".teaser").click(function(e) {
    $(".teaser").hide();
    $(".teaser-fulltext").slideDown('slow');
  });
  $(".teaser-fulltext").click(function(e) {
    $(".teaser-fulltext").slideUp();
    $(".teaser").show();
  });
});






















