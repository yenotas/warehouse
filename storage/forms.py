import json
from collections import OrderedDict
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models import ForeignKey, ManyToManyField, F
from django.forms import CharField

from .models import *
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models.functions import Concat
from django.db.models import QuerySet


from django.db.models import Value, TextField
from django.contrib.postgres.search import TrigramSimilarity


def trigram_search(query, queryset, search_field):
    # Создаем аннотацию с триграммным сходством
    queryset = queryset.annotate(
        similarity=TrigramSimilarity(search_field, query)
    ).filter(similarity__gt=0.3).order_by('-similarity')  # Порог сходства можно настроить

    # Если есть совпадения, возвращаем id и имя
    if queryset.exists():
        best_match = queryset.first()
        return best_match.id, getattr(best_match, search_field)
    return None, None

# def trigram_search(query, model_or_queryset, search_field, threshold=0.3):
#     """
#     Универсальная функция триграммного поиска.
#
#     :param query: строка запроса для поиска (например, "Иван Иванов").
#     :param model_or_queryset: модель или QuerySet для поиска.
#     :param search_field: поле, в котором выполняется поиск.
#     :param threshold: порог схожести для поиска (по умолчанию 0.3).
#     :return: tuple (id записи, найденный текст) или None, если ничего не найдено.
#     """
#     if not query or not model_or_queryset or not search_field:
#         raise ValueError("Все параметры (query, model_or_queryset, search_field) обязательны.")
#
#     # Если передана модель, получаем QuerySet
#     if isinstance(model_or_queryset, type) and hasattr(model_or_queryset, 'objects'):
#         queryset = model_or_queryset.objects.all()
#     elif isinstance(model_or_queryset, QuerySet):
#         queryset = model_or_queryset
#     else:
#         raise ValueError("model_or_queryset должен быть либо моделью, либо QuerySet.")
#
#     # Выполняем триграммный поиск
#     result = (
#         queryset.annotate(
#             similarity=TrigramSimilarity(search_field, query)
#         )
#         .filter(similarity__gte=threshold)
#         .order_by('-similarity')
#         .values_list('id', search_field, 'similarity')
#         .first()
#     )
#
#     if result:
#         record_id, record_text, similarity = result
#         return record_id, record_text
#     return None, None


