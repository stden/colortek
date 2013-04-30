<script type='text/javascript'>
var fields = [{% for f in G %}"{{ f }}"{% if not forloop.last %}, {% endif %}{% endfor %}];

var find = function(regexp){
    return function(item){
        if (item.search(regexp) != -1) return item;
        return undefined;
    }
}
var skip = function(item){
    return item
}
var getSearchPosition = function(){
    search = document.location.search;
    regular = /[-o]\w+=\d+/;
    filtered_search = search.replace('?', '').split('&');
    block = filtered_search.
        map(find(regular)).filter(skip);
    length = block.length;
    return (length) ? length + 1 : 1;

}
var appendSearch = function(element){
    //console.log(element);
    if (document.location.search)
        document.location.search += "&" + element
    else
        document.location.search += "?" + element
}

var formatTH = function(){
    search = document.location.search;	
    //fields.map(function(item){
	jQuery.map(fields, function(item){
        field = item.replace(/^[-o]{1,2}/, '');
        asc = (item.indexOf('-')  == -1 ) ? true : false;
        th = $("[data-selector=" + field + "]").parents('th');
        th.addClass((asc) ? 'asc' : 'desc');
    });
}

$(document).ready(function(){
    $('.csvLoad').click(function(e){
        if (document.location.search){
            href = String(document.location.href).replace('#', '');
            document.location.href =  href + '&format=csv';
        } else {
            document.location.href += "?format=csv";
            //document.location.reload();
        }
        return false;
    });
    $("a.filter").click(function(e){
		var search_th = '';
        search = document.location.search;
        field = $(this).data('selector');
        reg = new RegExp('[-o]' + field + '=\\d+');
        insearch = search.search(reg);
        if (insearch == -1){
            //appendSearch('-o' + field + '=' + getSearchPosition());
			document.location.search = '?-o' + field + '=1';
        } else {
            reg = new RegExp('[-o]+' + field + "=\\d+");
            if (search.match(reg)[0].indexOf('-') == -1){
                //has not desc ordering -o
                search = search.replace('o' + field, '-o' + field);
				search_th = '-o' + field;
            } else {
                //has descending ordering o
                search = search.replace('-o' + field, 'o' + field);
				search_th = 'o' + field;
            }
            //document.location.search = search;
			document.location.search = '?' + search_th + '=1';
        }
    });
    formatTH();

    //update statuses
    var reloadTotal = function(){
        amount = 0;
        $.each($("td.total"), function(index, item){
            amount += parseFloat($(item).text());
        });
        deliver_cost = parseInt($("#deliver_cost").data('deliver'));
        $("#total_price").text(amount + deliver_cost);
    }

    var updateForm = function(form){
        data = $(form).serialize();
        url = $(form).attr('action');
        submit = $(form).find('input[type=submit]');
        submit.attr({'disabled': "disabled"});
        postFormAjax({
            url: url,
            form: form,
            successMsg: "Успешно сохранено, для просмотра изменений обновите страницу",
            failureMsg: "Что-то пошло не так",
            notyTimeout: 2000,
            reloadPage: false,
            success: function(response){
                submit.removeAttr('disabled');
				var link = window.location.href;
				setTimeout(function(){
					window.location.href = link;
				}, 2000);
            }
        });
    }

    $('body').on('click', '.postAjax', function(e){
        form = $(this).parents('form');
        updateForm(form);		
        return false;
    });
    $("form.ajaxForm").submit(function(e){
        updateForm(this);
        return false;
    });
    $('.quantity.input').change(function(e){
        cost_block = $(this).parents('tr').find('.cost');
        total_block = $(this).parents('tr').find('.total');
        cost = parseInt(cost_block.data('value'));
        rate = parseFloat(cost_block.data('rate'));
        quantity = parseInt($(this).val());
        if (quantity){
            total_block.text((quantity * cost * rate).toFixed(2));
            reloadTotal()
        } else {
            total_block.text("Введите верное значение для количества");
        }
    });
});
</script>
