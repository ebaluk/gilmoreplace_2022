var $window = $(window);
var windowHeight = $window.height();
var windowWidth = $window.width();
window.isMenuShowing = true;


var global_waiting = function () {
    if (!$('body>.waiting-wrapper').length) {
        $('body').append('<div class="waiting-wrapper"><i class="waiting fa fa-circle-o-notch fa-spin"></i></div>');
    }
}
var global_waiting_stop = function () { $('.waiting-wrapper').remove(); }

$(function () {

    $('#scroll-down').on('click', function () {
        $('body,html').animate({ scrollTop: $(window).scrollTop() + (windowHeight * 0.95) }, 1000);
    });

    if (!!$.prototype.datepicker) {
        $('.date-pick').datepicker({ autoclose: true });
    }
});

$(function () {
    //iscroller
    if (!!$.prototype.iscroller) {
        $(".iscroller").iscroller().on("iscroller.update.end", function () {
            if (!!$.prototype.modal_carousel) {
                $(".modal-carousel", this).modal_carousel({ modalCarouselClass: "portfolio-modal", showDots: false });
            }
        });
    }
});

$(function () {
    $('.widget-dateinput input').datepicker({
        autoclose: true
    });
});

$(function () {

    $('#formThanks').clone().attr('id', 'formPopup').appendTo('body');

    $('#formPopup').on('show.bs.modal', function (e) {
        var $a = $(e.relatedTarget);
        var $t = $(this);

        if ($a.data('iframe')) {
            var $ih = $('<iframe></iframe>')
                .attr('src', $a.data('iframe'))
                .attr('width', 500)
                .attr('height', 280)
                .css({ 'width': '100%' })
                ;
            $('.modal-body', $t).html($ih);

            if ($a.data('title'))
                $('.modal-title', $t).html($a.data('title'));
        } else {
            $('.modal-body', $t).html($a.attr('href'));
        }
    });
});


$(function () {
    if (!!$.prototype.modal_carousel) {
        $(".modal-carousel").modal_carousel({ modalCarouselClass: "portfolio-modal", showDots: false });
    }
});


$(function () {

    var $youtubeLinks = $('a[href*="youtu.be"], a[href*="youtube.com"]');
    var $vimeoLinks = $('a[href*="vimeo.com"]');

    if ($youtubeLinks.length || $vimeoLinks.length) {

        $('#formThanks').clone().attr('id', 'formEmbedVideo').appendTo('body');
        var $formEmbedVideo = $('#formEmbedVideo');
        $formEmbedVideo.modal({ show: false });

        var showEmbedVideoModal = function (src) {
            $('.modal-body .embed-responsive', $formEmbedVideo).remove();
            var $gm = $("<div/>").addClass("embed-responsive embed-responsive-16by9");
            $('<iframe webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>').addClass('embed-responsive-item').attr('src', src).appendTo($gm);
            $('.modal-body', $formEmbedVideo).append($gm);
            $formEmbedVideo.modal('show');
        };

        $formEmbedVideo.on('hide.bs.modal', function (e) {
            $('.modal-body .embed-responsive', this).remove();
        });

        var youtubeRe = /(youtu\.be\/|youtube.com\/watch\?v=)([a-z_\-0-9]+)/i;
        $youtubeLinks.each(function () {
            var $this = $(this);
            var res = youtubeRe.exec($this.attr('href'));
            if (res) {
                $this.off('click').on('click', function (e) {
                    e.preventDefault();
                    showEmbedVideoModal("https://www.youtube.com/embed/" + res[2] + "?autoplay=1&rel=0");
                });
            }
        });

        var vimeoRe = /(vimeo\.com\/)([0-9]+)/i;
        $vimeoLinks.each(function () {
            var $this = $(this);
            var res = vimeoRe.exec($this.attr('href'));
            if (res) {
                $this.off('click').on('click', function (e) {
                    e.preventDefault();
                    showEmbedVideoModal("https://player.vimeo.com/video/" + res[2] + "?autoplay=1&color=75f703&portrait=0");
                });
            }
        });

    }

});

$(function () { 
    $('.hero-banner').each(function () {
        var $that = $(this);
        var $bg = $('.banner-bg', $that);
        var $video = $('video', $that);
        if($video.length){
            objectFitVideos($video[0]);
            $video[0].addEventListener(
                "ended",
                function () {
                    console.log('video ended');
                    // let vidDuration = this.duration;
                    // this.currentTime = vidDuration - 1;
                    $bg.addClass('active');
                },
                false
            );
        }        
    });
});

$(function () {
    if (window.form_default_email) {
        $('#id_email').val(window.form_default_email);
    }
});

$(function () {
    $(".rich-text a:not([href^='/'])").attr('target', '_blank');
});

