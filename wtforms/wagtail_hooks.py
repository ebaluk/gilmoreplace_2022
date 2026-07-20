from __future__ import absolute_import, unicode_literals

from django.urls import include, re_path
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.utils import quote

from wagtail.admin.menu import MenuItem
from wagtail import hooks
from wtforms import urls
from wagtail_modeladmin.options import ModelAdmin, modeladmin_register

from .models import WtForm, get_forms_for_user


from wagtail_modeladmin.helpers import ButtonHelper

class WtFormButtonHelper(ButtonHelper):
     
    def submissions_button(self, pk, classnames_add=[], classnames_exclude=[]):
        classnames = self.edit_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': '/admin/wtforms/submissions/%s/' % quote(pk),
            'label': _('Submissions'),
            'classname': cn,
            'title': _('View Submissions of this %s') % self.verbose_name,
        }
     
    def get_buttons_for_obj(self, obj, exclude=[], classnames_add=[], classnames_exclude=[]):        
        btns = super(WtFormButtonHelper, self).get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)
        pk = quote(getattr(obj, self.opts.pk.attname))
        btns.append(
                self.submissions_button(pk, classnames_add, classnames_exclude)
            )
        
        return btns

class WtFormAdmin(ModelAdmin):
    model = WtForm
    menu_label = _('Forms')
    button_helper_class = WtFormButtonHelper
    #index_template_name = 'wtforms/'
    #menu_icon = FLATMENU_MENU_ICON
    list_display = ('name', 'submissions_size')
    #list_filter = ('site', )
    
    add_to_settings_menu = False


#WtFormAdmin.url_helper = WtFormAdminURLHelper

modeladmin_register(WtFormAdmin)



# @hooks.register('before_serve_page')
# def wagtailmenu_params_helper(page, request, serve_args, serve_kwargs):
#     section_root = request.site.root_page.get_descendants().ancestor_of(
#         page, inclusive=True).filter(depth__exact=SECTION_ROOT_DEPTH).first()
#     if section_root:
#         section_root = section_root.specific
#     ancestor_ids = page.get_ancestors().values_list('id', flat=True)
#     request.META.update({
#         'CURRENT_SECTION_ROOT': section_root,
#         'CURRENT_PAGE_ANCESTOR_IDS': ancestor_ids,
#     })





@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        re_path(r'^wtforms/', include(urls, namespace='wtforms')),
    ]


class WtFormsMenuItem(MenuItem):
    def is_shown(self, request):
        # show this only if the user has permission to retrieve submissions for at least one form
        #return get_forms_for_user(request.user).exists()
        return True