class BaseTableForm(forms.ModelForm):
    related_fields = {}
    model_name = None

    def __init__(self, *args, **kwargs):
        self.unique_fields = kwargs.pop('unique_fields', [])
        self.auto_fields = kwargs.pop('auto_fields', [])
        self.required_fields = kwargs.pop('required_fields', [])
        super().__init__(*args, **kwargs)

        print(f"BaseTableForm. Инициализация формы. Instance: {self.instance}, PK: {self.instance.pk if self.instance else 'None'}")
        # Объединение полей модели для автозаполнения
        if self.related_fields:
            self.auto_fields = list(set(self.auto_fields + [field for field in list(self.related_fields.keys())]))
        # print('Все поля автозаполнения:', self.auto_fields)

        for field_name in self.auto_fields:
            field = self.fields.get(field_name)

            # Обработка связанных полей
            if self.related_fields and field_name in self.related_fields:

                rel_info = self.related_fields.get(field_name, {})
                print('related_field:', field_name, 'INFO:', rel_info)

                rel_model_name = rel_info['model']
                rel_field_name = rel_info.get('field', '__str__')
                rel_filter = rel_info.get('filter', None)
                rel_filter_field = rel_info.get('filter_field', None)

                id_field_name = f"{field_name}_id"
                name_field_name = f"{field_name}_name"
                print('Создаем', id_field_name, name_field_name)

                # Скрытое поле для ID
                self.fields[id_field_name] = forms.IntegerField(widget=forms.HiddenInput(), required=False)
                # Текстовое поле для имени
                self.fields[name_field_name] = forms.CharField(
                    required=False,
                    label=self._meta.model._meta.get_field(field_name).verbose_name,
                    widget=forms.TextInput(attrs={
                        'class': 'auto_complete rel_field',
                        'data-field-name': rel_field_name.lower(),
                        'data-model-name': rel_model_name.lower(),
                        'data-filter': rel_filter,
                        'data-filter-field': rel_filter_field,
                        'required': False,
                    })
                )
                # Если форма создаётся для редактирования
                if self.instance.pk:
                    related_object = getattr(self.instance, field_name, None)
                    if related_object:
                        self.fields[id_field_name].initial = related_object.id
                        self.fields[name_field_name].initial = getattr(related_object, rel_field_name, "")
                # Убираем исходное связанное поле
                if field_name in self.fields:
                    del self.fields[field_name]
                    # self.fields[field_name] = forms.CharField(widget=forms.HiddenInput(), required=False)

            # Обработка несвязанных полей
            else:
                self.model_name = self._meta.model._meta.model_name.lower()
                field.widget.attrs.update({
                    'data-field-name': field_name.lower(),
                    'data-model-name': self.model_name.lower(),
                    'class': field.widget.attrs.get('class', '') + ' auto_complete',
                    'required': False,
                })

        # Переупорядочиваем поля в соответствии с атрибутом fields
        new_order = []
        # print("Meta fields:", getattr(self._meta, 'fields', None))

        for field_name in self._meta.fields:
            if field_name in self.related_fields:
                # Заменяем связанное поле на его новые поля
                id_field_name = f"{field_name}_id"
                name_field_name = f"{field_name}_name"
                new_order.extend([name_field_name, id_field_name])
            else:
                new_order.append(field_name)

        # Создаём новый OrderedDict с полями в нужном порядке
        self.fields = OrderedDict((f, self.fields[f]) for f in new_order if f in self.fields)

        # Отладочная информация
        # print("Поля формы после переименования:", list(self.fields.keys()))

    def clean(self):
        cleaned_data = super().clean()
        print(f"Метод clean. Instance: {self.instance}, PK: {self.instance.pk if self.instance else 'None'}")
        # Проверка уникальности
        if self.unique_fields and not self.instance.pk:
            print('instance', self.instance)
            model_class = self._meta.model
            filter_args = {}

            for field_name in self.fields:
                if field_name in self.unique_fields:
                    print('unique_field', field_name)
                    field_value = cleaned_data.get(field_name)
                    filter_args[field_name] = field_value

                    # Проверка уникальности с учетом редактирования
                    existing_record = model_class.objects.filter(**filter_args).exclude(pk=self.instance.pk).first()
                    if existing_record:
                        print("Запись уже существует", self.instance.pk, existing_record.pk, existing_record)
                        self.add_error(field_name, f"{field_value} - Такая запись уже существует! | ")

        # Проверка заполнения
        if self.required_fields:
            print('required_fields:', self.required_fields)
            model_class = self._meta.model
            filter_args = {}

            for field_name in self.fields:
                if field_name in self.required_fields:
                    print('required_field', field_name)
                    field_value = cleaned_data.get(field_name)

                    if not field_value:
                        filter_args[field_name] = ''
                        self.add_error(field_name, f"- Обязательное поле | ")

            print('required_fields resume:', filter_args)

        if self.auto_fields:
            # Обработка связанных полей
            print('все поля на обработку', self.related_fields.items())
            for rel_field, rel_info in self.related_fields.items():
                print('Проверка rel_info', rel_info)
                rel_model_name = rel_info['model']
                rel_field_name = rel_info.get('field', None)
                rel_filter = rel_info.get('filter', None)

                id_field = f"{rel_field}_id"
                name_field = f"{rel_field}_name" if rel_field in self.related_fields else rel_field
                try:
                    related_model = apps.get_model('storage', rel_model_name)
                except LookupError:
                    raise ValidationError(f"Модель {rel_model_name} не найдена. ")

                rel_id = cleaned_data.get(id_field, None)
                rel_text = cleaned_data.get(name_field, '').strip()

                if not rel_text and rel_field not in self.required_fields:
                    continue

                print(f"Модель {rel_model_name}, поле {name_field}, ищем {rel_text}, id = {rel_id}")

                if rel_id:
                    # Если ID уже существует, сохраняем его и связанный текст
                    cleaned_data[id_field] = rel_id
                    cleaned_data[name_field] = rel_text
                    related_object = related_model.objects.filter(id=rel_id).first()
                    cleaned_data[rel_field] = related_object
                else:
                    if rel_model_name == 'CustomUser':
                        queryset = related_model.objects.annotate(
                            full_name=Concat('first_name', Value(' '), 'last_name')
                        ).all()
                        search_field = 'full_name'
                    elif rel_model_name == 'ProductRequest':
                        queryset = related_model.objects.annotate(
                            product=F('product_link__name')
                        ).all()
                        search_field = 'product'
                    else:
                        queryset = related_model.objects.all()
                        search_field = rel_field_name

                    rel_id, true_value = trigram_search(rel_text, queryset, search_field)
                    if rel_id:
                        print(f"НАЙДЕНО! {true_value} id {rel_id}")
                        cleaned_data[id_field] = rel_id
                        cleaned_data[name_field] = true_value
                        related_object = related_model.objects.filter(id=rel_id).first()
                        cleaned_data[rel_field] = related_object
                    else:
                        # Создаем новую запись (если это разрешено)
                        if getattr(related_model, 'relate_creating', False):
                            related_object = related_model.objects.create(**{rel_field_name: rel_text})
                            # Сохраняем объект в cleaned_data
                            cleaned_data[rel_field] = related_object
                            cleaned_data[id_field] = related_object.id
                            cleaned_data[name_field] = rel_text
                        elif rel_text != '':
                            self.add_error(name_field,f"Откройте форму добавления "
                                                      f"{related_model._meta.verbose_name} (двойной клик на ячейку) | ")
                            continue
            print('Обход связанных полей успешно завершен!')

        return cleaned_data


