import json
from collections import OrderedDict

from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models import ForeignKey, ManyToManyField

from .models import *
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.apps import apps
from django.core.exceptions import ValidationError


class AutoCompleteFields(forms.ModelForm):
    class Meta:
        abstract = True

    def get_related_models(self):
        """
        Получает словарь с информацией о связанных моделях из полей модели.
        """
        related_models = {}

        for field in self.Meta.model._meta.get_fields():
            if isinstance(field, (ForeignKey, ManyToManyField)):

                if hasattr(field, 'related_query_name'):
                    related_model_name = field.related_model._meta.model_name
                    related_models[field.name] = {field.related_query_name(): related_model_name}
                    print('поле', field.name, "модель / ключевое поле в модели",
                          related_models[field.name])

        return related_models

    def __init__(self, *args, **kwargs):
        self.unique_fields = kwargs.pop('unique_fields', [])
        self.auto_fields = kwargs.pop('auto_fields', [])
        self.related_fields = kwargs.pop('related_models', None) or self.get_related_models() or {}
        print('related_models:', self.related_fields)
        self.model_name = self._meta.model._meta.model_name
        kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        for field_name in self.auto_fields:
            field = self.fields.get(field_name)
            if field:

                field.label = self._meta.model._meta.get_field(field_name).verbose_name

                if self.related_fields and field_name in self.related_fields:

                    related_model_name, related_field_name = next(
                        iter([(model, field) for model, field in self.related_fields.get(field_name, {}).items()]))
                    field.widget.attrs['data-model-name'] = related_model_name.lower()
                    field.widget.attrs['data-field-name'] = related_field_name.lower()
                    field.widget.attrs['field_name'] = field_name.lower()

                else:
                    field.widget.attrs['data-field-name'] = field_name.lower()
                    field.widget.attrs['data-model-name'] = self.model_name.lower()

                # Добавляем CSS-класс для поля автозаполнения
                existing_classes = field.widget.attrs.get('class', '')
                classes = existing_classes.split()
                if 'auto_complete' not in classes:
                    classes.append('auto_complete')
                field.widget.attrs['class'] = ' '.join(classes)


