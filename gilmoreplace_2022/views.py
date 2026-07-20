from __future__ import absolute_import, unicode_literals
import re
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from wagtail.utils import sendfile_streaming_backend
from wagtail.utils.sendfile import sendfile
from wagtail.documents import get_document_model
from wagtail.documents.models import document_served


def pdf_document_serve(request, document_id, document_filename):
    Document = get_document_model()
    doc = get_object_or_404(Document, id=document_id)
    if doc.filename != document_filename:
        raise Http404('This document does not match the given filename.')
    document_served.send(sender=Document, instance=doc, request=request)
    local_path = doc.file.path
    return sendfile(
        request,
        local_path,
        attachment=False,
        attachment_filename=False,
        backend=sendfile_streaming_backend.sendfile
    )

