(function($) {

	$.fn.wtform = function(options) {

		// var opts = $.extend( {}, $.fn.iscroller.defaults, options );

		return this.each(function() {

			var WtForm = {
				config : {},
				form : false,

				fn : {

					init : function(form) {
						WtForm.form = $(form);						
						$('.venueselect select', WtForm.form).val($('body').data('venue'));
						WtForm.fn.bindEvents();
						WtForm.fn.init_recaptcha();
					},

					init_recaptcha: function(){
						
						if( window.recaptchaLoaded && typeof grecaptcha !== "undefined"){
							var $reca = $(".wt-recaptcha", WtForm.form);							
							if( $reca.length ){								
								var key = $reca.data("sitekey");								
								var widget_id = $reca.data("widgetId");								
								if( widget_id !== undefined ){
									grecaptcha.reset(widget_id);
								}else{									
									$reca.data("widgetId", grecaptcha.render($reca[0], {  'sitekey' : key }));
									$('.g-recaptcha-response', $reca)
									.attr('aria-hidden', 'true')
									.attr('aria-label', 'do not use')
									.attr('aria-readonly', 'true');
								}
							}
						}
					},
					
					bindEvents : function() {
						WtForm.form.off('submit').on('submit', WtForm.events.submit);
					},

					clearForm : function() {												
						WtForm.form[0].reset();
						$('.venueselect select', WtForm.form).val($('body').data('venue'));
					},

					clearErrors : function() {
						$(".inline-error", WtForm.form).remove();
						$(".alert-danger", WtForm.form).remove();
					}
				},

				events : {

					ajaxBeforeSend : function(xhr, settings) {
						if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain && $.cookie('csrftoken')){
							xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
						}
					},

					submit : function(e) {
						e.preventDefault();
						var $recresp = $('.g-recaptcha-response', WtForm.form);
						if( WtForm.form.data('enableRecaptcha') == 'True' && ( !$recresp.length || !$recresp.val() ) ){
							alert('Please confirm you are not a robot.')

						}else{
							var fd = !!window.FormData ? new FormData(WtForm.form[0]) : WtForm.form.serialize();
							$.ajax({
								url : WtForm.form.attr("action"),
								data : fd,
								dataType : "json",
								processData : false,
								contentType : false,
								type : 'POST',
								success : WtForm.events.submit_success,
								error : WtForm.events.submit_error,
								beforeSend : WtForm.events.ajaxBeforeSend
							});
						}
						
					},

					submit_success : function(data, textStatus, jqXHR) {
						WtForm.fn.clearErrors();
						WtForm.fn.init_recaptcha();
						if ("success" == data.status) {

							if('thank_you_url' in data && data.thank_you_url){
								location = data.thank_you_url;
							}else{
								$(".modal").modal("hide");
								$("#formThanks .modal-body").html(
										data["message_text"]);
								$("#formThanks .modal-title").html(
										data["message_title"]);
								$("#formThanks").modal();
								WtForm.fn.clearForm();
								
								if( data["call_js_on_success"] ){
									eval(data["call_js_on_success"]);
								}
							}								
							
						} else if ("error" == data.status) {
							$(".form-fields-container", WtForm.form)
									.html(data["form_html"]);
						}
						
					},

					submit_error : function(jqXHR, textStatus, errorThrown) {
						$(".errors", WtForm.form).html("Unknown Error. Please reload page and submit form again.");
					}
				}
			};
			
			WtForm.fn.init(this);	
		});
		
			
	};

	

	$(document).ready(function() {
		
		$(".wtform-modal-link").on("click", function(e){
			e.preventDefault();
			var id = $(this).data("wtform");
			var $modal = $(".modal#wt-modal-form-" + id);
			
			if(!$modal.length)
			{
				var tmr = setTimeout(function(){
					global_waiting();
				}, 100);
				
				$.ajax({
					url: "/wtform/"+id+"/",
					type: 'GET',
					success: function(data){
						$modal = $(data).appendTo($("body"));
						$("form.wtform", $modal).wtform();
						$(".widget-dateinput input", $modal).datepicker({autoclose: true});
						$modal.modal().modal("show");
						clearTimeout(tmr);
						global_waiting_stop();
					},
					error: function(jqXHR, textStatus, errorThrown) {
						clearTimeout(tmr);
						global_waiting_stop();
						alert("Unknown Error. Please reload page and try again.");
					}					
				});
			}
			else
			{
				$('.venueselect select', $modal).val($('body').data('venue'));
				$modal.modal("show");	
			}			
		});

		$("form.wtform").each(function() {
			$(this).wtform();
		});
	});
	
}(jQuery));
        
        


