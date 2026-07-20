$(function(){
	
	$('.slide-big .carousel.slideshow').carousel("pause");
	setTimeout(function(){
		$('.slide-big .carousel.slideshow').carousel("cycle");	
	}, 2000);
		
	setTimeout(function(){
		var bLazy = new Blazy({
			loadInvisible: true,
			selector: '[data-lazyload="true"]',
			validateDelay: 800
		});	
	}, 1000);	
});