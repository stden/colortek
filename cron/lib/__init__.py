#!/usr/bin/env python
# coding: utf-8
import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.pardir)
VENV_ROOT = os.path.join(PROJECT_ROOT, 've/lib/python2.7/site-packages')
#os.environ['DJANGO_SETTINGS_MODULE'] = PROJECT_ROOT
sys.path.insert(1, PROJECT_ROOT)
sys.path.insert(0, VENV_ROOT)
import settings
from django.core.management import setup_environ
setup_environ(settings)
