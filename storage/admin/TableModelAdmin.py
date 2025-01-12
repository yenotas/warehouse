import tempfile

from django import forms
from django.apps import apps
from django.contrib import admin
from django.contrib.postgres.search import TrigramSimilarity
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import modelformset_factory, BaseModelFormSet
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import escape
import json

from storage.forms import BaseTableForm
from storage.models import CustomUser
from django.forms.models import BaseModelFormSet
from django.core.cache import cache
from functools import lru_cache
from django.core.cache import cache


class CustomBaseModelFormSet(BaseModelFormSet):
    # Не работает
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def _construct_forms(self):
        self.forms = []
        for i in range(self.total_form_count()):
            print('\nCustomBaseModelFormSet ФОРМА', i, self.request)
            self.forms.append(self._construct_form(i, request=self.request))


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
                print(f"Сохранен файл {file.name} в сессию")
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
                print(f"Файл {file_data['name']} восстановлен из сессии")
            except FileNotFoundError:
                print(f"Файл {file_data['path']} не найден")
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


class TableModelAdmin(admin.ModelAdmin):
    change_list_template = 'admin/table_view.html'
    add_form_template = 'admin/table_add.html'
    change_form_template = 'admin/table_change.html'
    ordering = ['-id']

    @lru_cache(maxsize=None)
    def get_formset_class(self, request=None, obj=None, **kwargs):
        model = self.model
        formset_name = model.__name__ + '_formset'
        print(f'\nЗапрос formset_class {formset_name}')
        form = cache.get(formset_name, None)

        if not form:
            form = modelformset_factory(
                model,
                form=self.get_form_with_request(request, obj, **kwargs),
                extra=1,
                can_delete=True
            )
            cache.set(formset_name, form, timeout=60 * 60)
        else:
            print(f'ПОВТОРНЫЙ запрос формсета!\n')

        return form

    def get_form_with_request(self, request, obj=None, **kwargs):
        # Прихватываем request для каждой формы сета
        form_class = super().get_form(request, obj, **kwargs)
        class FormWithRequest(form_class):
            def __init__(form_self, *args, **kwargs):
                kwargs['request'] = request
                super().__init__(*args, **kwargs)

        return FormWithRequest

    def _process_related_fields(self, formset):
        for form in formset:
            if hasattr(form, 'related_fields'):
                for field_name, field_info in form.related_fields.items():
                    id_field = f"{field_name}_id"
                    if id_field in form.cleaned_data:
                        model = apps.get_model('storage', field_info['model'])
                        try:
                            related_obj = model.objects.get(pk=form.cleaned_data[id_field])
                            form.cleaned_data[field_name] = related_obj
                        except model.DoesNotExist:
                            pass
                    form.cleaned_data.pop(id_field, None)
                    form.cleaned_data.pop(f"{field_name}_name", None)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        request = request or None
        action = request.POST.get('form_action', None) or request.POST.get('action', '')
        print('\n\nchangelist_view тип формы', action or 'view')
        print('changelist_view request:', request or 'None', '\n\n')

        if request.method == 'POST':
            if 'edit' in action:
                object_id = action.replace('edit_', '')
                extra_context['form_action'] = action
                print('\nПоказываю change_view')
                return self.change_view(request, object_id, '', extra_context)
            elif action == 'add':
                print('\nПоказываю add_view')
                return self.add_view(request, '', extra_context)
        else:
            formset_class = self.get_formset_class(request)
            print('\nchangelist_view formset_class', formset_class)

            formset = formset_class(queryset=self.model.objects.none())
            extra_context['formset'] = formset
            form_fields = list(formset.forms[0].fields.keys()) if formset.forms else []
            extra_context['form_fields_json'] = json.dumps(form_fields)
            print('\n\nqueryset:\n', self.model.objects.none())
            print('\n\nformset:\n', formset)
            extra_context['title'] = ""
            extra_context['button_name'] = "Добавить"
            extra_context['preview_files'] = get_temp_files(request)
            extra_context['model_name'] = self.model._meta.model_name
            extra_context['app_label'] = self.model._meta.app_label
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        is_popup = '_popup' in request.GET or '_popup' in request.POST
        formset_class = self.get_formset_class(request)
        print('\nadd_view formset_class', formset_class)

        if request.method == 'POST':
            formset = formset_class(request.POST, request.FILES, queryset=self.model.objects.none())
            print('formset.errors', formset.errors)

            if formset.is_valid():
                # Создаем новые объекты, но не сохраняем их сразу
                clear_temp_files(request)
                self._process_related_fields(formset)
                new_objects = formset.save(commit=False)
                # Сохраняем каждый объект
                for new_object in new_objects:
                    print('new_objects', new_object.id)
                    if new_object.id == '':
                        new_object.id = None
                    new_object.save()  # Сохранение объекта в базе

                # Отправляем сообщение об успешном добавлении
                count = len(new_objects)
                if is_popup:
                    return self.response_add(request, new_objects[-1])
                else:
                    msg = 'Записи добавлены.' if count > 1 else '\"%(object)s\" добавлен.' % {'object': new_objects[0]}
                    self.message_user(request, msg, messages.SUCCESS)
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
        extra_context['title'] = ""
        extra_context['button_name'] = "Добавить"
        form_fields = list(formset.forms[0].fields.keys()) if formset.forms else []
        extra_context['form_fields_json'] = json.dumps(form_fields)

        return super().add_view(request,
                                'admin:%s_%s_changelist' % (self.model._meta.app_label, self.model._meta.model_name),
                                extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        is_popup = '_popup' in request.GET or '_popup' in request.POST

        print('\nchange_view Изменение формы', object_id)

        # Получаем существующую запись по ID
        try:
            instance = self.model.objects.get(pk=object_id)
            print(f"Запись с ID {object_id}:", instance)
        except self.model.DoesNotExist:
            instance = None
            print(f"Запись с ID {object_id} не найдена.")

        formset_class = self.get_formset_class(request)
        print('\nchange_view formset_class', formset_class)

        if request.method == 'POST':
            form_action = request.POST.get('form_action', '')
            print('Тип формы:', form_action)

            formset = formset_class(request.POST, request.FILES, queryset=instance)
            print('Форма привязана к существующей записи:', formset.is_bound)
            for i, form in enumerate(formset.forms):
                if hasattr(form.instance, 'request_date'):
                    form.instance.request_date = instance.request_date
                    print('установка request_date для формы', i, '-->', instance.request_date)
                if hasattr(form.instance, 'order_date'):
                    form.instance.order_date = instance.order_date
                    print('установка order_date для формы', i, '-->', instance.order_date)
                if hasattr(form.instance, 'creation_date'):
                    form.instance.creation_date = instance.creation_date
                    print('установка creation_date для формы', i, '-->', instance.creation_date)

            if formset.is_valid():
                print('Форма валидна, файлы:', request.FILES)
                self._process_related_fields(formset)
                updated_object = formset.save(commit=False)[0]
                updated_object.pk = object_id
                print('Обновленные объекты:', updated_object)
                if updated_object:  # Проверяем, что объект уже существует
                    self.save_model(request, updated_object, formset, change=True)
                    print(f"ИЗМЕНЕНИЯ объекта с ID {updated_object.pk} СОХРАНЕНЫ.", updated_object)
                else:
                    print(f"Объект с ID {updated_object.pk} не найден, создается новый объект.", updated_object)
                    self.save_model(request, updated_object, formset, change=False)
                if is_popup:
                    obj_repr = escape(str(updated_object))
                    return HttpResponse(f"""
                        <script type="text/javascript">
                            opener.dismissChangeRelatedObjectPopup(window, "{updated_object.pk}", "{obj_repr}");
                        </script>
                    """)
                else:
                    msg = 'Запись обновлена.'
                    self.message_user(request, msg, messages.SUCCESS)
                    return redirect(request.path)

            else:
                print('Формсет не валиден:', formset.errors)
                save_files_to_session(request, formset)
                extra_context['formset'] = formset
        else:
            # Привязываем форму к существующей записи для GET-запроса
            formset = formset_class(queryset=self.model.objects.filter(pk=object_id))
            extra_context['formset'] = formset

        extra_context['is_popup'] = is_popup
        extra_context['subtitle'] = ""
        if not is_popup:
            extra_context['title'] = ""
        extra_context['button_name'] = "Сохранить"
        print('FORM SET:', list(formset.forms))
        form_fields = list(formset.forms[0].fields.keys()) if formset.forms else []
        extra_context['form_fields_json'] = json.dumps(form_fields)

        response = super().change_view(request, object_id, form_url, extra_context)

        if response is None:
            response = self.render_change_form(request, None, form_url, extra_context)

        return response