$(function () {
    if (!!$.prototype.swipe) {
        $('.carousel').swipe({
            swipeLeft: function () {
                $(this).carousel('next');
            },
            swipeRight: function () {
                $(this).carousel('prev');
            }
        });
    }
});

$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});

$(function () {
    $('[data-preload-image]').each(function () {
        var img = $(this).data('preloadImage');
        if (img) {            
            $.each(img.split(" "), function(i, v){
                $('<img/>').attr('src', v);
                // console.log('Preload: ' + v);
            });            
        }
    });
});



$(function () {
    var $collageGallery = $('.gallery-type-flex');
    if ($collageGallery) {
        if (!!$.prototype.modal_carousel) {
            $(".modal-carousel", $collageGallery).modal_carousel({ modalCarouselClass: "portfolio-modal", showDots: false });
        }
        var items = [];
        var add_gallery_item = function (item, cnt) {
            $('.grid', $collageGallery).append(
                $('<a/>')
                    .attr('href', item.href)
                    .addClass('modal-carousel square' + (cnt > 12 ? ' hidden' : ''))
                    .data('cat', item.cat)
                    .data('id', item.id)
                    .data('title', item.title)
                    .attr('rel', 'home-photos').append(
                        $('<span/>').css('background-image', 'url(' + item.thumbnail + ')')
                    )
            );
        };

        $(".btn-view-more", $collageGallery).on('click', function (e) {
            e.preventDefault();
            $('.grid>a.hidden', $collageGallery).removeClass('hidden');
            $(this).hide();
        });

        $('.grid>a', $collageGallery).each(function () {
            var $this = $(this);
            items.push({
                thumbnail: $this.data('thumbnail'),
                href: $this.attr('href'),
                id: $this.data('id'),
                title: $this.data('title'),
                cat: $this.data('cat')
            });
        });


        $('.gallerywc-navbar [data-cat]').on('click', function (e) {
            e.preventDefault();
            $('.grid>a', $collageGallery).remove();
            $('.grid', $collageGallery).addClass('preview');
            var cnt = 0;
            var $this = $(this);
            var cat = $this.data('cat');
            $('.gallerywc-navbar > li').removeClass('active');
            $this.closest('li').addClass('active');

            if (cat == 'all') {
                $.each(items, function (k, v) {
                    cnt++;
                    add_gallery_item(v, cnt);
                });
            } else {
                var tmp_items = [];
                $.each(items, function (k, v) {
                    if (v.cat[cat] !== undefined) {
                        tmp_items.push(v);
                    }
                });

                tmp_items.sort((a, b) => (a.cat[cat] > b.cat[cat]) ? 1 : ((b.cat[cat] > a.cat[cat]) ? -1 : 0))
                $.each(tmp_items, function (k, v) {
                    cnt++;
                    add_gallery_item(v, cnt);
                });

            }
            

            // if (cnt > 12) {
            //     $(".btn-view-more", $collageGallery).show();
            // } else {
            //     $(".btn-view-more", $collageGallery).hide();
            // }

            if (!!$.prototype.modal_carousel) {
                $(".modal-carousel", $collageGallery).modal_carousel({ modalCarouselClass: "portfolio-modal", showDots: false });
            }
        });
    }

});



$(function () {
    //let $items = $('#filterGroup, #app>nav');
    let $body = $('body');
    let handleScroll = function () {
        let transparentTop = $('#app>.transparent')[0].offsetTop;
        let windowScroll = window.pageYOffset;
        if (transparentTop < windowScroll + 70) {
            $body.addClass('hide-nav');
        } else {
            $body.removeClass('hide-nav');
        }
    };
    $(window).on('scroll', function () {
        handleScroll();
    });

    $('nav .btn-menu, nav .hamburger').on('click', function (e) {
        e.preventDefault();
        $body.addClass('slideUp hide-nav');
    });

    $('.menu .close').on('click', function (e) {
        e.preventDefault();
        $body.removeClass('slideUp');
        handleScroll();
    });

    $('.scroll-down-icon').on('click', function (e) {
        e.preventDefault();
        window.scrollTo({
            top: window.innerHeight,
            behavior: "smooth"
        });
    });


});

$(function () {

    let $filterWrapper = $('#filterWrapper');

    if ($filterWrapper.length) {

        let $body = $('body');
        let stickPoint = $filterWrapper[0].offsetTop - 60;

        let handleScroll = function () {
            let elTop = $filterWrapper[0].offsetTop;
            let offset = window.pageYOffset;
            let distance = elTop - offset;
            if (distance <= 0 && !$body.hasClass('page-nav-fixed')) {
                $body.addClass('page-nav-fixed');
            } else if ($body.hasClass('page-nav-fixed') && offset <= stickPoint) {
                $body.removeClass('page-nav-fixed');
            }
        };

        $(window).on('scroll', function () {
            handleScroll();
        }).on('resize', function () {
            stickPoint = $filterWrapper[0].offsetTop - 60;
        });
    }

});


