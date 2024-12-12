import base64

from django.contrib import admin
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
import json

from storage.mixins import AccessControlMixin


def save_files_to_session(request, formset):
    files_data = {}
    for form in formset.forms:
        for field_name, file in form.files.items():
            print('save', field_name, file.name, file.content_type)
            if isinstance(file, InMemoryUploadedFile):
                file.seek(0)  # Перемещаем указатель в начало
                file_content_base64 = base64.b64encode(file.read()).decode('utf-8')
                files_data[field_name] = {
                    'name': file.name,
                    'content': file_content_base64,
                    'content_type': file.content_type,
                }
    request.session['saved_files'] = files_data



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
            print('ИНФО!')
            print(formset.errors)
            print(request.FILES)
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
                # Сохраняем файлы в сессию
                print('no valid set!')
                save_files_to_session(request, formset)
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
            print('ИНФО!')
            print(formset.errors)
            print(request.FILES)
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
                # Сохраняем файлы в сессию
                print('no valid set!')
                save_files_to_session(request, formset)
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
                # Сохраняем файлы в сессию
                save_files_to_session(request, formset)
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

    def get_form(self, request, obj=None, **kwargs):
        print('get_form')
        # Восстановление файлов из сессии
        files_data = request.session.get('saved_files', {})
        if files_data:
            for field_name, file_data in files_data.items():
                print('field_name', field_name, file_data['name'])
                if file_data['content']:  # Убедимся, что данные есть
                    file_content = base64.b64decode(file_data['content'].encode('utf-8'))
                    file = InMemoryUploadedFile(
                        file=ContentFile(file_content),
                        field_name=field_name,
                        name=file_data['name'],
                        content_type=file_data['content_type'],
                        size=len(file_content),
                        charset=None,
                    )
                    # Добавляем в request.FILES
                    request.FILES[field_name] = file

        return super().get_form(request, obj, **kwargs)


