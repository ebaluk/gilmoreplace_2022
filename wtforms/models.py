from django.utils.deprecation import MiddlewareMixin
from wagtail.contrib.forms.models import AbstractEmailForm
import json
import os
import re
import uuid
import requests
import traceback
import threading

from django.contrib.contenttypes.models import ContentType

from django.db import models
from django.conf import settings as system_settings

from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from unidecode import unidecode

from wagtail.models import Page, Orderable, Collection, get_page_models
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel

from wagtail.documents.models import Document
from modelcluster.fields import ParentalKey
from wagtail.snippets.models import register_snippet

# WT
from wtadmin.models import WtSettings
from wtpages.headless import NextHeadlessPreviewMixin

from django.core.mail.backends.smtp import EmailBackend

from django.core.serializers.json import DjangoJSONEncoder
from wagtail.admin.mail import send_mail
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache

from .forms import WtFormBuilder, WagtailAdminWtFormPageForm

import random

from modelcluster.models import ClusterableModel
from django.utils.safestring import mark_safe

from wagtail.fields import StreamField

from wtforms.blocks import WTFORMS_BLOCKS, iter_form_field_blocks, FormFieldBlockAdapter


from .fields import WtFileField, WtGroupField
from django.template.defaultfilters import default


def random_digit_challenge():
    ret = u''
    for _ in range(4):
        ret += str(random.randint(0, 9))
    return ret, ret


class DisableCSRF(MiddlewareMixin):
    def process_request(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)


COLLECTION_NAME = 'Form Submissions'

FORM_FIELD_CHOICES = (
    ('singleline', _('Single line text')),
    ('multiline', _('Multi-line text')),
    ('email', _('Email')),
    ('number', _('Number')),
    ('url', _('URL')),
    ('checkbox', _('Checkbox')),
    ('checkboxes', _('Checkboxes')),
    ('dropdown', _('Drop down')),
    ('radio', _('Radio buttons')),
    ('date', _('Date')),
    ('time', _('Time')),
    ('datetime', _('Date/time')),
    ('captcha', _('Captcha')),
    ('file', _('File')),
    ('fieldsgroup', _('Fields Group')),
    ('sectiontitleh2', _('Section Title H2')),
    ('sectiontitleh3', _('Section Title H3')),
    # ('stateselect', _('US State Select')),
    # ('countryselect', _('Country Select')),
    # ('dropdown2', _('Drop down (two drop downs)')),
    # ('venueselect', _('Venue Select')),
)


def lasso_add(url, api_key, data, cond_rotations):

    def _lasso_add(rid=None):
        if rid:
            data['rotationId'] = rid
        try:
            r = requests.post(
                url,
                json=data,
                headers={"Authorization": "Bearer %s" % api_key},
            )

            try:
                with open("/tmp/lasso.log", "a") as fl:
                    fl.write(json.dumps(data))
                    fl.write(r.text)
            except:
                pass

        except:
            traceback.print_exc()

    if cond_rotations:
        for rotation_id, _ in cond_rotations.items():
            _lasso_add(rid=rotation_id)
    else:
        _lasso_add()


# def salesforce_add(url, data):
#     try:
#         r = requests.post(url, data=data, )
#         #print(url, data, r.text)
#     except:
#         traceback.print_exc()


# def revinate_add(url, data):
#     try:
#         r = requests.post(url, json=data, )
#         #print(url, data, r.text)
#     except:
#         traceback.print_exc()

class WtFormLassoListItems(Orderable):
    list = ParentalKey('WtFormLassoList', related_name='list_items')
    title = models.CharField(max_length=255)
    lasso_id = models.IntegerField(db_index=True)
    panels = [
        FieldPanel('title'),
        FieldPanel('lasso_id'),
    ]


@register_snippet
class WtFormLassoList(ClusterableModel):
    QUESTION_TYPE_CHOICES = (
        ('checkbox', 'checkbox'),
        ('text', 'text'),
        ('single_select', 'single_select'),
        ('multi_select', 'multi_select'),
        ('date', 'date'),
    )

    class Meta:
        verbose_name = 'Form Lasso Question'
        ordering = ['title']

    title = models.CharField(max_length=255)
    lasso_id = models.IntegerField(db_index=True)
    field_type = models.CharField(
        max_length=20, default='checkbox', choices=QUESTION_TYPE_CHOICES)

    def __str__(self):
        return self.title

    panels = [
        MultiFieldPanel([
            FieldPanel('title', classname="title"),
            FieldPanel('lasso_id'),
            FieldPanel('field_type'),
        ], heading=_('Basic')),
        MultiFieldPanel([InlinePanel('list_items',),],
                        heading='List Items', classname="collapsible collapsed-no"),
    ]


