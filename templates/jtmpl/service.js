<script type='text/javascript'>
$(document).ready(function(){
    var alterValue = function(blk, value){
        v = blk.attr('value')/1 + value/1;
        if (v < 1) return false;
        $(blk).attr({'value': v});
        return false;
    }
    /*$("a.plus").click(function(){
       quantity = $(this).parent().find('#id_quantity');
       alterValue(quantity, 1);
    });*/
    /*$("a.minus").click(function(){
        quantity = $(this).parent().find('#id_quantity');
        alterValue(quantity, -1);
    });*/
    $('.orderCheck').click(function(e){
        form = $(this).parents('form');
        $form = $(form);
        data = form.serialize();
        url = form.attr('action');
        src = "{{ kart.service.service_name }}";
        dst = $(form).data('service-name');

        postFormAjax({
            data: data,
            url: url,
            reloadPage: true,
            reloadTimeout: 1000,
            successMsg: "Товар добавлен в корзину",
            success: function(response, code){
                _form = (typeof response.form == 'undefined') ? {} : response.form;
                errors = (typeof _form.errors == 'undefined') ? {} : _form.errors;

                if ("item" in errors){
					//alert(errors['item']);
					jQuery.map(errors['item'], function(itm){
                    //errors['item'].map(function(itm){
                        if (itm == 400){
                            reload = true;
                            noty({
                                text: "Вы пытаетесь положить в корзину товары службы доставки \"" +
                                    dst +
                                    "\". В этом случае товары службы \"" +
                                    src +
                                    "\" будут удалены из корзины.",
                                type: "warning",
                                timeout: false,
                                buttons: [
                                    {
                                        addClass: "success",
                                        text: "Заменить",
                                        onClick: function($noty){
                                            // cart cleanse initiate
                                            $.get('{% url catalog:cart-cleanse %}', function(response){
                                                return $($form).submit();
                                                //$noty.close();
                                            }); // cleanse cart
                                        }//onClick
                                    },
                                    {
                                        addClass: "failure",
                                        text: "Отменить",
                                        onClick: function($noty){
                                            $noty.close();
                                        }//onClick
                                    }
                                ] // buttons
                            }); // noty
                        }
                    }); // errors map
                }
            }
        });
        return false;
    });
});
</script>

