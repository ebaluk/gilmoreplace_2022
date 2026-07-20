$(function(){
	$("#btn-layout-image-points").on('click', function(e){
		e.preventDefault();
		$("#layout-image-points-modal").remove();
		var image_id = $('#id_layout_image').val();		
		var expInt = /([0-9]+)/i;
		image_id = expInt.test(image_id) ? parseInt(image_id) : '0';
		
		$.ajax({
            url: '/wtadmin/interactivemaps/get-image/' + image_id,            
            type: 'get',
            dataType: "json",
            xhrFields: {
                withCredentials: true
            },
            success: function(data){
            	var $modal = $(data['modal']);
            	var $points = $('.points', $modal);
				var i = 0;
				var j = 0;
				var k = 0;
				
				// Wagtail 6.x: Find all inline form items by looking for fields with pattern id_points-N-title
				var $titleFields = $('[id^="id_points-"][id$="-title"]');
				
				$titleFields.each(function(){
					k++;
					if(i>10){
						i = 0;
						j += 32;
					}
					
					// Extract index from field ID (e.g., "id_points-0-title" -> "0")
					var fieldId = $(this).attr('id');
					var matches = /id_points-(\d+)-title/.exec(fieldId);
					
					if(matches){            		
                		var idx = matches[1];
                		var title = $(this).val();
                		var left = $('#id_points-'+idx+'-left').val();
                		var top = $('#id_points-'+idx+'-top').val();
						
						if(!left || left == '0' || left == '0.0' || left == '0,0' || !top || top == '0' || top == '0.0' || top == '0,0'){
							i++;
							left = (32 * i) + 'px';
							top = j + 'px';								
						}else{
							left = left + '%';
							top = top + '%';
						}
						
                		var $point = $('<p/>')
							.html('<span>'+k+'</span>')
                			.addClass('point')
                			.attr('title', title)
                			.css({left: left, top: top})
                			.data('idx', idx)
                			.appendTo($points).draggable({
    					      stop: function() {
    				    	  var p = $(this).position();
    				    	  var idx = $(this).data('idx');
    				    	  var w = $points.width(); 
    				    	  var h = $points.height();
    				    	  
    				    	  if(w && h){    					    		  
    				    		  
	    					    	  var left = p.left * 100 / w;
	    					    	  var top = p.top * 100 / h
	    					    	  
	    					    	  $('#id_points-'+idx+'-left').val(left);
	    		                	  $('#id_points-'+idx+'-top').val(top);
    				    	  }
    				    	  
    					      }
                			});
                		
            			}
            		});
            	
            	$('body').append($modal);
            	
            	// Show modal using plain JavaScript (Bootstrap not available in Wagtail 6.x)
            	$modal.css('display', 'block');
            	$modal.addClass('show');
            	$('body').addClass('modal-open');
            	
            	// Add backdrop
            	$('<div class="modal-backdrop fade show"></div>').appendTo('body');
            	
            	// Close button handler
            	$modal.find('[data-dismiss="modal"]').on('click', function(){
            		$modal.remove();
            		$('.modal-backdrop').remove();
            		$('body').removeClass('modal-open');
            	});
            }
        });
		
	});

});

