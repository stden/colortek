<script type='text/javascript'> {% load corefilters %}
{% if form.data and form.errors %}
    var form = {
        errors: {
            {% for error in form.errors %}"{{ error }}": ['{{ form.errors|get:error|striptags }}']{% if not forloop.last %},{% endif %}
            {% endfor %}
        }
    }

    fields = { {% for field in form.data %}
        "{{ field }}": "{{ form.data|get:field }}"{% if not forloop.last %},{% endif %}
    {% endfor %}
    }
    var updateFields = function(){
        for (field in fields){
            blk = $("[name=" + field + "]");
            blk.val(fields[field]);
        }

    }
    $(document).ready(function(){
        updateFields();
        form = (typeof form == 'undefined') ? {} : form;
    });
{% endif %}
</script>