class WtAbstractFormField(Orderable):
    # SALESFORCE_FIELD_TYPE_CHOICES = (
    #     ('regular', 'Regular'),
    #     ('array', 'Array'),
    # )
    # TITLE_TAG_NAME_CHOICES = (
    #     ('div', 'DIV'),
    #     ('h2', 'H2'),
    #     ('h3', 'H3'),
    # )

    label = models.TextField(
        verbose_name=_('label'),
        # max_length=255,
        help_text=_('The label of the form field')
    )
    show_label = models.BooleanField(default=True)
    field_type = models.CharField(verbose_name=_(
        'field type'), max_length=16, choices=FORM_FIELD_CHOICES)
    required = models.BooleanField(verbose_name=_('required'), default=True)
    choices = models.TextField(
        verbose_name=_('choices'),
        blank=True,
        help_text=_(
            'New line separated list of choices. Only applicable in checkboxes, radio and dropdown.')
    )
    # choices2 = models.TextField(
    #     verbose_name=_('choices 2'),
    #     blank=True,
    #     help_text=_('New line separated list of choices. Only applicable in Drop Down (two drop downs).')
    # )

    lasso_question_list = models.ForeignKey('WtFormLassoList', null=True, blank=True,
                                            related_name='+', on_delete=models.SET_NULL, verbose_name=_('Lasso Question'))
    lasso_field_name = models.CharField(max_length=255, blank=True, null=True)
    # lasso_question_id = models.CharField(max_length=255, blank=True, null=True)
    # lasso_field_is_array = models.BooleanField(default=False, )

    # revinate_value_based_names = models.TextField(
    #     blank=True,
    #     help_text=_('New line separated list of choices. Only applicable in checkboxes, radio and dropdown.')
    # )
    default_value = models.CharField(
        verbose_name=_('default value'),
        max_length=255,
        blank=True,
        help_text=_(
            'Default value. New line separated values supported for checkboxes.')
    )
    help_text = models.TextField(verbose_name=_('help text'), blank=True)

    add_css_class = models.CharField(verbose_name=_(
        'Add CSS class'), max_length=255, blank=True, null=True)
    related_input_class = models.CharField(verbose_name=_(
        'Related Input Name'), max_length=255, blank=True, null=True)
    placeholder = models.CharField(verbose_name=_(
        'Placeholder'), max_length=255, blank=True, null=True)
    # salesforce_field = models.CharField(max_length=255, blank=True, null=True)
    # salesforce_field_type = models.CharField(max_length=20, default='regular', choices=SALESFORCE_FIELD_TYPE_CHOICES)
    # revinate_field = models.CharField(max_length=255, blank=True, null=True)

    # checkbox_value = models.CharField(
    #     verbose_name=_('Checkbox Value'),
    #     max_length=255,
    #     blank=True,
    #     help_text=_('Only for Checkbox field type.')
    # )

    @property
    def clean_name(self):
        return '%s-%s' % (str(slugify(str(unidecode(self.label)))), self.pk)

    @property
    def clean_name_2(self):
        return str(slugify(str(unidecode(self.label))))

    @property
    def clean_related_input_name(self):
        return str(slugify(str(unidecode(self.related_input_class)))) if self.related_input_class else None

    panels = [
        FieldPanel('label'),
        FieldPanel('placeholder'),
        FieldPanel('show_label'),
        FieldPanel('help_text'),
        FieldPanel('required'),
        FieldPanel('field_type', classname="formbuilder-type"),
        FieldPanel('choices', classname="formbuilder-choices"),
        # FieldPanel('choices2', classname="formbuilder-choices"),
        # FieldPanel('revinate_value_based_names', classname="formbuilder-choices"),
        FieldPanel('default_value', classname="formbuilder-default"),
        FieldPanel('add_css_class'),
        FieldPanel('related_input_class'),
        # FieldPanel('salesforce_field_type'),
        # FieldPanel('revinate_field'),

        FieldPanel('lasso_question_list'),
        FieldPanel('lasso_field_name'),
        # FieldPanel('lasso_question_id'),
        # FieldPanel('lasso_field_is_array'),

    ]

    class Meta:
        abstract = True
        ordering = ['sort_order']


class WtFormField(WtAbstractFormField):
    page = ParentalKey('WtForm', related_name='form_fields')


class WtFormHiddenField(Orderable):
    page = ParentalKey('WtForm', related_name='hidden_fields')
    name = models.CharField(max_length=255, )
    value = models.CharField(max_length=255, blank=True, null=True)
    panels = [
        FieldPanel('name'),
        FieldPanel('value'),
    ]

