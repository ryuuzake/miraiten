from .base import *

from os import environ

if environ['DJANGO_SETTINGS_MODULE'] == 'miraiten.settings':
    from .development import *
