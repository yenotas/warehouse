from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from urllib.parse import urlencode
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin, GroupAdmin as DefaultGroupAdmin, UserAdmin
from django.contrib.admin import ModelAdmin
from django.forms import ModelForm