# class WtFormConditionalLassoFields(Orderable):
#     page = ParentalKey('WtForm', related_name='conditional_fields')
#     name = models.CharField(max_length=255)
#     value = models.CharField(max_length=255)
#     condition_field_name = models.CharField(max_length=255)
#     condition_field_value = models.CharField(max_length=255)
#     panels = [
#         FieldPanel('name'),
#         FieldPanel('value'),
#         FieldPanel('condition_field_name'),
#         FieldPanel('condition_field_value'),
#     ]


class WtFormConditionalRotationFields(Orderable):
    page = ParentalKey('WtForm', related_name='conditional_rotation_fields')
    condition_field_name = models.CharField(max_length=255)
    condition_field_value = models.CharField(max_length=255)
    rotation_id = models.IntegerField()
    panels = [
        FieldPanel('condition_field_name'),
        FieldPanel('condition_field_value'),
        FieldPanel('rotation_id'),
    ]

# class WtFormRevinateTokens(Orderable):
#     page = ParentalKey('WtForm', related_name='revinate_tokens')
#     name = models.CharField(max_length=255, )
#     panels = [
#         FieldPanel('name'),
#     ]


class WtFormThankYouPages(Orderable):
    page = ParentalKey('WtForm', related_name='thank_you_pages')
    field_name = models.CharField(max_length=255)
    field_value = models.CharField(max_length=255)
    thank_you_page = models.ForeignKey(
        'wtpages.StandardPage', on_delete=models.CASCADE, related_name='+', verbose_name=_('Thank You Page'))
    panels = [
        FieldPanel('field_name'),
        FieldPanel('field_value'),
        PageChooserPanel('thank_you_page')
    ]


# class WtDocument(Document):
#     def __init__(self, *args, **kwargs):
#         super(WtDocument, self).__init__(*args, **kwargs)
#         #self.file = models.FileField(upload_to=kwargs['upload_to'], verbose_name=_('file'))


class FormPage(AbstractEmailForm):
    class Meta:
        verbose_name = "Form"
    parent_page_types = []
    subpage_types = []


