from __future__ import absolute_import, unicode_literals

import csv
import datetime

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import smart_str
from django.utils.translation import gettext as _


from wagtail.admin import messages
from wagtail.models import Page
from .forms import SelectDateForm


from django.http import HttpResponseRedirect
from django.views import View

from .models import WtForm, get_forms_for_user

def index(request):
    form_pages = get_forms_for_user(request.user)

    from django.core.paginator import Paginator
    paginator = Paginator(form_pages, per_page=25)
    form_pages = paginator.get_page(request.GET.get('p'))

    return render(request, 'wtforms/admin/index.html', {
        'form_pages': form_pages,
    })


def delete_submission(request, page_id, submission_id):
    if not get_forms_for_user(request.user).filter(id=page_id).exists():
        raise PermissionDenied

    page = get_object_or_404(WtForm, id=page_id)
    submission = get_object_or_404(page.get_submission_class(), id=submission_id)

    if request.method == 'POST':
        submission.delete()

        messages.success(request, _("Submission deleted."))
        return redirect('wtforms:list_submissions', page_id)

    return render(request, 'wtforms/admin/confirm_delete.html', {
        'page': page,
        'submission': submission
    })


def list_submissions(request, page_id):
    if not get_forms_for_user(request.user).filter(id=page_id).exists():
        raise PermissionDenied

    form_page = get_object_or_404(WtForm, id=page_id)
    form_submission_class = form_page.get_submission_class()

    data_fields = form_page.get_data_fields()

    submissions = form_submission_class.objects.filter(page=form_page).order_by('submit_time')
    data_headings = [label for name, label in data_fields]

    select_date_form = SelectDateForm(request.GET)
    if select_date_form.is_valid():
        date_from = select_date_form.cleaned_data.get('date_from')
        date_to = select_date_form.cleaned_data.get('date_to')
        # careful: date_to should be increased by 1 day since the submit_time
        # is a time so it will always be greater
        if date_to:
            date_to += datetime.timedelta(days=1)
        if date_from and date_to:
            submissions = submissions.filter(submit_time__range=[date_from, date_to])
        elif date_from and not date_to:
            submissions = submissions.filter(submit_time__gte=date_from)
        elif not date_from and date_to:
            submissions = submissions.filter(submit_time__lte=date_to)

    if request.GET.get('action') == 'CSV':
        # return a CSV instead
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment;filename=export.csv'

        # Prevents UnicodeEncodeError for labels with non-ansi symbols
        data_headings = [smart_str(label) for label in data_headings]

        writer = csv.writer(response)
        writer.writerow(data_headings)
        for s in submissions:
            data_row = []
            form_data = s.get_data()
            for name, label in data_fields:
                data_row.append(smart_str(form_data.get(name)))
            writer.writerow(data_row)
        return response

    from django.core.paginator import Paginator
    paginator = Paginator(submissions, per_page=25)
    submissions = paginator.get_page(request.GET.get('p'))

    data_rows = []
    for s in submissions:
        form_data = s.get_data()
        data_row = [form_data.get(name) for name, label in data_fields]
        data_rows.append({
            "model_id": s.id,
            "fields": data_row
        })

    return render(request, 'wtforms/admin/index_submissions.html', {
        'form_page': form_page,
        'select_date_form': select_date_form,
        'submissions': submissions,
        'data_headings': data_headings,
        'data_rows': data_rows
    })



class WtFormView(View):

    def get(self, request, *args, **kwargs):
        obj = WtForm.objects.get(id=self.kwargs['pk'])
        return obj.serve(request)        

    def post(self, request, *args, **kwargs):
        obj = WtForm.objects.get(id=self.kwargs['pk'])
        return obj.serve(request)
    
    
    
    
    
