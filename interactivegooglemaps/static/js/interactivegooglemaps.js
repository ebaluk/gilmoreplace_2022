(function ($){

	var 
	
	defaults = {
		key: window.GOOGLE_MAP_API_KEY,
		styles: [
            {
              featureType: 'all',
              elementType: 'labels.text.fill',
              stylers: [
                {
                  saturation: 36
                },
                {
                  color: '#9b9b9b'
                },
                {
                  lightness: 40
                }
              ]
            },
            {
              featureType: 'all',
              elementType: 'labels.text.stroke',
              stylers: [
                {
                  visibility: 'off'
                },
                {
                  color: '#000000'
                },
                {
                  lightness: 16
                }
              ]
            },
            {
              featureType: 'all',
              elementType: 'labels.icon',
              stylers: [
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'administrative',
              elementType: 'geometry.fill',
              stylers: [
                {
                  color: '#000000'
                },
                {
                  lightness: 20
                }
              ]
            },
            {
              featureType: 'administrative',
              elementType: 'geometry.stroke',
              stylers: [
                {
                  color: '#000000'
                },
                {
                  lightness: 17
                },
                {
                  weight: 1.2
                }
              ]
            },
            {
              featureType: 'administrative.locality',
              elementType: 'labels.text.fill',
              stylers: [
                {
                  color: '#00a0c4'
                }
              ]
            },
            {
              featureType: 'administrative.locality',
              elementType: 'labels.text.stroke',
              stylers: [
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'administrative.neighborhood',
              elementType: 'labels.text.fill',
              stylers: [
                {
                  color: '#ffffff'
                }
              ]
            },
            {
              featureType: 'landscape',
              elementType: 'geometry',
              stylers: [
                {
                  color: '#232f3d'
                },
                {
                  lightness: '0'
                }
              ]
            },
            {
              featureType: 'poi',
              elementType: 'geometry',
              stylers: [
                {
                  color: '#000000'
                },
                {
                  lightness: 21
                },
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'poi.park',
              elementType: 'all',
              stylers: [
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'poi.school',
              elementType: 'all',
              stylers: [
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'road',
              elementType: 'all',
              stylers: [
                {
                  visibility: 'on'
                }
              ]
            },
            {
              featureType: 'road',
              elementType: 'geometry.fill',
              stylers: [
                {
                  color: '#ffffff'
                }
              ]
            },
            {
              featureType: 'road',
              elementType: 'geometry.stroke',
              stylers: [
                {
                  lightness: '0'
                },
                {
                  color: '#ffffff'
                },
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'road.highway',
              elementType: 'geometry.fill',
              stylers: [
                {
                  color: '#000000'
                },
                {
                  lightness: '0'
                },
                {
                  visibility: 'on'
                }
              ]
            },
            {
              featureType: 'road.highway',
              elementType: 'geometry.stroke',
              stylers: [
                {
                  color: '#000000'
                },
                {
                  lightness: 29
                },
                {
                  weight: 0.2
                }
              ]
            },
            {
              featureType: 'road.highway',
              elementType: 'labels.text.stroke',
              stylers: [
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'road.highway',
              elementType: 'labels.icon',
              stylers: [
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'road.arterial',
              elementType: 'all',
              stylers: [
                {
                  visibility: 'simplified'
                }
              ]
            },
            {
              featureType: 'road.arterial',
              elementType: 'geometry',
              stylers: [
                {
                  color: '#000000'
                },
                {
                  lightness: '0'
                }
              ]
            },
            {
              featureType: 'road.arterial',
              elementType: 'geometry.fill',
              stylers: [
                {
                  lightness: '0'
                },
                {
                  gamma: '1'
                }
              ]
            },
            {
              featureType: 'road.arterial',
              elementType: 'labels.text.stroke',
              stylers: [
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'road.local',
              elementType: 'all',
              stylers: [
                {
                  visibility: 'simplified'
                }
              ]
            },
            {
              featureType: 'road.local',
              elementType: 'geometry',
              stylers: [
                {
                  color: '#000000'
                },
                {
                  lightness: 16
                }
              ]
            },
            {
              featureType: 'transit',
              elementType: 'geometry',
              stylers: [
                {
                  color: '#000000'
                },
                {
                  lightness: 19
                }
              ]
            },
            {
              featureType: 'transit.line',
              elementType: 'all',
              stylers: [
                {
                  visibility: 'simplified'
                },
                {
                  weight: '3'
                }
              ]
            },
            {
              featureType: 'transit.line',
              elementType: 'geometry',
              stylers: [
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'transit.line',
              elementType: 'geometry.fill',
              stylers: [
                {
                  visibility: 'off'
                },
                {
                  color: '#ffb81c'
                }
              ]
            },
            {
              featureType: 'transit.line',
              elementType: 'geometry.stroke',
              stylers: [
                {
                  visibility: 'simplified'
                }
              ]
            },
            {
              featureType: 'transit.line',
              elementType: 'labels',
              stylers: [
                {
                  weight: '1'
                }
              ]
            },
            {
              featureType: 'transit.line',
              elementType: 'labels.icon',
              stylers: [
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'transit.station.airport',
              elementType: 'all',
              stylers: [
                {
                  visibility: 'off'
                }
              ]
            },
            {
              featureType: 'water',
              elementType: 'geometry',
              stylers: [
                {
                  color: '#233f5b'
                },
                {
                  lightness: 17
                }
              ]
            }
          ]
	},
	
	methods = {		
		init: function(options){
			
			var that = this;
			
			var settings = $.extend( {}, defaults, options || {} );
			
			
			
            that.each(function(){		
                var $widget = $(this);
                var locationLatLng = {lat: $widget.data("latitude"), lng: $widget.data("longitude")};
                var defIcon = {
                    path: "M0 0 L22 0 L22 22 L0 22 Z",
                    fillColor: "#611120",
                    fillOpacity: 0,
                    scale: 1.3,
                    origin: new google.maps.Point(20, 20),
                    strokeColor: "white",                    
                    strokeWeight: 4                    
                };
                var icon_name = $widget.data("icon") ? $widget.data("icon") : 'marker-main.svg';
                var icon = {
                    url: '/static/images/'+icon_name, 
                    scaledSize: new google.maps.Size(80, 93)                    
                };
                var zoom = parseInt($widget.data("zoom") || 16);
                var map = new google.maps.Map($('.places-map', $widget)[0], {						    
                    zoom: zoom,
                    scrollwheel: false,
                    center: locationLatLng,
                    clickableIcons: false,
                    styles: $widget.data("styles") ? $widget.data("styles") : settings.styles
                });
                var locationMarker = new google.maps.Marker({
                    position: locationLatLng,
                    map: map,
                    icon: icon,
                    title: $widget.data("title")
                });
                var infoWindow = new google.maps.InfoWindow({
                    content: "holding..."
                });
                var showInfoWindow=function($marker){
                    var content = '<h4>' + $marker.data("title") + '</h4>'
                    if($marker.data("address")){
                        content += '<br/>' + $marker.data("address");
                    }
                    if($marker.data("url")){
                        content += '<br/><br/><a target="_blank" href="'+$marker.data("url")+'">Visit Website</a>';
                    }
                    infoWindow.setContent(content);
                    infoWindow.open(map, $marker[0]);
                };
                var $groups = $('.places-category', $widget);
                
                $groups.each(function(){
                    var color = $(this).data('color');
                    $('.list-group-item', this).each(function(){
                        $place = $(this);
                        var latLng = {lat: $place.data("latitude"), lng: $place.data("longitude")};
                        var marker = new google.maps.Marker({
                            position: latLng,
                            map: map,
                            icon: $.extend( {}, defIcon, {strokeColor: color} ),
                            title: $place.data("title")
                        });
                        marker.setVisible(false);
                        $place.data("marker", marker);
                        $(marker).data({title: $place.data("title"), address: $place.data("address"), url: $place.data("url")});            
                        marker.addListener('click', function() {                            
                            showInfoWindow($(marker));
                        });	
                    });
                });

                $('.list-group-item', $widget).on('click', function(){
                    showInfoWindow($($(this).data('marker')));                    
                });
               

                var resizeTimer;

                var adjustBounds=function(){
                    clearTimeout(resizeTimer);
                    resizeTimer = setTimeout(function(){                        
                        var $items = $('.panel-collapse[aria-expanded="true"] .list-group-item', $widget);                        
                        if( $items.length ){
                            var latlngbounds = new google.maps.LatLngBounds();
                            latlngbounds.extend(locationLatLng);
                            $items.each(function(){
                                var $place = $(this);
                                var marker = $place.data("marker");
                                latlngbounds.extend(marker.position);
                            });
                            map.fitBounds(latlngbounds);
                        }else{
                            map.setCenter( locationLatLng );                            
                            map.setZoom( zoom );
                        }    
                    }, 100);
                };

                $window.on('resize', function(){                    
                    adjustBounds();
                });

                $('.collapse', $groups).on('hide.bs.collapse', function () {                    
                    infoWindow.close();
                    var $collapse = $(this);                    
                    $('.list-group-item', $collapse).each(function(){
                        var $place = $(this);
                        var marker = $place.data("marker");
                        marker.setVisible(false);
                    });
                    adjustBounds();                    
                }).on('show.bs.collapse', function () {                    
                    infoWindow.close();
                    var $collapse = $(this);                    
                    $('.list-group-item', $collapse).each(function(){
                        var $place = $(this);
                        var marker = $place.data("marker");
                        marker.setVisible(true);                       
                    });                    
                    adjustBounds();
                })

                $('.collapse', $groups[0]).trigger('show.bs.collapse');
                
            });			
			
			
			return that;
		}
	};
	
	$.fn.places_widget = function(method){
		return methods.init.apply( this, arguments );
	};
    
	
}(jQuery));