class BaseAutoCompleteForm(forms.ModelForm):
    related_fields = {}
    model_name = None

    def __init__(self, *args, **kwargs):
        self.unique_fields = kwargs.pop('unique_fields', [])
        self.auto_fields = kwargs.pop('auto_fields', [])
        super().__init__(*args, **kwargs)

        # Обработка полей модели для автозаполнения
        for field_name in self.auto_fields:
            field = self.fields.get(field_name)

            # Обработка связанных полей
            if self.related_fields and field_name in self.related_fields:
                for rel_field, rel_info in self.related_fields.items():
                    rel_model_name = list(rel_info.keys())[0]
                    rel_field_name = rel_info[rel_model_name]

                    id_field_name = f"{rel_field}_id"
                    name_field_name = f"{rel_field}_name"

                    # Скрытое поле для ID
                    self.fields[id_field_name] = forms.IntegerField(widget=forms.HiddenInput(), required=False)
                    # Текстовое поле для имени
                    self.fields[name_field_name] = forms.CharField(
                        required=False,
                        label=self._meta.model._meta.get_field(rel_field).verbose_name,
                        widget=forms.TextInput(attrs={
                            'class': 'auto_complete rel_field',
                            'data-field-name': rel_field_name.lower(),
                            'data-model-name': rel_model_name.lower(),
                            'required': False,
                        })
                    )
                    # Если форма создаётся для редактирования
                    if self.instance.pk:
                        related_object = getattr(self.instance, rel_field, None)
                        if related_object:
                            self.fields[f"{rel_field}_id"].initial = related_object.id
                            self.fields[f"{rel_field}_name"].initial = getattr(related_object, rel_field_name, "")

                    # Скрываем оригинальное связанное поле
                    if rel_field in self.fields:
                        # self.fields[rel_field].widget = forms.HiddenInput()
                        # self.fields[rel_field].required = False
                        # удаляю исходное поле связи
                        del self.fields[rel_field]
            else:
                self.model_name = self._meta.model._meta.model_name.lower()
                field.widget.attrs.update({
                    'data-field-name': field_name.lower(),
                    'data-model-name': self.model_name,
                    'class': field.widget.attrs.get('class', '') + ' auto_complete',
                    'required': False,
                })

        # Переупорядочиваем поля в соответствии с атрибутом fields
        new_order = []
        print("Meta fields:", getattr(self._meta, 'fields', None))

        for field_name in self._meta.fields:
            if field_name in self.fields:
                new_order.append(field_name)
            elif field_name in self.related_fields:
                # Заменяем связанное поле на его новые поля
                id_field_name = f"{field_name}_id"
                name_field_name = f"{field_name}_name"
                new_order.extend([name_field_name, id_field_name])

        # Добавляем остальные поля, которые могли быть добавлены (например, 'id')
        for field_name in self.fields.keys():
            if field_name not in new_order:
                new_order.append(field_name)

        # Создаём новый OrderedDict с полями в нужном порядке
        self.fields = OrderedDict((k, self.fields[k]) for k in new_order if k in self.fields)

    def clean(self):
        cleaned_data = super().clean()

        if self.related_fields:
            # Обработка связанных полей
            for rel_field, rel_info in self.related_fields.items():
                rel_model_name = list(rel_info.keys())[0]
                rel_field_name = rel_info[rel_model_name]

                id_field = f"{rel_field}_id"
                name_field = f"{rel_field}_name"

                # Получаем модель
                try:
                    related_model = apps.get_model('storage', rel_model_name)
                except LookupError:
                    raise ValidationError(f"Модель {rel_model_name} не найдена.")

                if not getattr(related_model, 'relate_creating', False):
                    self.add_error(
                        name_field,
                        f"Откройте форму добавления (двойной клик) для '{related_model._meta.verbose_name}'."
                    )
                    continue

                rel_id = cleaned_data.get(id_field)
                rel_name = cleaned_data.get(name_field)

                related_object = None

                if rel_id:
                    # Если указан ID, проверяем, существует ли запись
                    related_object = related_model.objects.filter(id=rel_id).first()
                    if related_object:
                        # Если имя не совпадает
                        if getattr(related_object, rel_field_name) != rel_name:
                            # Проверяем, существует ли запись с таким именем
                            existing_object = related_model.objects.filter(**{rel_field_name: rel_name}).first()
                            if existing_object:
                                print("Такое имя есть")
                                related_object = existing_object  # Используем существующую запись
                            else:
                                # Создаём новую запись (если это разрешено)
                                related_object = related_model.objects.create(**{rel_field_name: rel_name})
                    else:
                        print(id_field, f"Запись с ID {rel_id} не найдена.")

                if not related_object and rel_name:
                    # Если указан только name, создаём новую запись
                    related_object = related_model.objects.create(**{rel_field_name: rel_name})

                # Связываем объект с cleaned_data
                if related_object:
                    cleaned_data[rel_field] = related_object
                else:
                    self.add_error(name_field, 'Это поле необходимо заполнить.')

        # Проверка уникальности
        if self.unique_fields and not self.instance.pk:
            model_class = self._meta.model
            filter_args = {}

            for field_name in self.fields:
                if field_name in self.unique_fields:
                    print('unique_field', field_name)
                    if field_name + "_name" in self.related_fields:
                        filter_args[field_name.replace('_name', '')] = cleaned_data.get(field_name + "_name")
                    else:
                        filter_args[field_name] = cleaned_data.get(field_name)
            print('unique_fields', filter_args)

            if model_class.objects.filter(**filter_args).exists():
                raise ValidationError("Такая запись уже существует!")

        return cleaned_data


class ProductsForm(BaseAutoCompleteForm):

    class Meta:
        model = Products
        fields = ['name', 'product_sku', 'packaging_unit', 'supplier', 'product_link', 'product_image']
        exclude = ['near_products', 'supplier_old', 'categories']

    related_fields = {'supplier': {'Suppliers': 'name'}}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(
            *args,
            auto_fields=['name', 'supplier'],
            **kwargs
        )
        self.fields['name'].widget.attrs.update({'required': 'required'})
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


