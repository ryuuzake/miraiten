from .base import *

from os import environ

if environ['DJANGO_SETTINGS_MODULE'] == 'kyou_id_clone.settings':
    from .development import *
