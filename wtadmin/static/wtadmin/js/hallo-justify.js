(function() {
    (function(jQuery) {
        return jQuery.widget("IKS.hallojustify1", {
            options: {
                editable: null,
                toolbar: null,
                uuid: '',
                buttonCssClass: null
            },
            populateToolbar: function(toolbar) {
                var buttonize, buttonset,
                _this = this;
                buttonset = jQuery("<span class=\"" + this.widgetName + "\"></span>");
                buttonize = function(alignment) {
                    var buttonElement;
                    buttonElement = jQuery('<span></span>');
                    var just = "justify" + alignment;
                    if(alignment == 'Justify')
                        just = "justifyFull";
                    buttonElement.hallobutton({
                        uuid: _this.options.uuid,
                        editable: _this.options.editable,
                        label: alignment,
                        command: just,
                        icon: "icon-align-" + (alignment.toLowerCase()),
                                              cssClass: _this.options.buttonCssClass
                    });
                    return buttonset.append(buttonElement);
                };
                buttonize("Left");
                buttonize("Center");
                buttonize("Right");
                buttonize("Justify");
                buttonset.hallobuttonset();
                return toolbar.append(buttonset);
            }
        });
    })(jQuery);
    
}).call(this);