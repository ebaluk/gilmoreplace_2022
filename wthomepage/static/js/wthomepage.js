(function($) {
	$.fn.bookingWidget = function(options) {
		return this.each(function() {

			var widget = {				


				fn : {

					init : function(form) {
						widget.form = $(form);												
						widget.fn.bindEvents();
						if (!!$.prototype.daterangepicker){      
							$('.book-form-_dates', widget.form).daterangepicker();
						}
					},
					
					bindEvents : function() {
						widget.form.on('submit', widget.events.submit);						
					},

					clearForm : function() {												
						widget.form[0].reset();						
					},

					clearErrors : function() {
						$(".inline-error", widget.form).remove();
						$(".alert-danger", widget.form).remove();
					}
				},

				events : {

					submit : function(e) {                        
                        var r = /([0-9]+)\/([0-9]+)\/([0-9]+) \- ([0-9]+)\/([0-9]+)\/([0-9]+)/,
                            d = r.exec($(".book-form-_dates", widget.form).val()),
                            codeType = $(".book-form-code-type", widget.form).val(),
							promo = $(".book-form-promo", widget.form).val(),
							dateFrom='',
							dateTo='',
							days = 0,
							loc = '';

						if(d){
							dateFrom = moment(d[3]+"-"+d[1]+"-"+d[2]);
							dateTo = moment(d[6]+"-"+d[4]+"-"+d[5]);
							days = dateTo.diff(dateFrom, 'days') ;
						}

						
						if(!d || days < 1){
							e.preventDefault();
							alert('Please select correct Checkin/Checkout dates');
							return;
						}						
                    
						if(codeType == 'corporate'){
							codeType = 'promo';
						}
							
						$(".book-form-checkinDate", widget.form).val(d?d[3]+"-"+d[1]+"-"+d[2]:"");        
						$(".book-form-checkoutDate", widget.form).val(d?d[6]+"-"+d[4]+"-"+d[5]:"");
						$('input.book-form-code', widget.form).remove();
						if(promo){
							$('<input/>').attr('type', 'hidden').addClass('book-form-code').attr('name', codeType).val(promo).appendTo(widget.form);
						}
                        
						
					},
					
				}
			};
			
			widget.fn.init(this);	
		});
		
			
	};

	$(document).ready(function() {
		$(".book-form").each(function() {
            $(this).bookingWidget();
		});
	});
	
}(jQuery));