class ProductsForm(BaseTableForm):

    related_fields = {'supplier': {'model': 'Suppliers', 'field': 'name'}}

    class Meta:
        model = Products
        fields = ['name', 'product_sku', 'packaging_unit', 'supplier', 'product_url', 'product_image']
        exclude = ['id', 'near_products', 'supplier_old', 'categories']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(
            *args,
            auto_fields=['name', 'supplier'],
            required_fields=['name'],
            **kwargs
        )
        self.fields['product_image'].widget.attrs.update({'class': 'product_image'})

        # Если есть экземпляр объекта, передаем ID поставщика в атрибуты виджета
        # if self.instance and self.instance.pk:
        #     supplier_id = self.instance.suppliers__id
        #     if supplier_id:
        #         field = self.fields['supplier']
        #         field.widget.attrs['data-initial-id'] = supplier_id
        # if self.request:
        #     data = self.request.session.get('initial_data')
        #     print('Data loaded from session:', data)  # Отладочный вывод
        #     if data:
        #         data = self.request.session.get('initial_data')
        #         if data:
        #             initial_fields = data.get('fields', {})
        #             m2m_fields = data.get('m2m', {})
        #             # Устанавливаем начальные значения для полей
        #             for field_name, value in initial_fields.items():
        #                 if field_name == 'name':
        #                     continue  # Пропускаем поле 'name'
        #                 field = self.fields.get(field_name)
        #                 if field:
        #                     field.initial = value
        #             # Устанавливаем начальные значения для ManyToMany полей
        #             for field_name, value in m2m_fields.items():
        #                 field = self.fields.get(field_name)
        #                 if field:
        #                     field.initial = value
        #                     print(field, value)
        #             # Удаляем данные из сессии после использования
        #             del self.request.session['initial_data']


class ProjectsForm(BaseTableForm):

    related_fields = {
        'manager': {'model': 'CustomUser', 'filter': 'Менеджеры'},
        'engineer': {'model': 'CustomUser', 'filter': 'Инженеры'},
    }

    class Meta:
        model = Projects
        fields = '__all__'
        exclude = ['manager_old', 'engineer_old']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args,
                         unique_fields=['detail_code'],
                         required_fields=['name', 'detail_full_name', 'manager', 'engineer', 'project_code',
                                          'detail_name', 'detail_code'],
                         auto_fields=['manager', 'engineer', 'name', 'project_code', 'detail_name', 'detail_name',
                                      'detail_full_name'],
                         **kwargs)

        prefix = 'АРХ'
        detail_codes = Projects.objects.filter(detail_code__startswith=prefix).values_list('detail_code', flat=True)
        numbers = [int(code.replace(prefix, '')) for code in detail_codes if code.startswith(prefix)]
        if numbers:
            max_number = max(numbers)
            new_number = max_number + 1
        else:
            new_number = 1

        new_detail_code = f"{prefix}{new_number}"

        self.fields['detail_code'].initial = new_detail_code

    # def clean_detail_code(self):
    #     detail_code = self.cleaned_data.get('name')
    #     if Projects.objects.filter(detail_code=detail_code).exists():
    #         raise forms.ValidationError('Проект с таким кодом уже существует.')
    #     if detail_code == '':
    #         raise forms.ValidationError('Поле должно быть заполнено!')
    #     return detail_code