class WtForm(ClusterableModel):
    class Meta:
        verbose_name = "Form"

    selected_thank_you_page = None

    base_form_class = WagtailAdminWtFormPageForm
    form_builder = WtFormBuilder

    theme = models.ForeignKey('wtpages.CssTheme', null=True, blank=True,
                              on_delete=models.SET_NULL, related_name='+', verbose_name=_('Theme'))

    body = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)
    ajax_form = True

    use_streamfield = models.BooleanField(default=False, verbose_name=_("Use StreamField for form fields"))
    form_body = StreamField(WTFORMS_BLOCKS, use_json_field=True, blank=True, verbose_name=_("Form fields (StreamField)"))


    name = models.CharField(max_length=255)
    title = models.CharField(blank=True, max_length=255)

    to_address = models.CharField(
        verbose_name=_('to address'), max_length=255, blank=True,
        help_text=_(
            "Optional - form submissions will be emailed to these addresses. Separate multiple addresses by comma.")
    )
    from_address = models.CharField(verbose_name=_(
        'from address'), max_length=255, blank=True)
    subject = models.CharField(verbose_name=_(
        'subject'), max_length=255, blank=True)

    call_js_on_success = models.TextField(blank=True, null=True)

    enable_recaptcha = models.BooleanField(
        default=False, verbose_name=_('Enable reCAPTCHA'),)

    # post_to_salesforce = models.BooleanField(default=False)
    # salesforce_url = models.URLField(blank=True, null=True)

    # post_to_revinate = models.BooleanField(default=False)
    # revinate_url = models.URLField(blank=True, null=True)

    post_to_lasso = models.BooleanField(default=False)
    lasso_api_url = models.URLField(blank=True, null=True)
    lasso_uid = models.CharField(max_length=255, blank=True, null=True)
    lasso_client_id = models.CharField(max_length=255, blank=True, null=True)
    lasso_project_id = models.CharField(max_length=255, blank=True, null=True)
    lasso_api_key = models.CharField(max_length=1000, blank=True, null=True)
    lasso_domain_account_id = models.CharField(
        max_length=255, blank=True, null=True)
    lasso_source_type = models.CharField(max_length=255, blank=True, null=True)
    lasso_secondary_source_type = models.CharField(
        max_length=255, blank=True, null=True)
    lasso_follow_up_process_id = models.CharField(
        max_length=255, blank=True, null=True)

    submit_button_title = models.CharField(
        max_length=255, blank=True, null=True)

    default_thank_you_page = models.ForeignKey('wtpages.StandardPage', null=True, blank=True,
                                               on_delete=models.SET_NULL, related_name='+', verbose_name=_('Default Thank You Page'))

    captcha_sitekey = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '%s' % self.name

    def get_context(self, request, *args, **kwargs):
        return {
            'page': self,
            'self': self,
            'request': request,
        }

    def get_template(self, request, *args, **kwargs):
        # if request.is_ajax():
        #    return self.ajax_template or self.template
        # else:
        return self.template

    def get_form_fields(self):
        if self.use_streamfield and self.form_body:
            return list(iter_form_field_blocks(self.form_body))
        return self.form_fields.all()

    def get_data_fields(self):
        data_fields = [
            ('submit_time', _('Submission date')),
        ]
        for field in self.get_form_fields():
            if not field.field_type in ['fieldsgroup', 'sectiontitleh2', 'sectiontitleh3']:
                data_fields += [(field.clean_name, field.label)]

        return data_fields

    def get_form_class(self):
        fb = self.form_builder(self.get_form_fields())
        return fb.get_form_class()

    def get_form_parameters(self):
        return {'enable_recaptcha': self.enable_recaptcha}

    def get_form(self, *args, **kwargs):
        form_class = self.get_form_class()
        form_params = self.get_form_parameters()
        form_params.update(kwargs)

        return form_class(*args, **form_params)

    def get_submission_class(self):
        return WtFormSubmission

    def handle_files_upload(self, form, request):
        for filename, file in request.FILES.items():
            folder = str(uuid.uuid4())
            dest_folder = os.path.join(system_settings.UPLOADS_ROOT, folder)

            fn, ex = os.path.splitext(file.name)
            bn = os.path.basename(fn)

            dx = 54 - len(bn) - len(ex)
            if dx < 0:
                bn = bn[:dx]

            fn = "%s%s" % (bn, ex)

            # uploads/79d9ae0a-3671-4a6a-9408-7ce0485e1d25/
            dest = os.path.join(dest_folder, fn)
            save_upload(file, dest)

            # logger.info('Upload saved: %s' % dest)

            cname = '%s - %s' % (COLLECTION_NAME, self.name)

            try:

                try:
                    theCollection = Collection.objects.get(name=cname)
                except Collection.DoesNotExist:
                    theCollection = Collection.get_first_root_node(
                    ).add_child(instance=Collection(name=cname))
                    theCollection.save()

                # file=models.FileField(upload_to="uploads/%s" % folder, verbose_name=_('file'))
                doc = Document(title=file.name)
                # doc.file.upload_to("uploads/%s" % folder)
                doc.file = os.path.join("uploads", folder, fn)
                doc.collection_id = theCollection.id
                doc.save()

                form.cleaned_data[re.sub(
                    r'_0$', '', filename)] = request.build_absolute_uri(doc.url)

            except:
                pass

    def process_form_submission(self, form, request):
        email_back = ''
