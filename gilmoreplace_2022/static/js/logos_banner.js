(function ($) {
    'use strict';

    function LogosBanner(element, options) {
        this.element = element;
        this.pageSize = 0;
        this.resizeTimer = null;
        this.animationTimer = null;
        this.slides = [];      
        this.init();
    };

    LogosBanner.constructor = LogosBanner;
    LogosBanner.VERSION = '2026.02.27';
    LogosBanner.DEFAULTS = {};
    LogosBanner.mediaQueryXSmall = window.matchMedia('(min-width: 375px)');    
    LogosBanner.mediaQueryMedium = window.matchMedia('(min-width: 768px)');    
    LogosBanner.mediaQueryLarge = window.matchMedia('(min-width: 1024px)');    
    LogosBanner.mediaQueryXLarge = window.matchMedia('(min-width: 1200px)');    
    LogosBanner.mediaQueryXXLarge = window.matchMedia('(min-width: 1440px)');
    LogosBanner.transitionEndEvents = 'transitionend webkitTransitionEnd oTransitionEnd MSTransitionEnd';

    LogosBanner.prototype.init = function () {
        this.$widget = $(this.element);        
        const that = this;
        const cache = {};
        $('.logo-block', this.$widget).each(function () {
            let el = $(this).detach();
            let elemId = el.attr('data-id');            
            if(!cache[elemId]) {
                cache[elemId] = 1;
                that.slides.push(el);
            }
        });
        this.update();
        this.bindEvents();
    };    

    LogosBanner.prototype.update = function () {
        let that = this;
        let w = that.$widget.width();
        let ps = 2;
        if(LogosBanner.mediaQueryXXLarge.matches) {
            ps = 10;
        }
        else if(LogosBanner.mediaQueryXLarge.matches) {
            ps = 8;
        }
        else if(LogosBanner.mediaQueryLarge.matches) {
            ps = 6;
        }
        else if(LogosBanner.mediaQueryMedium.matches) {
            ps = 4;
        }                        
        else if(LogosBanner.mediaQueryXSmall.matches) {
            ps = 3;
        }                        
        
        
        const $track = $('.logo-track', that.$widget);

        $track.off(LogosBanner.transitionEndEvents);
        $track.css('transition', 'none');
        $track.css('left', '0px');            
        $track.empty();            
        void $track[0].offsetWidth;
        $track.removeAttr('style');

        that.pageSize = ps;    
        let keys = Object.keys(this.slides);            
        let cnt = Math.floor(this.pageSize / keys.length) + 1;
        for(let i = 0; i < cnt; i++) {
            $.each(this.slides, function(idx, slide) {                
                $('.logo-track', this.$widget).append(slide.clone());
            });                
        }
        
        clearTimeout(this.animationTimer);
        that.animationTimer = setTimeout(function () {
            that.animation();    
        }, 300)
                   
        
        
    };

    LogosBanner.prototype.animation = function () {        
        const $track = $('.logo-track', this.$widget);        
        const itemWidth = `-${this.pageSize ? 100 / this.pageSize : 100}vw`; 
        const that = this;               
        
        $track.off(LogosBanner.transitionEndEvents).one(LogosBanner.transitionEndEvents, function(event) {            
            $track.css('transition', 'none');
            $track.css('left', '0px');
            $('.logo-block:first', $track).appendTo($track);
            void $track[0].offsetWidth;
            $track.removeAttr('style');
            that.animation();    
        });                
        
        $track.css('left', itemWidth);
    };

    LogosBanner.prototype.bindEvents = function () {
        var that = this;        
        $(window).on('resize', function () {
            clearTimeout(this.resizeTimer);
            const $track = $('.logo-track', that.$widget);
            $track.off(LogosBanner.transitionEndEvents);
            that.resizeTimer = setTimeout(function () {
                that.update();
            }, 100);
        });        
    };

    function Plugin(option) {
        var that = this;
        var pluginArgs = Array.prototype.slice.call( arguments, 1 );
        return this.each(function () {
          var $this   = $(this);
          var data    = $this.data('logos_banner');
          var options = $.extend({}, LogosBanner.DEFAULTS, $this.data(), typeof option == 'object' && option);
          var action  = typeof option == 'string' ? option : 'update';
          if (!data) $this.data('logos_banner', (data = new LogosBanner(this, options)));
          if( data[action] ){
              data[action].apply( data, pluginArgs );
          }
        })
     }

     var old = $.fn.logos_banner;

     $.fn.logos_banner             = Plugin;
     $.fn.logos_banner.Constructor = LogosBanner;


     // NO CONFLICT
     // ====================

     $.fn.logos_banner.noConflict = function () {
        $.fn.logos_banner = old;
        return this;
     }


    $(function () {
        $('.logos-banner').logos_banner();
    });


})(jQuery);