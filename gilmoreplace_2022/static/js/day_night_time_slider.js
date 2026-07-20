(function ($) {
    'use strict';

    function DayNightTimeSlider(element, options) {
        this.element = element;
        this.width = 50;
        this.mouseX = 0;       
        this.init();
    };

    DayNightTimeSlider.constructor = DayNightTimeSlider;
    DayNightTimeSlider.VERSION = '2022.06.17';
    DayNightTimeSlider.DEFAULTS = {};

    DayNightTimeSlider.prototype.init = function () {
        this.$widget = $(this.element);
        this.$slide = $('.slide', this.$widget);        
        this.$button = $('.slide-button', this.$widget);        
        
        this.hammer = new Hammer.Manager(this.$button[0]);      
        this.hammer.add( new Hammer.Pan({ direction: Hammer.DIRECTION_HORIZONTAL, threshold: 0 }) );
        this.bindEvents();        
    };    

    DayNightTimeSlider.prototype.panstart = function (e) {
        this.mouseX = e.center.x;
    };

    DayNightTimeSlider.prototype.panmove = function (e) {
        let dx = this.$widget.width() ? (this.mouseX - e.center.x) * 100 / this.$widget.width() : 0;
        this.mouseX = e.center.x;        
        this.width -= dx;
        var w = this.width;
        if(w < 0){
            w = 0;
        }
        else if(w > 100){
            w = 100;
        }
        this.$slide.css('width', w + '%');        
    };

    DayNightTimeSlider.prototype.bindEvents = function () {
        var that = this;
        this.hammer.on("panstart", function (e) {
            that.panstart(e);
        });

        this.hammer.on("panmove", function (e) {
            that.panmove(e);
        });

    };
    

    function Plugin(option) {
        var that = this;
        var pluginArgs = Array.prototype.slice.call( arguments, 1 );
        return this.each(function () {
          var $this   = $(this);
          var data    = $this.data('day_night_time_slider');
          var options = $.extend({}, DayNightTimeSlider.DEFAULTS, $this.data(), typeof option == 'object' && option);
          var action  = typeof option == 'string' ? option : 'update';
          if (!data) $this.data('day_night_time_slider', (data = new DayNightTimeSlider(this, options)));

          if( data[action] ){
              data[action].apply( data, pluginArgs );
          }

        })
     }

     var old = $.fn.day_night_time_slider;

     $.fn.day_night_time_slider             = Plugin;
     $.fn.day_night_time_slider.Constructor = DayNightTimeSlider;


     // NO CONFLICT
     // ====================

     $.fn.day_night_time_slider.noConflict = function () {
        $.fn.day_night_time_slider = old;
        return this;
     }


    $(function () {
        $('.day-night-time-slider').day_night_time_slider();
    });


})(jQuery);