# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class crawl_data(models .Model):
    Task_ID = models.IntegerField()
    crawl_domain = models.CharField (max_length= 255)
    title = models.CharField (max_length= 255)
    decode = models.CharField (max_length= 255)
    date_time = models.DateTimeField ()



# Create your models here.
