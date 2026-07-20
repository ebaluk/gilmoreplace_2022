$(function(){
    var $ir = $('#image-results');
    if( ! $ir.length )
        return;

    $('.listing.images li', $ir).each(function(){
        var $t = $(this);
        var $a = $('>a.image-choice',$t);
        if($a.length){
            var val = $a.attr('href');
            $t.css('position','relative');
            $('<input class="wt-delete-cb" type="checkbox" name="wt_delete_cb" value="'+val+'">').appendTo($t);
        }
    });

    // $(
    //     '<div class="wt-image-controls">'
    //     +'<a class="button js-image-check-all" href="#">Check all</a>'
    //     +'<a class="button js-image-uncheck-all" href="#">Uncheck all</a>'
    //     +'<a class="button js-image-delete" href="#">Delete</a>'
    //     +'</div>'
    // ).insertAfter('#image-results h2');

    $('body').on('click', '.js-image-check-all', function(){
        $('.wt-delete-cb').prop('checked','checked');
    });

    $('body').on('click', '.js-image-uncheck-all', function(){
        $('.wt-delete-cb').prop('checked','');
    });

    $('body').on('click', '.js-image-delete', function(){
        var dt = [];
        var $cb = $('.wt-delete-cb');
        for(var i=0; i<$cb.length; i++){
            if( $($cb[i]).prop('checked') ){
                dt.push( $($cb[i]).val() );
            }
        }
        $.ajax({
            url: '/wtadmin/delete-images/',
            data: {'images':dt},
            type: 'post',
            xhrFields: {
                withCredentials: true
            },
            success: function(data){
                if(data['code']){
                    eval(data['code']);
                }
            }
        });
    });
});