class SuppliersForm(BaseAutoCompleteForm):
    class Meta:
        model = Suppliers
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          **kwargs)
        self.fields['name'].widget.attrs.update({'required': 'required'})


class DepartmentsForm(BaseAutoCompleteForm):
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


class CategoriesForm(BaseAutoCompleteForm):
    class Meta:
        model = Categories
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          **kwargs)


class CustomUserChangeForm(UserChangeForm, BaseAutoCompleteForm):
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
            if not (self.request and self.request.user.groups.filter(name='Администраторы').exists()):
                raise ValidationError("Вы не можете добавлять пользователей в группу 'Администраторы'.")

        return groups

    def clean_is_superuser(self):
        is_superuser = self.cleaned_data.get('is_superuser')
        if is_superuser:
            # Проверяем, является ли текущий пользователь суперпользователем
            if not (self.request and self.request.user.is_superuser):
                raise ValidationError("Вы не можете назначать статус суперпользователя.")

        return is_superuser


class CustomUserCreationForm(UserCreationForm, BaseAutoCompleteForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'department', 'position_name', 'tel', 'tg')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args,
                          auto_fields=['position_name'],
                          **kwargs)


class StorageCellsForm(BaseAutoCompleteForm):
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


class ProjectsForm(BaseAutoCompleteForm):

    manager = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label="Менеджер",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        initial=None,
        empty_label='---------',
    )
    engineer = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label="Инженер",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        initial=None,
        empty_label='---------',
    )

    class Meta:
        model = Projects
        fields = '__all__'
        exclude = ['manager_old', 'engineer_old']

        def __init__(self, *args, **kwargs):
            self.request = kwargs.pop('request', None)
            super().__init__(*args,
                             unique_fields=['detail_code'],
                             auto_fields=['name', 'project_code', 'detail_name', 'detail_name', 'detail_full_name'],
                             **kwargs)
            self.fields['manager'].initial = None
            self.fields['engineer'].initial = None


class OrdersForm(BaseAutoCompleteForm):

    manager = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label="Менеджер",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        initial=None,
        empty_label='---------',
    )

    class Meta:
        model = Orders
        fields = '__all__'
        exclude = ['order_date', 'manager_old', 'product_request_old']

    related_fields = {'product_request': {'ProductRequest': 'product'}}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(
            *args,
            auto_fields=['product_request'],
            **kwargs
        )
        self.fields['manager'].initial = None


class ProductMoviesForm(BaseAutoCompleteForm):
    class Meta:
        model = ProductMovies
        fields = '__all__'
        exclude = ['record_date', 'product_old', 'new_cell_old']

    related_fields = {'product': {'Products': 'name'}, 'new_cell': {'StorageCells': 'name'}}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(
            *args,
            auto_fields=['product', 'new_cell'],
            **kwargs
        )


class ProductRequestForm(BaseAutoCompleteForm):

    responsible = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label="Ответственный",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label='---------',
        initial=None,
    )
    class Meta:
        model = ProductRequest
        exclude = ['request_date', 'project_old', 'product_old', 'responsible_old']

    related_fields = {'product': {'Products': 'name'}, 'project': {'Projects': 'name'}}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(
            *args,
            auto_fields=['product', 'project'],
            **kwargs
        )
        self.fields['responsible'].initial = None

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


from django.core.exceptions import ValidationError


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


class PivotTableForm(BaseAutoCompleteForm):
    # product_name = forms.ModelChoiceField(
    #     queryset=Products.objects.all(),
    #     widget=forms.TextInput(attrs={'class': 'rel_field'}),
    #     label="Наименование",
    #     required=True
    # )
    # responsible = forms.ModelChoiceField(
    #     queryset=CustomUser.objects.all(),
    #     widget=forms.TextInput(attrs={'class': 'rel_field'}),
    #     label="Ответственный",
    #     required=False
    # )

    class Meta:
        model = PivotTable
        fields = [
            'product_name',
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
                self.fields['product_name'].initial = self.instance.product_request.product
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
        if not instance.product_request and self.cleaned_data.get('product_name'):
            product = self.cleaned_data['product_name']
            responsible = self.cleaned_data.get('responsible')
            product_request = ProductRequest.objects.create(
                product=product,
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


