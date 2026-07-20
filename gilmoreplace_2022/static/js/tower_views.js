(function ($) {
    'use strict';

    function TowerViews(element, options) {
        this.element = element;
        this.positionX = 0;
        this.mouseX = 0;
        this.imageHeight = 0;
        this.imageWidth = 0;
        this.imageViewWidth = 0;
        this.init();
    };

    TowerViews.constructor = TowerViews;
    TowerViews.VERSION = '2022.06.17';
    TowerViews.DEFAULTS = {};

    TowerViews.prototype.init = function () {
        this.$widget = $(this.element);
        this.$view = $('.view', this.$widget);
        this.$select = $('.level-select select', this.$widget);
        this.$pano = $('.pano-block', this.$widget);
        this.hammer = new Hammer(this.$view[0]);
        this.$leftArrow = $('.arrow.left', this.$pano);
        this.$rightArrow = $('.arrow.right', this.$pano);
        this.bindEvents();
        this.selectChange();
    };

    TowerViews.prototype.selectChange = function () {        
        this.$option = $('option:selected', this.$select);
        this.image = this.$option.data('image');
        this.imageHeight = this.$option.data('imageHeight');
        this.imageWidth = this.$option.data('imageWidth');
        this.$view.css('backgroundImage', 'url(' + this.image + ')');
        this.handleImageLoad();
        this.$pano.addClass('active');
    };

    TowerViews.prototype.panstart = function (e) {
        this.mouseX = e.center.x;
    };

    TowerViews.prototype.panmove = function (e) {
        let dx = this.mouseX - e.center.x;
        this.mouseX = e.center.x;
        this.positionX += -(dx * 2);
        this.setBackgroundPositionX();
    };

    TowerViews.prototype.bindEvents = function () {
        var that = this;
        this.hammer.on("panstart", function (e) {
            that.panstart(e);
        });

        this.hammer.on("panmove", function (e) {
            that.panmove(e);
        });

        this.$select.on('change', function () {
            that.selectChange();
        });
        $(window).on('resize', function () {
            that.windowResize();
        });

        this.$leftArrow.on('click', function(){
            that.positionX += 100;
            that.setBackgroundPositionX();
        });
        this.$rightArrow.on('click', function(){
            that.positionX -= 100;
            that.setBackgroundPositionX();
        });

    };

    TowerViews.prototype.setBackgroundPositionX = function () {
        this.$view.css('backgroundPositionX', this.positionX + 'px');
    };

    TowerViews.prototype.getImageViewWidth = function () {
        this.imageViewWidth = this.imageHeight ? (this.$view[0].clientHeight / this.imageHeight) * this.imageWidth : 0;
    };

    TowerViews.prototype.resetPositionX = function () {
        this.positionX = this.imageViewWidth * 0.5 + window.innerWidth * 0.5;
        this.setBackgroundPositionX();
    };

    TowerViews.prototype.handleImageLoad = function () {
        this.getImageViewWidth();
        this.resetPositionX();
    };

    TowerViews.prototype.windowResize = function (e) {
        this.getImageViewWidth(e);
    };
   

    function Plugin(option) {
        var that = this;
        var pluginArgs = Array.prototype.slice.call( arguments, 1 );
        return this.each(function () {
          var $this   = $(this);
          var data    = $this.data('tower_views');
          var options = $.extend({}, TowerViews.DEFAULTS, $this.data(), typeof option == 'object' && option);
          var action  = typeof option == 'string' ? option : 'update';
          if (!data) $this.data('tower_views', (data = new TowerViews(this, options)));

          if( data[action] ){
              data[action].apply( data, pluginArgs );
          }

        })
     }

     var old = $.fn.tower_views;

     $.fn.tower_views             = Plugin;
     $.fn.tower_views.Constructor = TowerViews;


     // NO CONFLICT
     // ====================

     $.fn.tower_views.noConflict = function () {
        $.fn.tower_views = old;
        return this;
     }


    $(function () {
        $('.tower-views-widget').tower_views();
    });


})(jQuery);