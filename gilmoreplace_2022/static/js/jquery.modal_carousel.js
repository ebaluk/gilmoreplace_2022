(function ($) {

    $.fn.modal_carousel = function(options){
        var opts = $.extend( {}, $.fn.modal_carousel.defaults, options );       
        return this.each(function(){
            var $this = $(this);
            $this.addClass("modal-carousel-source").off("click").on("click", function(event){
                event.preventDefault();
                $.fn.modal_carousel.createModalCarousel($this, opts);
            });
        });    
    };
    
    $.fn.modal_carousel.defaults = {
               showDots: true,
             showArrows: true,
             modalCarouselClass: "modal-carousel-default",
             modalDialogClass: "modal-lg",
             carouselOptions: {interval: false},
        };
        
        $.fn.modal_carousel.createModalCarousel=function($item, opts){
            
            $("#modal-carousel").remove();      

            var $allImages = [];
            
            var $modal = $('<div/>').addClass("modal fade modal-carousel").addClass(opts["modalCarouselClass"]).attr("tabindex", -1)
                    .attr("aria-labelledby", "Modal Carousel").attr("aria-hidden", "true").attr("id", "modal-carousel");
            
            var $modalDialog = $('<div/>').addClass("modal-dialog").addClass(opts["modalDialogClass"]).appendTo( $modal );  
            
            var $close = $("<button/>").addClass("close").attr("type", "button").attr("data-dismiss", "modal").attr("aria-label", "Close").appendTo($modalDialog);      
            var $svg = $('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30" enable-background="new 0 0 30 30" stroke-width="4" stroke="#fff"><line x1="0" y1="0" x2="30" y2="30"></line><line x1="0" y1="30" x2="30" y2="0" ></line></svg>')
                .appendTo($close);
            
            var $modalContent = $('<div/>').addClass("modal-content").appendTo($modalDialog);
            
            var $carousel = $('<div/>').addClass("carousel slide").attr("id", "modal-carousel-carousel").attr("data-ride", "carousel").appendTo($modalContent);
            
            var $carouselInner = $('<div/>').addClass("carousel-inner").appendTo($carousel);
        
            var $items = $(".modal-carousel-source[rel="+$item.attr("rel")+"]:not(.disabled, .icrs_hidden)");         
            var itemIndex = $items.index($item);
            
            var $dots =  $('<ol/>').addClass("carousel-indicators");
            
            if( opts["showDots"] && $items.length > 1 )
            {
                $dots.appendTo($carousel);
            }
            
            if( opts["showArrows"] && $items.length > 1 )
            {       
            	var $cwr = $('<div/>').addClass("carousel-control-wrapper").appendTo($carousel);
                var $left = $('<a/>').attr("href", "#modal-carousel-carousel").attr("aria-hidden", "true").attr("role", "button")
                            .attr("data-slide", "prev").addClass("left carousel-control").appendTo($cwr);
                
                $('<span/>').addClass("glyphicon glyphicon-chevron-left").appendTo($left);
        
                var $right = $('<a/>').attr("href", "#modal-carousel-carousel").attr("aria-hidden", "true").attr("role", "button")
                            .attr("data-slide", "next").addClass("right carousel-control").appendTo($cwr);
                
                $('<span/>').addClass("glyphicon glyphicon-chevron-right").appendTo($right);
            }   
                    
            
            $items.each(function(index){
                var $this = $(this);
                var $dot =  $('<li/>').attr("data-target", "#modal-carousel-carousel").attr("data-slide-to", index).appendTo($dots);
                var $carouselItem =  $('<div/>').addClass("item");
                if( index == itemIndex )
                {
                    $carouselItem.addClass("active");
                    $dot.addClass("active");
                }
                
                var imgSrc = $this.data("img") ? $this.data("img") : $this.attr("href");

                $allImages.push(imgSrc);
                
                var $img = $('<div/>').addClass("image").css({backgroundImage: "url("+imgSrc+")"}).appendTo($carouselItem);
                
                if( $this.data("title") || $this.data("dsc")  )
                {
                	var $caption =  $('<div/>').addClass("carousel-caption").appendTo( $this.data("captionPlacement") == 'img' ? $img : $carouselItem);
                    //var $caption =  $('<div/>').addClass("carousel-caption").appendTo($img);
                    
                    if($this.data("carouselCaptionStyle")){
                    	$caption[0].style = $this.data("carouselCaptionStyle");
                    }
                    
                    if( $this.data("title") )
                    {
                        $('<h2/>').addClass("title").html( $this.data("title") ).appendTo($caption);    
                    }
                    if( $this.data("dsc") )
                    {
                        var is_id_re = /^\#[0-9\-a-z]+$/i;                    	
                        $('<div/>').addClass("dsc").html( 
                       		is_id_re.test( $this.data("dsc") ) ? $($this.data("dsc")).html() : $this.data("dsc") 
           				).appendTo($caption);
                        
                    }
                }
            
                $carouselInner.append($carouselItem);
            });
            
            $carousel.carousel(opts["carouselOptions"]);
            
            if (!!$.prototype.swipe){
            	$carousel.swipe( {
            		swipeLeft:function() {
            			$(this).carousel('next');            		    
            		},
            		swipeRight:function() {
            		    $(this).carousel('prev');
            		}
	        	});
            }       

            
            $.each($allImages, function( idx, value ) {
                $('<img/>').attr('src', value);
            });            
            
            
            $modal.modal('show').on('shown.bs.modal', function(){                
                var $rArrow = $(".carousel-control-wrapper .right", $carousel);
                if($rArrow.length){
                    $rArrow.focus();
                }                
            });
            
        };
        

}(jQuery));