$(function () {
    $('.sitemap-section').each(function () {
        let $this = $(this);
        $('.sitemap-desktop .hotspot', $this).on('mouseover', function () {
            $(this).addClass('active');
            $('.sitemap-desktop .callout[data-idx="' + $(this).data('idx') + '"]', $this).addClass('active');
            $('.sitemap-desktop .overlay', $this).addClass('active');
        }).on('mouseleave', function () {
            $(this).removeClass('active');
            $('.sitemap-desktop .callout, .sitemap-desktop .overlay', $this).removeClass('active');
        });

        $('.sitemap-mobile .hotspot-mobile', $this).on('click', function () {
            $(this).addClass('active');
            $('.sitemap-mobile .mobile-callout', $this).addClass('active');
            $('.sitemap-mobile .mobile-callout > div', $this).html(
                $('.sitemap-desktop .callout[data-idx="' + $(this).data('idx') + '"]', $this).html()
            );
        });

        $('.sitemap-mobile .mobile-callout', $this).on('click', function () {
            $('.sitemap-mobile .hotspot-mobile, .sitemap-mobile .mobile-callout', $this).removeClass('active');
        });
    });
});

// $(function () {
//     $('.pan-mobile').each(function () {
//         let $this = $(this);
//         $('.overlay', $this).on('touchstart click', function () {
//             $(this).removeClass('active');
//         });
//     });
// });

$(function () {
    $('.video-block').each(function () {
        let $this = $(this);
        $this.on('click', function () {
            if (!$this.data('isPlaying')) {
                $('video', $this)[0].play();
                $this.data('isPlaying', true);
            }
            else {
                $('video', $this)[0].pause();
                $this.data('isPlaying', false);
            }
        });
    });
});

$(function () {
    $('.section-plans').each(function () {
        let $this = $(this);
        $('.select-box select', $this).on('change', function () {
            $('.appartment-type').removeClass('active');
            $('.appartment-type[data-apartment-type="'+$(this).val()+'"]').addClass('active');
        });

        $('.list-container .card:not(.sold)', $this).on('click', function () {
            let $card = $(this);
            let kpImages = $card.data('floorplatesImages');
            let kpImagesLength = kpImages.length;            
            let $kpItems = $('#apartment-keyplates-desktop .kp-items', $this);
            $("section.pages").css('zIndex', 9999);
            $("#filterGroup").css('zIndex', -1000);
            $('.overlay', $this).addClass('active').attr('data-cnt', kpImagesLength);

            $('#apartment-title', $this).text($card.data('title'));
            $('#apartment-type', $this).text($card.data('apartmentType'));
            $('#apartment-int', $this).text($card.data('interiors'));
            $('#apartment-ext', $this).text($card.data('exteriors'));

            if($card.data('pdf')){
                $('#apartment-pdf-desktop', $this).attr('href', $card.data('pdf')).removeClass('hidden');                
            }
            else
            {
                $('#apartment-pdf-desktop', $this).addClass('hidden');                
            }

            if(kpImagesLength){                
                $kpItems.empty();                
                $.each(kpImages, function( index, value ) {       
                    console.log(value);
                    $kpItems.append($('<img/>').attr('src', value));
                });
                $('#apartment-keyplates-desktop', $this).removeClass('hidden');                
            }            
            else
            {
                $('#apartment-keyplates-desktop', $this).addClass('hidden');                
            }

            if($card.data('floorplanImage')){
                $('#apartment-floorplan', $this).css({'backgroundImage': 'url('+ $card.data('floorplanImage')+')'}).removeClass('hidden').addClass($card.data('layout'));
            }
            else
            {
                $('#apartment-floorplan', $this).removeAttr('style').removeClass('horizontal vertical').addClass('hidden');
            }

        });

        $('.overlay .close', $this).on('click', function () {
            $("section.pages").css('zIndex', 100);            
            setTimeout(function(){
                $("#filterGroup").css('zIndex', 1000);
              }, 333);
            $('.overlay', $this).removeClass('active');            
        });

    });
});

