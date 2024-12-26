import tempfile

from django import forms
from django.contrib import admin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import modelformset_factory, BaseModelFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import escape
import json

from storage.mixins import AccessControlMixin
from storage.models import CustomUser


def save_files_to_session(request, formset):
    temp_files = {}
    for form in formset.forms:
        for field_name, file in form.files.items():
            if file:
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file.write(file.read())
                temp_file.close()
                temp_files[field_name] = {
                    'path': temp_file.name,
                    'name': file.name,
                    'content_type': file.content_type,
                }
    request.session['saved_files'] = temp_files


def get_temp_files(request):
    temp_files = request.session.get('saved_files', {})
    file_previews = {}
    for field_name, file_data in temp_files.items():
        if file_data and file_data['path']:
            try:
                with open(file_data['path'], 'rb') as f:
                    file = InMemoryUploadedFile(
                        file=ContentFile(f.read()),
                        field_name=field_name,
                        name=file_data['name'],
                        content_type=file_data['content_type'],
                        size=f.tell(),
                        charset=None,
                    )
                request.FILES[field_name] = file
                file_previews[field_name] = file_data['path']
            except FileNotFoundError:
                pass
    return file_previews


def clear_temp_files(request):
    print("очистка файлов")
    temp_files = request.session.pop('saved_files', {})
    for file_data in temp_files.values():
        try:
            if file_data and file_data['path']:
                default_storage.delete(file_data['path'])
        except Exception as e:
            print(f"Ошибка удаления файла {file_data['path']}: {e}")


def handle_related_field_error(form, field_name, error):
    """
    Обрабатывает ошибки, связанные с полями, указанными в related_fields.
    """
    related_info = form.get_related_model_info(field_name)
    if not related_info:
        return

    model_name = related_info.get('model')
    group_key = related_info.get('filter')
    if model_name == "CustomUser" and group_key:
        # Извлекаем имя пользователя из ошибки
        user_name = error.split("'")[1]
        first_name, last_name = user_name.split()[0], user_name.split()[1]
        filter_dict = {'manager': 'Менеджеры', 'engineer': 'Инженеры'}
        group_name = filter_dict.get(group_key)

        if group_name:
            qs = CustomUser.objects.filter(
                groups__name=group_name,
                first_name__iexact=first_name,
                last_name__iexact=last_name
            )
            if qs.exists():
                user = qs.first()
                hidden_field_name = f"{field_name}_id"
                form.cleaned_data[hidden_field_name] = user.id
                form.data = form.data.copy()
                form.data[f"id_{form.prefix}-{hidden_field_name}"] = user.id
            else:
                raise forms.ValidationError(f"Пользователь {user_name} не найден.")


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

    # Функция для создания класса formset
    # def get_formset_class(self, request, extra=1):
    #     return modelformset_factory(
    #         self.model,
    #         form=self.get_form(request),
    #         extra=extra,
    #     )

    def get_formset_class(self, request, extra=1):
        class BaseTableFormSet(BaseModelFormSet):
            def construct_instance(self, form, **kwargs):
                # Call the super method to create the instance
                instance = super().construct_instance(form, **kwargs)
                # Update the instance with data from the new fields
                for field_name in self.form.related_fields:
                    id_field_name = f"{field_name}_id"
                    if id_field_name in form.cleaned_data:
                        setattr(instance, field_name, form.cleaned_data)
                return instance

        return modelformset_factory(
            self.model,
            form=self.get_form(request),
            extra=extra,
            formset=BaseTableFormSet  # Use the custom formset class
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if request.method == 'POST':
            formset_class = self.get_formset_class(request)
            formset = formset_class(request.POST, request.FILES, queryset=self.model.objects.none())
            print('ИНФО!')
            print(formset.errors)
            print('Файлы в сессии:', request.FILES)
            print('Формсет поля:', [form.fields.keys() for form in formset.forms])
            if formset.is_valid():

                # print('Обновляю формсет')
                # for form in formset.forms:
                #     form.update_instance()  # Обновляем инстансы моделей перед сохранением

                clear_temp_files(request)
                new_objects = formset.save(commit=False)

                print('Сохраняю формсет')
                for new_object in new_objects:
                    self.save_model(request, new_object, formset, change=False)
                count = len(new_objects)
                if count == 1:
                    msg = '"%(object)s" добавлен.' % {'object': new_objects[0]}
                else:
                    msg = 'Записи добавлены.'
                self.message_user(request, msg, messages.SUCCESS)
                return redirect(request.path)
            else:
                # Сохраняем файлы в сессию
                print('no valid set!')
                print('Formset errors:', formset.errors)
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
        extra_context['preview_files'] = get_temp_files(request)
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
                        msg = '"%(object)s" добавлен!' % {'object': new_objects[0]}
                    else:
                        msg = 'Записи добавлены!'
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
        form_fields = list(formset.forms[0].fields.keys()) if formset.forms[0] else []
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
                    msg = 'Запись обновлена.'
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
        print('formset', list(formset.forms))
        form_fields = list(formset.forms[0].fields.keys()) if formset.forms[0] else []
        extra_context['form_fields_json'] = json.dumps(form_fields)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

