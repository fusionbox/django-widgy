$(document).ready(function(){
  
  //|
  //| Mobile Slide-Left Nav
  //|
  $("section.mobile a").bind("touchstart, click", function(event){
    $("body").toggleClass("shift");
    event.preventDefault();
  });
  
});