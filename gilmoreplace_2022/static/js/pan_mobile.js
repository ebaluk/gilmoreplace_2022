(function ($) {
    'use strict';

    function PanMobile(element, options) {
        this.element = element;
        this.scrollLeft = 0;        
        this.mouseX = 0;        
        this.init();
    };

    PanMobile.constructor = PanMobile;
    PanMobile.VERSION = '2022.08.25';
    PanMobile.DEFAULTS = {};

    PanMobile.prototype.init = function () {
        this.$widget = $(this.element);
        this.$overflowWrapper = $('.overflow-wrapper', this.$widget);        
        this.$overlay = $('.overlay', this.$widget);        
        this.$imageContainer = $('.image-container', this.$widget);        
        this.$image = $('img', this.$imageContainer);
        
        this.hammer = new Hammer(this.$widget[0]);
        this.bindEvents();
    };
    
    PanMobile.prototype.panstart = function (e) {
        this.mouseX = e.center.x;        
        this.$overlay.removeClass('active');        
    };

    PanMobile.prototype.panmove = function (e) {
        let dx = this.mouseX - e.center.x;        
        this.mouseX = e.center.x;
        this.scrollLeft = dx;        
        this.setScrollLeft();
    };

    PanMobile.prototype.bindEvents = function () {
        var that = this;
        this.hammer.on("panstart", function (e) {
            that.panstart(e);
        });

        this.hammer.on("panmove", function (e) {
            that.panmove(e);
        });              

    };

    PanMobile.prototype.setScrollLeft = function () {
        var x = this.$overflowWrapper.scrollLeft() + this.scrollLeft;         
        this.$overflowWrapper.scrollLeft(x);        
    };    
   

    function Plugin(option) {
        var that = this;
        var pluginArgs = Array.prototype.slice.call( arguments, 1 );
        return this.each(function () {
          var $this   = $(this);
          var data    = $this.data('pan_mobile');
          var options = $.extend({}, PanMobile.DEFAULTS, $this.data(), typeof option == 'object' && option);
          var action  = typeof option == 'string' ? option : 'update';
          if (!data) $this.data('pan_mobile', (data = new PanMobile(this, options)));

          if( data[action] ){
              data[action].apply( data, pluginArgs );
          }

        })
     }

     var old = $.fn.pan_mobile;

     $.fn.pan_mobile             = Plugin;
     $.fn.pan_mobile.Constructor = PanMobile;


     // NO CONFLICT
     // ====================

     $.fn.pan_mobile.noConflict = function () {
        $.fn.pan_mobile = old;
        return this;
     }


    $(function () {
        $('.pan-mobile').pan_mobile();
    });


})(jQuery);