$(function () {
    $('.penthouses-widget').each(function () {
        let $this = $(this);
        $('.select-box select', $this).on('change', function () {
            $('.tower-item, .penthouse', $this).removeClass('active');            
            $('.tower-item.'+$(this).val()+', .penthouse.'+$(this).val(), $this).addClass('active');            
        });
        
        $('input[data-tower-id]', $this).on('change', function () {
            console.log('$(this)');
            var $btn = $(this);            
            var $tower = $('.tower-item[data-tower-id="'+$btn.data('tower-id')+'"]', $this);            
            if($btn.prop('checked')){
                $tower.addClass('in');
            }else{
                $tower.removeClass('in');
            }            
        });

        $('.view-floor-plan', $this).on('click', function () {
            let $card = $(this).closest('.penthouse');
            let kpImages = $card.data('floorplatesImages');
            let kpImagesLength = kpImages.length;            
            let $kpItems = $('#apartment-keyplates-desktop .kp-items', $this);
            $("section.pages").css('zIndex', 9999);
            $("#filterGroup").css('zIndex', -1000);
            $('.overlay', $this).addClass('active').attr('data-cnt', kpImagesLength);

            $('#apartment-title', $this).text($card.data('title'));
            $('#apartment-type', $this).text($card.data('apartmentType'));
            $('#apartment-int', $this).text($card.data('interiors'));
            $('#apartment-ext', $this).text($card.data('exteriors'));
            $('#apartment-total', $this).text($card.data('total'));

            if($card.data('pdf')){
                $('#apartment-pdf-desktop', $this).attr('href', $card.data('pdf')).removeClass('hidden');                
            }
            else
            {
                $('#apartment-pdf-desktop', $this).addClass('hidden');                
            }

            if(kpImagesLength){                
                $kpItems.empty();                
                $.each(kpImages, function( index, value ) {       
                    console.log(value);
                    $kpItems.append($('<img/>').attr('src', value));
                });
                $('#apartment-keyplates-desktop', $this).removeClass('hidden');                
            }            
            else
            {
                $('#apartment-keyplates-desktop', $this).addClass('hidden');                
            }

            if($card.data('floorplanImage')){
                $('#apartment-floorplan', $this).css({'backgroundImage': 'url('+ $card.data('floorplanImage')+')'}).removeClass('hidden').addClass($card.data('layout'));
            }
            else
            {
                $('#apartment-floorplan', $this).removeAttr('style').removeClass('horizontal vertical').addClass('hidden');
            }

        });

        $('.overlay .close', $this).on('click', function () {
            $("section.pages").css('zIndex', 100);            
            setTimeout(function(){
                $("#filterGroup").css('zIndex', 1000);
              }, 333);
            $('.overlay', $this).removeClass('active');            
        });

    });
});

// $(function () {
//     $('.tower-views-widget').each(function () {
//         let $widget = $(this);
//         let $view = $('.view', $widget);
//         let positionX = 0;
//         let mouseX = 0;
//         let imageHeight = 0;
//         let imageWidth = 0;
//         let imageViewWidth = 0;

//         let setBackgroundPositionX = function() {            
//             $view.css('backgroundPositionX', positionX + 'px');            
//         };

//         let getImageViewWidth = function() {            
//             imageViewWidth = imageHeight ? ($('.view', $widget)[0].clientHeight / imageHeight) * imageWidth : 0;            
//         };
//         let resetPositionX = function() {
//             positionX = imageViewWidth * 0.5 + window.innerWidth * 0.5;
//             setBackgroundPositionX(positionX);            
//         };
//         let handleImageLoad = function() {
//             getImageViewWidth();            
//             resetPositionX();            
//         };
        
        
//         $('.level-select select', $widget).on('change', function () {
//             let $option = $('option:selected', this);            
//             let image = $option.data('image');
//             imageHeight = $option.data('imageHeight');
//             imageWidth = $option.data('imageWidth');
//             $('.view', $widget).css('backgroundImage', 'url('+image+')');
//             handleImageLoad();
//             $('.pano-block', $widget).addClass('active');            
//         }).trigger('change');

//         var mc = new Hammer($('.view', $widget)[0]);        
        
//         mc.on("panstart", function(e) {
//             mouseX = e.center.x;            
//         });
        
//         mc.on("panmove", function(e) {            
//             let dx = mouseX - e.center.x;
//             mouseX = e.center.x;
//             positionX += -(dx * 2);
//             setBackgroundPositionX();                            
//         });
        

//         $(window).on('resize', function () {
//             getImageViewWidth();
//         });
        

//     });
// });


// const swiper = new Swiper('.logos-banner .swiper', {
//   loop: true,
//   speed: 5000,
//   autoplay: {
//     delay: 0,
//     disableOnInteraction: false,
//     pauseOnMouseEnter: false,
//     // reverseDirection: false,
//     // stopOnLastSlide: false,
//     waitForTransition: false
//   },  
//   watchOverflow: true,
//   allowTouchMove: false,
//   slideToClickedSlide: false,
//   slidesPerView: 5, // Or a specific number
//   slidesPerGroup: 5,
// //   freeMode: true,
//   spaceBetween: 20
// });