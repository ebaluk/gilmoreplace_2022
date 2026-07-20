(function ($) {	
    $.fn.wagtail_admin_inline_panel_sorter = function(options){
        var opts = $.extend( {}, $.fn.wagtail_admin_inline_panel_sorter.defaults, options );       
        return this.each(function(){
            var $this = $(this);
            $this.off("click").on("click", function(event){
                event.preventDefault();
                $.fn.wagtail_admin_inline_panel_sorter.createModal($this, opts);
            });
        });    
    };
    
    $.fn.wagtail_admin_inline_panel_sorter.defaults = {
         modalClass: "wagtail-admin-inline-panel-sorter",
         carouselOptions: {interval: false},
         fieldId: '',
         
    };
        
    $.fn.wagtail_admin_inline_panel_sorter.createModal=function($item, opts){        	
    	var modal_id = 'wagtail-admin-inline-panel-sorter';
    	var editor_id = 'wagtail-admin-inline-panel-sorter-editor-panel';
    	var $modal = $("#"+modal_id);        	
    	
    	if( !$modal.length ){
            var $modal = $('<div/>')
            .addClass("modal fade modal-carousel")
            .addClass(opts["modalClass"])
            .attr("tabindex", -1)
            .attr("id", modal_id).append(
           		$('<div/>').addClass("modal-dialog").addClass(opts["modalDialogClass"]).append(
           				
           			$('<div/>').addClass("modal-content").append(
           				$('<header/>').addClass("merged tab-merged").append(
       						$('<div/>').addClass("row nice-padding").append(
       							$('<div/>').addClass("left").append(
       								$('<div/>').addClass("col header-title").append(
       									$('<h1/>').addClass("icon icon-image").html('Sorter')
       								)
       							)
       						)
       					)
       					
           			).append(
           					
       					$('<button/>').addClass("button close icon text-replace icon-cross").attr('type', 'button').attr('data-dismiss', 'modal').html('×')
       					
	       			).append(
	       					
           				$('<div/>').attr('id', editor_id).addClass("wtadmin-sorter-panel")
           				
           			)
           		)	
           	);
    	}
    	
    	var $editor_panel = $('#'+editor_id, $modal);
    	$editor_panel
    	$('>p', $editor_panel).remove();    	    	
    	
    	var field_id = opts["fieldId"];
    	var $fields = $('#'+field_id+'-FORMS');
    	   	
    	
    	var exp = /^[^\-]+-([0-9]+)$/i;
    	
    	var cnt = parseInt($('#'+field_id+'-TOTAL_FORMS').val()); 
    	    	
    	
    	var $items = $('>li:visible', $fields);
    	
    	
    	$items.each(function(){
    		var $li = $(this);
    		var matches = exp.exec($li.attr('id'));
    		if(matches){
        		var idx = matches[1];
        		var title = '';
        		var image = '';
        		
        		
        		
        		$('#'+field_id+'-'+idx+'-title, #'+field_id+'-'+idx+'-caption, #'+field_id+'-'+idx+'-name, #'+field_id+'-'+idx+'-label').each(function(){
        			var $this = $(this);
        			title = $this.val();
        			if(title){        				  
        				return false;
        			}
        		});
        		
        		
        		if(!title){
        			$('.chosen .title', $li).each(function(){
        				var $this = $(this);
            			title = $this.text();            			
            			if(title){        				  
            				return false;
            			}	
        			});
        		}
        		
        		if(!title){
        			title = 'Untitled';
        		}
        		
        		$('.preview-image>img', $li).each(function(){
        			var $this = $(this);
        			image = $this.attr('src');
        			if(image){        				  
        				return false;
        			}
        		});
        		
        		var order = parseInt($('#'+field_id+'-'+idx+'-ORDER').val());
        		
        		var $point = $('<p/>')
        			.addClass('sorter-item')
        			//.attr('title', title)        			
        			.data('idx', idx)        			
        			.appendTo($editor_panel);
        			
        			if(title){
        				$point.append($('<span/>').html(title));
        			}
        			
        			$img = $('<b/>').appendTo($point);
        			if(image){
        				$img.css({backgroundImage: 'url('+image+')'});
        			}
    			}
    		});
    	
    	var sortable = Sortable.create($editor_panel[0], {
    	      animation: 150,
    	      draggable: "p",
    	      ghostClass: "ghost"
    	    });
        
        $modal.modal('show')
        .on('shown.bs.modal', function (e) {
        	$('body>.wrapper').css({overflow: 'hidden'});        	
        })
        .on('hide.bs.modal', function (e) {
        	$('body>.wrapper').css({overflow: 'auto'});
        	$('.sorter-item', $editor_panel).each(function(index){
	    	  var $this = $(this);
	    	  var idx = $this.data('idx');
	    	  $('#'+field_id+'-'+idx+'-ORDER').val(index + 1);
        	});
        	
        	var $items = $('>li:visible', $fields);
        	$items.sort(function(a, b){
        		var a1 = parseInt($('input[name$="-ORDER"]', a).val());
        		var b1 = parseInt($('input[name$="-ORDER"]', b).val());
        		return a1-b1;
        	});
        	
        	
        	$items.detach().appendTo($fields);
        	
        	
        	
        	$items.each(function(i){        	
        		$('ul.controls .inline-child-move-up', this).toggleClass('disabled', i === 0).toggleClass('enabled', i !== 0);
            	$('ul.controls .inline-child-move-down', this).toggleClass('disabled', i === cnt - 1).toggleClass('enabled', i != cnt - 1);
        	});
        	
        	
        });
    };
    
    
    $(function(){
    	$('input[id$="-TOTAL_FORMS"]').each(function(){    		
    		var $this = $(this);
    		var exp = /^([^\-]+)-TOTAL_FORMS$/;
    		var matches = exp.exec($this.attr('id'));
    		if(matches){           		
        		var $fields = $this.closest('.fields');
        		var $a = $('<a/>').attr('href', '#').text('Open Visual Sorter').prependTo($fields);        		
        		$a.wagtail_admin_inline_panel_sorter({fieldId: matches[1]});
    		}	
    	});    	
    	
    });
        
        
}(jQuery));