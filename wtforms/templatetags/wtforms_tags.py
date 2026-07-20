from django import template
from wtforms.models import WtForm
register = template.Library()

@register.inclusion_tag('wtforms/form.html', takes_context=True)
def wtform(context, form_id):
    form = WtForm.objects.get(pk=form_id)
    return {
        'is_popup': False,        
        'self': form,
        'request': context['request'],
    }