#         for x in form.fields.items():
#             if isinstance(x[1], fields.EmailField):
#                 str(form.data.get(x[0]))
#                 email_back = str(form.data.get(x[0]))
#                 break

        # super(AbstractEmailForm, self).process_form_submission(form)
        urls = re.compile(
            r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.MULTILINE | re.UNICODE)
        data = {}
        field_by_label = {}
        for name, field in form.fields.items():
            bf = form[name]
            val = form.cleaned_data[name]

            if isinstance(field, WtFileField):
                val = mark_safe(urls.sub(
                    r'<a href="\1" target="_blank">'+os.path.basename(str(val))+'</a>', val))

            if not isinstance(field, WtGroupField):
                data[name] = val

            field_by_label[str(bf.label)] = val

        submission = WtFormSubmission.objects.create(
            form_data=json.dumps(data, cls=DjangoJSONEncoder),
            page=self,
        )

        self.selected_thank_you_page = self.default_thank_you_page
        for thank_you_page in self.thank_you_pages.all():
            s = field_by_label.get(thank_you_page.field_name)
            if s and isinstance(s, list):
                field_values = thank_you_page.field_value.split(',')
                if len(s) == 1 and len(field_values) == 1:
                    # exact property
                    if s[0].strip() == field_values[0].strip():
                        self.selected_thank_you_page = thank_you_page.thank_you_page
                        break
                elif len(s) == len(field_values):
                    match_cnt = 0
                    for field_value in field_values:
                        if field_value.strip() in s:
                            match_cnt += 1

                    if match_cnt == len(s):
                        # city
                        self.selected_thank_you_page = thank_you_page.thank_you_page
                        break

        config = WtSettings.objects.first()
        if not config:
            return
        if self.to_address:

            data = []

            from_email = self.from_address

            for name, field in form.fields.items():
                bf = form[name]
                val = str(form.cleaned_data[name])
                # val = str(form.data.get(x[0]))

                if field.field_type == 'email':
                    from_email = val

                if isinstance(field, WtFileField):
                    val = mark_safe(
                        urls.sub(r'<a href="\1" target="_blank">'+os.path.basename(val)+'</a>', val))

                if not isinstance(field, WtGroupField):
                    data.append({'label': str(bf.label), 'value': val})

            html = render_to_string("wtforms/mail.html", {'form': data})

            if system_settings.DEBUG:
                from django.core.files import File
                f = open('/tmp/mail.html', 'w')
                myfile = File(f)
                myfile.write(html)
                myfile.close()

            content = '\n'.join(
                [x[1].label + ': ' + str(form.data.get(x[0])) for x in form.fields.items()])
            backend = None
            if config.smtp_host:
                backend = EmailBackend(
                    host=config.smtp_host,
                    username=config.smtp_user,
                    password=config.smtp_pass,
                )

            for adr in re.split(r"[\s,;]+", self.to_address):
                if adr:
                    send_mail(self.subject, content, [
                              adr], from_email, connection=backend, html_message=html)  # , fail_silently=False,

            if email_back:
                send_mail(self.subject, content, [
                          email_back], from_email, connection=backend, html_message=html)  # , fail_silently=False,

        # self.add_salesforce(form, request)
        # self.add_revinate(form, request)
        self.add_lasso(form, request, submission)

    def send_mail(self, form):
        addresses = [x.strip() for x in self.to_address.split(',')]
        content = '\n'.join(
            [x[1].label + ': ' + str(form.data.get(x[0])) for x in form.fields.items()])
        send_mail(self.subject, content, addresses, self.from_address,)

    def add_lasso(self, form, request, submission):

        cond_rotations = {}
        cflds = None

        def _add_cond_field(s):
            if cflds:
                for cfld in cflds:
                    if cfld.condition_field_value.casefold() == "{}".format(s).casefold():
                        cond_rotations[cfld.rotation_id] = cfld.rotation_id

        if self.post_to_lasso and self.lasso_api_url and self.lasso_client_id and self.lasso_project_id and self.lasso_api_key:
            # p = re.compile(r'^([a-z0-9]+)([\+]{0,1})[\s]+.*')
            data = {}
            address = {}
            person = {}
            email = None
            phone = None
            questions = []
            ratingID = None

            fields_by_name = {}
            fields = self.get_form_fields()
            for field in fields:
                fields_by_name[field.clean_name_2] = field

            conditional_hash = {}
            for cfld in self.conditional_rotation_fields.all():
                if not cfld.condition_field_name in conditional_hash:
                    conditional_hash[cfld.condition_field_name] = []
                conditional_hash[cfld.condition_field_name].append(cfld)

            form_guid = form.cleaned_data['guid']

            for field in fields:

                # lasso_field_is_array = models.BooleanField(default=False, )
                if field.lasso_field_name or field.lasso_question_list:

                    v = form.cleaned_data[field.clean_name]
                    if field.field_type == 'date' and form.cleaned_data[field.clean_name]:
                        v = form.cleaned_data[field.clean_name].strftime(
                            "%m/%d/%Y")

                    if v and v != '--None--':

                        cflds = conditional_hash[field.label] if field.label in conditional_hash else None

                        if not field.lasso_question_list:
                            _add_cond_field(v)

                        if field.lasso_field_name in ['nameTitle', 'firstName', 'lastName', 'company', 'contactPreference', ]:
                            person[field.lasso_field_name] = v

                        elif field.lasso_field_name in ['address', 'city', 'country', 'state', 'zipCode', ]:
                            address[field.lasso_field_name] = v
                            if v == 'Other' or v == 'other':
                                clean_related_input_name = field.clean_related_input_name
                                if clean_related_input_name in fields_by_name:
                                    address[field.lasso_field_name] = form.cleaned_data[fields_by_name[clean_related_input_name].clean_name]

                        elif field.lasso_field_name == 'email':
                            email = v

                        elif field.lasso_field_name == 'phone':
                            phone = v

                        elif field.lasso_field_name == 'ratingID':
                            ratingID = 2647 if v == 'Yes' else 1650

                        elif field.lasso_question_list:
                            q = {
                                "questionId": "%s" % field.lasso_question_list.lasso_id,
                                "type": "%s" % field.lasso_question_list.field_type,
                                        "name": field.lasso_question_list.title,
                                "answers": []
                            }

                            if field.lasso_question_list.field_type in ["text", "date"]:
                                _add_cond_field(v)
                                q['answers'].append(
                                    {
                                        "answer": v,
                                    }
                                )
                            elif field.field_type == 'checkbox':
                                answer = field.lasso_question_list.list_items.first()
                                if answer:
                                    _add_cond_field(answer.id)
                                    q['answers'].append(
                                        {
                                            "answerId": "%s" % answer.id,
                                            "answer": answer.title,
                                        }
                                    )
                            else:

                                if not isinstance(v, list):
                                    v = [v]

                                for answer_id in v:

                                    _add_cond_field(answer_id)

                                    try:
                                        answer = field.lasso_question_list.list_items.get(
                                            lasso_id=answer_id)
                                        q['answers'].append(
                                            {
                                                "answerId": "%s" % answer_id,
                                                "answer": answer.title,
                                            }
                                        )
                                    except:
                                        pass

                            if q['answers']:
                                questions.append(q)

            for field in self.hidden_fields.all():
                data[field.name] = field.value

            if address:
                data['addresses'] = []
                data['addresses'].append(address)

            if person:
                data['person'] = person

            if email:
                data['emails'] = [
                    {
                        "email": email,
                        "type": "Personal",
                        "primary": True
                    }
                ]

            if phone:
                data['phones'] = [
                    {
                        "phone": phone,
                        "type": "Mobile",
                        "primary": True
                    }
                ]

            if questions:
                data['questions'] = questions

            if ratingID:
                data['ratingID'] = ratingID

            if data:
                data['clientId'] = self.lasso_client_id
                data['project'] = {
                    'projectId': self.lasso_project_id
                }

                if self.lasso_source_type:
                    data['sourceType'] = {
                        'sourceType': self.lasso_source_type
                    }

                if self.lasso_secondary_source_type:
                    data['secondarySourceType'] = {
                        'secondarySourceType': self.lasso_secondary_source_type
                    }

                if self.lasso_domain_account_id:
                    data['websiteTracking'] = {
                        'domainAccountId': self.lasso_domain_account_id,
                        'guid': form_guid if form_guid else submission.id,
                    }

                if self.lasso_follow_up_process_id:
                    data['followUpProcess'] = {
                        'followUpProcessId': self.lasso_follow_up_process_id,
                    }

                # if cond_rotations:
                #     for rotation_id, _ in cond_rotations.items():
                #         print(rotation_id)
                #         data['rotationId'] = rotation_id
                #         # t = threading.Thread(target=lasso_add, args=(self.lasso_api_url, self.lasso_api_key, data))
                #         # t.start()

                t = threading.Thread(target=lasso_add, args=(
                    self.lasso_api_url, self.lasso_api_key, data, cond_rotations))
                t.start()

    # def add_salesforce(self, form, request):
    #     data = {}
    #     p = re.compile(r'^([0-9]+)([\+]{0,1})[\s]+.*')
    #     if self.post_to_salesforce and self.salesforce_url:
    #         for field in self.get_form_fields():
    #             if field.salesforce_field:

    #                 v = form.cleaned_data[field.clean_name]
    #                 if field.field_type == 'date' and form.cleaned_data[field.clean_name]:
    #                     v = form.cleaned_data[field.clean_name].strftime("%m/%d/%Y")

    #                 if v and v != '--None--':
    #                     if field.field_type == 'dropdown2':
    #                         f_names = field.salesforce_field.split(',')
    #                         f_values = v.split(',')
    #                         if len(f_names) == len(f_values) == 2:
    #                             for i in range(0, 2):
    #                                 if f_names[i].strip() in ['00N1U00000UZI09', '00N1U00000UZI0E']:
    #                                     matches = p.match( str(f_values[i].strip()) )
    #                                     if matches:
    #                                         data[f_names[i].strip()] = matches[1] + matches[2]
    #                                 else:
    #                                     data[f_names[i].strip()] = f_values[i].strip()

    #                     else:

    #                         if field.salesforce_field_type == 'array':
    #                             data[field.salesforce_field] = []
    #                             data[field.salesforce_field].append(v)

    #                         elif field.salesforce_field in data:
    #                             data[field.salesforce_field] += ' ' + v

    #                         else:
    #                             data[field.salesforce_field] = v

    #         for field in self.hidden_fields.all():
    #             if field.name in data:
    #                 data[field.name] += ' ' + field.value
    #             else:
    #                 data[field.name] = field.value

    #         if self.captcha_sitekey and self.enable_recaptcha:
    #             data['g-recaptcha-response'] = request.POST.get('g-recaptcha-response', '')

    #         if data:
    #             try:
    #                 from django.core.files import File
    #                 f = open('/tmp/salesforce.log', 'w')
    #                 myfile = File(f)
    #                 myfile.write(json.dumps(data))
    #                 myfile.close()
    #             except:
    #                 pass

    #             t = threading.Thread(target=salesforce_add, args=(self.salesforce_url, data,))
    #             t.start()

    # def add_revinate(self, form, request):
    #     data = {
    #         'tokens': [],
    #         'contacts': [],
    #     }

    #     contact = {}

    #     p = re.compile(r'^([0-9]+)([\+]{0,1})[\s]+.*')
    #     if self.post_to_revinate and self.revinate_url:

    #         for tn in self.revinate_tokens.all():
    #             data['tokens'].append(tn.name)

    #         for field in self.get_form_fields():
    #             if field.revinate_field or field.revinate_value_based_names:

    #                 v = form.cleaned_data[field.clean_name]
    #                 if field.field_type == 'date' and form.cleaned_data[field.clean_name]:
    #                     v = form.cleaned_data[field.clean_name].strftime("%Y-%m-%d")

    #                 if v and v != '--None--':
    #                     if field.field_type in ['dropdown', 'checkboxes'] and field.revinate_value_based_names:
    #                         if field.field_type == 'dropdown':
    #                             v = [v]
    #                         choices_items =  field.choices.splitlines()
    #                         revinate_value_based_names_items = field.revinate_value_based_names.splitlines()
    #                         if len(choices_items) == len(revinate_value_based_names_items):
    #                             for i in range(0, len(choices_items)):
    #                                 if choices_items[i] in v:
    #                                     contact[revinate_value_based_names_items[i]] = True

    #                     else:

    #                         if field.revinate_field in contact:
    #                             contact[field.revinate_field] += ' ' + v

    #                         else:
    #                             contact[field.revinate_field] = v

    #         if contact:
    #             data['contacts'].append(contact)
    #             # try:
    #             #     from django.core.files import File
    #             #     f = open('/tmp/revinate.log', 'w')
    #             #     myfile = File(f)
    #             #     myfile.write(json.dumps(data))
    #             #     myfile.close()
    #             # except:
    #             #     pass

    #             t = threading.Thread(target=revinate_add, args=(self.revinate_url, data,))
    #             t.start()

    @csrf_exempt
    @never_cache
    def serve(self, request):

        for field in self.get_form_fields():
            if field.field_type == 'venueselect':
                field.default_value = str(
                    request.META.get('CURRENT_VENUE', None))

        context = self.get_context(request)

        if request.method == 'POST':
            # print(request.COOKIES)
            # print(request.META['HTTP_X_CSRFTOKEN'])

            form = self.get_form(request.POST, request.FILES)

            if self.ajax_form:
                cont = self.get_context(request)
                if form.is_valid():

                    self.handle_files_upload(form, request)

                    self.process_form_submission(form, request)
                    cont['form'] = self.get_form()
                    res = {
                        'status': 'success',
                        'message_text': self.thank_you_text,
                        'message_title': self.title,
                        'call_js_on_success': self.call_js_on_success,
                        'thank_you_url': self.selected_thank_you_page.url if self.selected_thank_you_page else None,
                    }
                else:
                    cont['form'] = form
                    res = {
                        'status': 'error',
                        'form_html': render_to_string(self.template_fields, cont),
                    }
                return JsonResponse(res)

            elif form.is_valid():

                self.handle_files_upload(form, request)

                self.process_form_submission(form, request)
                # render the landing_page
                # TODO: It is much better to redirect to it
                return render(
                    request,
                    self.landing_page_template,
                    self.get_context(request)
                )

        else:
            form = self.get_form()
            context['is_popup'] = True
            context['modal_only'] = True

        context['form'] = form
        return render(
            request,
            self.template,
            context
        )

    @property
    def submissions_size(self):
        return self.get_submission_class().objects.filter(page=self).count()

    @property
    def recaptcha_sitekey(self):
        return system_settings.RECAPTCHA_SITEKEY

    @property
    def has_bootstrap_col_class(self):
        p = re.compile('col-(xs|sm|md|lg)-[0-9]+')
        try:
            for field in self.get_form_fields():
                if p.match(str(field.add_css_class)):
                    return True
        except:
            pass
        return False

    panels = [
        MultiFieldPanel([
            FieldPanel('name', classname="full title"),
            FieldPanel('title', classname="full title"),
            FieldPanel('body'),
            FieldPanel('submit_button_title'),
            FieldPanel('thank_you_text', classname="full"),
            FieldPanel('theme'),
            FieldPanel('call_js_on_success'),

            # FieldPanel('post_to_salesforce'),
            # FieldPanel('salesforce_url'),

            # FieldPanel('post_to_revinate'),
            # FieldPanel('revinate_url'),

            PageChooserPanel('default_thank_you_page'),
        ], "Basic"),

        MultiFieldPanel([
            FieldPanel('enable_recaptcha'),
            FieldPanel('captcha_sitekey'),
        ], "reCaptcha", classname="collapsible collapsed-no"),


        MultiFieldPanel([
            FieldPanel('post_to_lasso'),
            FieldPanel('lasso_api_url'),
            FieldPanel('lasso_uid'),
            FieldPanel('lasso_client_id'),
            FieldPanel('lasso_project_id'),
            FieldPanel('lasso_domain_account_id'),
            FieldPanel('lasso_source_type'),
            FieldPanel('lasso_secondary_source_type'),
            FieldPanel('lasso_follow_up_process_id'),

            FieldPanel('lasso_api_key'),
        ], "Lasso", classname="collapsible collapsed-no"),


        MultiFieldPanel([
            FieldPanel('use_streamfield'),
            FieldPanel('form_body'),
        ], heading='Form fields (StreamField)', classname="collapsible "),

        MultiFieldPanel([InlinePanel('form_fields',),],
                        heading='Form fields (Legacy InlinePanel)', classname="collapsible "),

        MultiFieldPanel([InlinePanel('hidden_fields',),],
                        heading='Hidden fields', classname="collapsible "),
        MultiFieldPanel([InlinePanel('conditional_rotation_fields',),],
                        heading='Lasso API Conditional RotationID', classname="collapsible "),


        # MultiFieldPanel([InlinePanel('revinate_tokens',),],heading='Revinate Tokens',classname="collapsible "),

        MultiFieldPanel([InlinePanel('thank_you_pages',),],
                        heading='Thank You Pages', classname="collapsible "),

        MultiFieldPanel([
            FieldPanel('to_address', classname="full"),
            FieldPanel('from_address', classname="full"),
            FieldPanel('subject', classname="full"),
        ], "Email", classname="collapsible collapsed"),

    ]