class OrdersForm(BaseTableForm):

    related_fields = {
        'manager': {'model': 'CustomUser', 'filter': 'Менеджеры'},
        'product_request': {'model': 'ProductRequest', 'field': 'product_link'}
    }

    class Meta:
        model = Orders
        fields = '__all__'
        exclude = ['order_date', 'manager_old', 'product_request_old', 'order_accepted']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(
            *args,
            auto_fields=['manager', 'product_request'],
            **kwargs
        )
        # self.fields['product_request'] = forms.CharField(widget=forms.HiddenInput(), required=False)


class ProductMoviesForm(BaseTableForm):

    related_fields = {
        'product_link': {'model': 'Products', 'field': 'name'},
        'new_cell': {'model': 'StorageCells', 'field': 'name'}
    }

    class Meta:
        model = ProductMovies
        fields = '__all__'
        exclude = ['record_date', 'product_old', 'new_cell_old']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(
            *args,
            auto_fields=['product_link', 'new_cell'],
            **kwargs
        )


class ProductRequestForm(BaseTableForm):

    related_fields = {
        'product_link': {'model': 'Products', 'field': 'name'},
        'project_link': {'model': 'Projects', 'field': 'detail_code'},
        'responsible': {'model': 'CustomUser', 'filter': 'ПДО'},
        'manager': {'model': 'CustomUser', 'filter': 'ПДО'}
        }

    class Meta:
        model = ProductRequest
        fields = '__all__'
        exclude = ['request_date', 'project_old', 'product_old', 'responsible_old', 'request_accepted']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(
            *args,
            auto_fields=['product_link', 'project_link', 'responsible', 'manager'],
            **kwargs
        )
        self.fields['project_link'] = forms.CharField(widget=forms.HiddenInput(), required=False)
        self.fields['product_link'] = forms.CharField(widget=forms.HiddenInput(), required=False)
        # self.fields['responsible'].initial = self.request.user

        # if self.request:
        #     data = self.request.session.get('initial_data')
        #     print('Data loaded from session:', data)  # Отладочный вывод
        #     if data:
        #         data = self.request.session.get('initial_data')
        #         if data:
        #             initial_fields = data.get('fields', {})
        #             m2m_fields = data.get('m2m', {})
        #             # Устанавливаем начальные значения для полей
        #             for field_name, value in initial_fields.items():
        #                 if field_name == 'name':
        #                     continue  # Пропускаем поле 'name'
        #                 field = self.fields.get(field_name)
        #                 if field:
        #                     field.initial = value
        #             # Устанавливаем начальные значения для ManyToMany полей
        #             for field_name, value in m2m_fields.items():
        #                 field = self.fields.get(field_name)
        #                 if field:
        #                     field.initial = value
        #                     print(field, value)
        #             # Удаляем данные из сессии после использования
        #             del self.request.session['initial_data']


class SuppliersForm(BaseTableForm):
    class Meta:
        model = Suppliers
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          required_fields=['name'],
                          **kwargs)


class DepartmentsForm(BaseTableForm):
    class Meta:
        model = Departments
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          **kwargs)
        self.fields['name'].widget.attrs.update({'required': 'required'})


class CategoriesForm(BaseTableForm):
    class Meta:
        model = Categories
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          **kwargs)


class CustomUserChangeForm(UserChangeForm, BaseTableForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          auto_fields=['position_name'],
                          **kwargs)

    def clean_groups(self):
        groups = self.cleaned_data.get('groups')
        admin_group = Group.objects.filter(name='Администраторы').first()

        if admin_group in groups:
            # Проверяем, состоит ли текущий пользователь в группе "Администраторы"
            if not ((self.request and self.request.user.groups.filter(name='Администраторы').exists()) or
                    self.request.user.is_superuser):
                raise ValidationError("Вы не можете добавлять пользователей в группу 'Администраторы'.")

        return groups

    def clean_is_superuser(self):
        is_superuser = self.cleaned_data.get('is_superuser')
        if is_superuser:
            # Проверяем, является ли текущий пользователь суперпользователем
            if not (self.request and self.request.user.is_superuser):
                raise ValidationError("Вы не можете назначать статус суперпользователя.")

        return is_superuser


class CustomUserCreationForm(UserCreationForm, BaseTableForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'department', 'position_name', 'tel', 'tg')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args,
                          auto_fields=['position_name'],
                          **kwargs)


class StorageCellsForm(BaseTableForm):
    class Meta:
        model = StorageCells
        fields = '__all__'
        exclude = ['new_cell_old']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name', 'info'],
                          **kwargs)


