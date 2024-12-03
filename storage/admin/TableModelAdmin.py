from django.contrib import admin
from django.forms import modelformset_factory
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
import json

from storage.mixins import AccessControlMixin


class TableModelAdmin(AccessControlMixin, admin.ModelAdmin):
    change_list_template = 'admin/table_view.html'
    add_form_template = 'admin/table_add.html'

    def get_admin_form(self, request, form):
        from django.contrib.admin.helpers import AdminForm
        return AdminForm(form, list(self.get_fieldsets(request)), {})

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.distinct()

    def get_formset_class(self, request):
        return modelformset_factory(
            self.model,
            form=self.get_form(request),
            extra=1,
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if request.method == 'POST':
            formset_class = self.get_formset_class(request)
            formset = formset_class(request.POST, request.FILES, queryset=self.model.objects.none())
            if formset.is_valid():
                new_objects = formset.save(commit=False)
                for new_object in new_objects:
                    self.save_model(request, new_object, formset, change=False)
                count = len(new_objects)
                if count == 1:
                    msg = _('"%(object)s" добавлен.') % {'object': new_objects[0]}
                else:
                    msg = _('Записи добавлены.')
                self.message_user(request, msg, messages.SUCCESS)
                return redirect(request.path)
            else:
                extra_context['formset'] = formset
        else:
            formset_class = self.get_formset_class(request)
            formset = formset_class(queryset=self.model.objects.none())
            extra_context['formset'] = formset

        form_fields = list(formset.forms[0].fields.keys()) if formset.forms else []
        extra_context['form_fields_json'] = json.dumps(form_fields)
        extra_context['title'] = ""
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        is_popup = '_popup' in request.GET or '_popup' in request.POST
        formset_class = self.get_formset_class(request)

        if request.method == 'POST':
            formset = formset_class(request.POST, request.FILES, queryset=self.model.objects.none())
            if formset.is_valid():
                new_objects = formset.save(commit=False)
                for new_object in new_objects:
                    self.save_model(request, new_object, formset, change=False)
                count = len(new_objects)
                if is_popup:
                    return self.response_add(request, new_objects[-1])
                else:
                    if count == 1:
                        msg = _('"%(object)s" добавлен.') % {'object': new_objects[0]}
                    else:
                        msg = _('Записи добавлены.')
                    self.message_user(request, msg, messages.SUCCESS)
                    return redirect('admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
            else:
                extra_context['formset'] = formset
        else:
            formset = formset_class(queryset=self.model.objects.none())
            extra_context['formset'] = formset

        extra_context['is_popup'] = is_popup
        if not is_popup:
            extra_context['title'] = ""
        form_fields = list(formset.forms[0].fields.keys()) if formset.forms else []
        extra_context['form_fields_json'] = json.dumps(form_fields)
        return super().add_view(request, form_url, extra_context=extra_context)
