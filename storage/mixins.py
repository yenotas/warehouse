# Миксин для контроля доступа к полям
import json

from django.forms import modelformset_factory

from storage.models import ModelAccessControl
from django.contrib.admin.views.main import ChangeList

from storage.admin.__CustomAdminSite import admin_site
from django.db import models

def check_old_value(obj, field):
    """ Проверяем, является ли поле ForeignKey и если да, то есть ли старое сохраненное значение"""
    field_obj = obj._meta.get_field(field)
    if isinstance(field_obj, models.ForeignKey):
        old_field_name = f"{field}_old"
        if hasattr(obj, old_field_name):
            return getattr(obj, old_field_name)
    return None


def get_changelist_instance(request, model):
    verbose_names = []
    methods = {}
    print('\n\nget_changelist_instance\n\n')
    admin_class = admin_site._registry.get(model)
    if not admin_class:
        raise ValueError(f"Admin class for {model} not found.")

    list_display = admin_class.get_list_display(request)
    list_display_text = []

    for field in list_display:
        if hasattr(model, field):
            verbose_names.append(model._meta.get_field(field).verbose_name)
            list_display_text.append(f"display_{field}")
        elif hasattr(admin_class, field):
            method = getattr(admin_class, field)
            verbose_names.append(getattr(method, 'short_description', field))
            methods[field] = method
            list_display_text.append(f"display_{field}")
        else:
            verbose_names.append(field)
            list_display_text.append(f"display_{field}")

    cl = ChangeList(
        request,
        model,
        list_display=list_display,
        list_display_links=admin_class.get_list_display_links(request, list_display),
        list_filter=admin_class.get_list_filter(request),
        date_hierarchy=admin_class.date_hierarchy,
        search_fields=admin_class.get_search_fields(request),
        list_select_related=admin_class.get_list_select_related(request),
        list_per_page=admin_class.list_per_page,
        list_max_show_all=admin_class.list_max_show_all,
        list_editable=admin_class.list_editable,
        sortable_by=admin_class.sortable_by,
        search_help_text=admin_class.search_help_text,
        model_admin=admin_class
    )

    queryset = cl.queryset

    # Добавляем текстовые поля в объекты queryset
    for obj in queryset:
        for field in list_display:
            value = getattr(admin_class, field, None) or getattr(obj, field, None)
            if callable(value):
                value = value(obj)
            if not value:
                value = check_old_value(obj, field)
            text_field = f"display_{field}"
            setattr(obj, text_field, str(value) if value is not None else "—")
            print(f'НОВЫЙ queryset {text_field}: {getattr(obj, text_field)}')

    cl.list_display_text = list_display_text

    if model._meta.model_name == 'pivottable':
        # для широкой таблицы делаю редактируемые поля
        editable_fields = [field for field in list_display if model._meta.get_field(field).editable]
        formset = modelformset_factory(model, fields=editable_fields, extra=0)
        cl.formset = formset(queryset=cl.queryset)
    else:
        cl.formset = None

    return cl, verbose_names, methods



class AccessControlMixin:
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = request.user
        user_groups = set(user.groups.values_list('name', flat=True))
        model_name = self.model._meta.model_name

        access_controls = ModelAccessControl.objects.filter(model_name__model=model_name)

        # Делаем поле 'ID' неактивным для всех пользователей
        if 'id' in form.base_fields:
            form.base_fields['id'].disabled = True
            form.base_fields['id'].widget.attrs['readonly'] = True
            form.base_fields['id'].widget.attrs['style'] = 'background-color: #f0f0f0;'

        # Отключаем поля на основе настроек доступа
        for access_control in access_controls:
            access_groups = set(access_control.groups.values_list('name', flat=True))
            if user_groups.isdisjoint(access_groups):
                if isinstance(access_control.fields_to_disable, str):
                    fields_to_disable = json.loads(access_control.fields_to_disable)
                else:
                    fields_to_disable = access_control.fields_to_disable
                for field in fields_to_disable:
                    if field in form.base_fields:
                        form.base_fields[field].disabled = True
                        form.base_fields[field].widget.attrs['readonly'] = True
                        form.base_fields[field].widget.attrs['style'] = 'background-color: #f0f0f0;'

        return form
