# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response

# Create your views here.
from crawl_web.models import crawl_data


def crawl_web_data(request):
    data = crawl_data.objects .all()
    return render_to_response ("craw_web_data.html", locals ())