class WtFormSubmission(models.Model):

    form_data = models.TextField()
    page = models.ForeignKey(WtForm, on_delete=models.CASCADE)

    submit_time = models.DateTimeField(
        verbose_name=_('submit time'), auto_now_add=True)

    def get_data(self):
        """
        Returns dict with form data.

        You can override this method to add additional data.
        """
        form_data = json.loads(self.form_data)
        form_data.update({
            'submit_time': self.submit_time,
        })

        return form_data

    def __str__(self):
        return self.form_data

    class Meta:
        verbose_name = _('Wt Form submission')


_FORM_CONTENT_TYPES = None


def get_form_types():
    global _FORM_CONTENT_TYPES
    if _FORM_CONTENT_TYPES is None:
        form_models = [
            model for model in get_page_models()
            if issubclass(model, WtForm)
        ]

        _FORM_CONTENT_TYPES = list(
            ContentType.objects.get_for_models(*form_models).values()
        )
    return _FORM_CONTENT_TYPES


def get_forms_for_user(user):
    """
    Return a queryset of form pages that this user is allowed to access the submissions for
    """
#     editable_forms = UserPagePermissionsProxy(user).editable_pages()
#     editable_forms = editable_forms.filter(content_type__in=get_form_types())
#
#     # Apply hooks
#     for fn in hooks.get_hooks('filter_form_submissions_for_user'):
#         editable_forms = fn(user, editable_forms)
#
#     return editable_forms

    return WtForm.objects.all()


