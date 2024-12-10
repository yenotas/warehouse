from django.contrib import admin
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
import json

from storage.mixins import AccessControlMixin


class TableModelAdmin(AccessControlMixin, admin.ModelAdmin):
    change_list_template = 'admin/table_view.html'
    add_form_template = 'admin/table_add.html'
    change_form_template = 'admin/table_change.html'
    ordering = ['-id']

    def get_admin_form(self, request, form):
        from django.contrib.admin.helpers import AdminForm
        return AdminForm(form, list(self.get_fieldsets(request)), {})

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.distinct()

    def get_formset_class(self, request, extra=1):
        return modelformset_factory(
            self.model,
            form=self.get_form(request),
            extra=extra,
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
        extra_context['button_name'] = "Добавить"
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        is_popup = '_popup' in request.GET or '_popup' in request.POST
        formset_class = self.get_formset_class(request)

        if request.method == 'POST':
            formset = formset_class(request.POST, request.FILES, queryset=self.model.objects.none())
            if formset.is_valid():
                # Создаем новые объекты, но не сохраняем их сразу
                new_objects = formset.save(commit=False)

                # Сохраняем каждый объект и вызываем дополнительные методы, если нужно
                for new_object in new_objects:
                    self.save_model(request, new_object, formset,
                                    change=False)  # Применение кастомной логики сохранения
                    new_object.save()  # Сохранение объекта в базе

                # Отправляем сообщение об успешном добавлении
                count = len(new_objects)
                if is_popup:
                    return self.response_add(request, new_objects[-1])
                else:
                    if count == 1:
                        msg = _('"%(object)s" добавлен!') % {'object': new_objects[0]}
                    else:
                        msg = _('Записи добавлены!')
                    self.message_user(request, msg, messages.SUCCESS)

                    # Редирект на список объектов
                    return redirect(
                        'admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
            else:
                # Передача формы с ошибками в контекст
                extra_context['formset'] = formset
        else:
            # Создаем пустой formset для добавления новых записей
            formset = formset_class(queryset=self.model.objects.none())
            extra_context['formset'] = formset

        extra_context['is_popup'] = is_popup
        if not is_popup:
            extra_context['title'] = ""

        extra_context['button_name'] = "Добавить"
        form_fields = list(formset.forms[0].fields.keys()) if formset.forms else []
        extra_context['form_fields_json'] = json.dumps(form_fields)

        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        is_popup = '_popup' in request.GET or '_popup' in request.POST

        # Получаем редактируемый объект
        queryset = self.model.objects.filter(pk=object_id)

        # Создаём класс formset с параметром extra=0
        formset_class = self.get_formset_class(request, extra=0)

        if request.method == 'POST':
            formset = formset_class(request.POST, request.FILES, queryset=queryset)
            if formset.is_valid():
                updated_objects = formset.save(commit=False)
                for updated_object in updated_objects:
                    self.save_model(request, updated_object, formset, change=True)
                if is_popup:
                    # Логика для обработки попапа
                    obj_repr = escape(str(updated_objects[0]))
                    return HttpResponse(f"""
                        <script type="text/javascript">
                            opener.dismissChangeRelatedObjectPopup(window, "{updated_objects[0].pk}", "{obj_repr}");
                        </script>
                    """)
                else:
                    # Обычный редирект на список объектов
                    msg = _('Запись обновлена.')
                    self.message_user(request, msg, messages.SUCCESS)
                    return redirect(
                        'admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name))
            else:
                extra_context['formset'] = formset
        else:
            # Создаём formset только для редактируемого объекта
            formset = formset_class(queryset=queryset)
            extra_context['formset'] = formset

        extra_context['is_popup'] = is_popup
        extra_context['subtitle'] = ""
        if not is_popup:
            extra_context['title'] = ""
        extra_context['button_name'] = "Сохранить"
        form_fields = list(formset.forms[0].fields.keys()) if formset.forms else []
        extra_context['form_fields_json'] = json.dumps(form_fields)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)



