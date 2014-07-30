$(document).ready(function(){
  
  //|
  //| Scroll-Based Functions
  //|
  var headerHeight = $("header").height();
  var arbitrarySpacer = 300;
  
  function runAtScrollPosition() {
    var distanceFromTop = $(window).scrollTop();
    
    // if we've scrolled past the header
    if (distanceFromTop >= headerHeight - 25) {
      $("body").addClass("bop-it");
    }
    else {
      $("body").removeClass("bop-it");
    }
  }

  var throttled = _.throttle(runAtScrollPosition, 100);
  $(window).delay(3000).scroll(throttled);
  
  //|
  //| Mobile Slide-Left Nav
  //|
  $("section.mobile a").bind("touchstart, click", function(event){
    $("body").toggleClass("shift");
    event.preventDefault();
  });
  
});