class WtFormLinkField(models.Model):
    is_popup = models.BooleanField("Popup Form", blank=True, default=False)
    form = models.ForeignKey('wtforms.WtForm', null=False,
                             blank=False, related_name='+', on_delete=models.CASCADE)

    panels = [
        FieldPanel('form'),
        FieldPanel('is_popup'),
    ]

    class Meta:
        abstract = True


class FormLinkPage(NextHeadlessPreviewMixin, Page):
    class Meta:
        verbose_name = _("Form Popup Page")

    form = models.ForeignKey('wtforms.WtForm', null=True,
                             blank=True, related_name='+', on_delete=models.SET_NULL)
    # external = models.BooleanField(default=False, help_text='Open link in a new window')

    def get_sitemap_urls(self, request=None):
        return []

    content_panels = [
        MultiFieldPanel([
            FieldPanel('title', classname="title"),
            FieldPanel('form'),
            # FieldPanel('external'),
        ], heading=_('Basic')),
    ]
    promote_panels = [
        MultiFieldPanel([
            FieldPanel('show_in_menus'),
            FieldPanel('slug'),
            # FieldPanel('seo_title'),
            # FieldPanel('search_description'),
            # FieldPanel('seo_keywords'),
        ], _('Common page configuration')),
    ]


def save_upload(f, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb+') as destination:
        if hasattr(f, 'multiple_chunks') and f.multiple_chunks():
            for chunk in f.chunks():
                destination.write(chunk)
        else:
            destination.write(f.read())