class ModelAccessControlForm(forms.ModelForm):
    model_name = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(app_label='storage'),
        label="Правило для формы",
        empty_label="Выберите модель",
        to_field_name="id"
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Группы редакторов"
    )
    fields_to_disable = forms.JSONField(
        required=False,
        label="Отключаемые поля для остальных",
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = ModelAccessControl
        fields = ['model_name', 'groups', 'fields_to_disable']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model_choices = [
            ('', 'Выберите модель'),
            *[(ct.id, ct.model_class()._meta.verbose_name_plural)
              for ct in ContentType.objects.filter(app_label='storage')]
        ]
        self.fields['model_name'].choices = model_choices
        self.fields['model_name'].widget.attrs.update({'class': 'dynamic-model-select'})

        # Обработка сохраненного JSON, если он уже существует
        if isinstance(self.instance.fields_to_disable, list):
            self.initial['fields_to_disable'] = json.dumps(self.instance.fields_to_disable)
        elif isinstance(self.instance.fields_to_disable, str):
            try:
                # Попытка десериализовать, если строка — корректный JSON
                self.initial['fields_to_disable'] = json.loads(self.instance.fields_to_disable)
            except json.JSONDecodeError:
                # Обработка ошибки, если JSON некорректен
                print("Ошибка десериализации JSON в fields_to_disable:", self.instance.fields_to_disable)

    def clean_fields_to_disable(self):
        data = self.cleaned_data['fields_to_disable']
        if isinstance(data, str):
            try:
                # Пробуем десериализовать строку, если это JSON
                data = json.loads(data)
            except json.JSONDecodeError:
                raise ValidationError("Введите корректный JSON.")
        # Убедимся, что результат — список, и преобразуем в JSON-строку
        if not isinstance(data, list):
            raise ValidationError("Ожидается список значений.")
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Сериализация данных перед сохранением
        if isinstance(self.cleaned_data['fields_to_disable'], list):
            instance.fields_to_disable = json.dumps(self.cleaned_data['fields_to_disable'])
        if commit:
            instance.save()
        return instance


class PivotTableForm(BaseTableForm):

    class Meta:
        model = PivotTable
        fields = [
            'product_link',
            'request_about',
            'responsible',
            'invoice_number',
            'waiting_date',
            'delivery_status',
            'document_flow',
            'documents',
            'accounted_in_1c',
        ]
        widgets = {
            'waiting_date': AdminDateWidget(),
            'delivery_status': forms.Select(),
            'document_flow': forms.Select(),
            'documents': forms.Select(),
            'accounted_in_1c': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super(PivotTableForm, self).__init__(*args, **kwargs)
        if self.instance:
            # Инициализируем поля значениями из связанных моделей
            if self.instance.product_request and self.instance.product_request.product:
                self.fields['product_link'].initial = self.instance.product_request.product
            if self.instance.product_request:
                self.fields['request_about'].initial = self.request_about or self.instance.product_request.request_about
                self.fields['responsible'].initial = self.responsible or self.instance.product_request.responsible
            if self.instance.order:
                self.fields['invoice_number'].initial = self.invoice_number or self.instance.order.invoice_number
                self.fields['waiting_date'].initial = self.waiting_date or self.instance.order.waiting_date
                self.fields['delivery_status'].initial = self.delivery_status or self.instance.order.delivery_status
                self.fields['document_flow'].initial = self.document_flow or self.instance.order.document_flow
                self.fields['documents'].initial = self.documents or self.instance.order.documents
                self.fields['accounted_in_1c'].initial = self.accounted_in_1c if self.accounted_in_1c is not None else self.instance.order.accounted_in_1c

    def save(self, commit=True):
        instance = super(PivotTableForm, self).save(commit=False)
        # Обработка создания product_request
        if not instance.product_request and self.cleaned_data.get('product_link'):
            product_link = self.cleaned_data['product_link']
            responsible = self.cleaned_data.get('responsible')
            product_request = ProductRequest.objects.create(
                product_link=product_link,
                responsible=responsible,
                request_about=self.cleaned_data.get('request_about'),
            )
            instance.product_request = product_request

        # Обработка создания order
        if not instance.order and instance.waiting_date:
            order = Orders.objects.create(
                product_request=instance.product_request,
                invoice_number=instance.invoice_number,
                waiting_date=instance.waiting_date,
                delivery_status=instance.delivery_status,
                document_flow=instance.document_flow,
                documents=instance.documents,
                accounted_in_1c=instance.accounted_in_1c,
            )
            instance.order = order

        # Сохраняем и синхронизируем связанные модели
        if commit:
            instance.save()
        return instance


