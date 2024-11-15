import json

from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import modelformset_factory

from .models import *
from dal import autocomplete
from django import forms
from django.contrib.contenttypes.models import ContentType


# class AutoCompleteForms(forms.ModelForm):
#     class Meta:
#         abstract = True
#
#     def __init__(self, *args, **kwargs):
#         self.unique_fields = kwargs.pop('unique_fields', [])
#         self.auto_fields = kwargs.pop('auto_fields', [])
#         super().__init__(*args, **kwargs)
#         self.model_name = self._meta.model._meta.model_name
#
#         for field_name in self.auto_fields:
#             field = self.fields.get(field_name)
#             if field:
#                 # Добавляем атрибуты к виджету поля
#                 field.widget.attrs['field_name'] = field_name
#                 field.widget.attrs['model_name'] = self.model_name
#
#                 # Обновляем класс виджета, добавляя 'single_line_add'
#                 existing_classes = field.widget.attrs.get('class', '')
#                 classes = existing_classes.split()
#                 if 'single_line_add' not in classes:
#                     classes.append('single_line_add')
#                 field.widget.attrs['class'] = ' '.join(classes)
#
#     def clean(self):
#         cleaned_data = super().clean()
#         if self.unique_fields and not self.instance.pk:
#             model_class = self._meta.model
#             filter_args = {field: cleaned_data.get(field) for field in self.unique_fields}
#             if model_class.objects.filter(**filter_args).exists(): raise forms.ValidationError(
#                 "Такая запись уже существует!")
#         return cleaned_data
#
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         for field in self.fields:
#             setattr(instance, field, self.cleaned_data.get(field))
#         if commit:
#             instance.save()
#         return instance
class AutoCompleteForms(forms.ModelForm):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        self.unique_fields = kwargs.pop('unique_fields', [])
        self.auto_fields = kwargs.pop('auto_fields', [])
        related_model_names = self.related_model_mapping = kwargs.pop('related_model_mapping', [])
        self.model_name = self._meta.model._meta.model_name

        super().__init__(*args, **kwargs)

        for field_name in self.auto_fields:
            field = self.fields.get(field_name)
            if field:

                if field_name in related_model_names:
                    field.widget.attrs['model_name'] = related_model_names[field_name][0].lower()
                    field.widget.attrs['field_name'] = related_model_names[field_name][1].lower()
                    print(field.widget.attrs)
                else:
                    field.widget.attrs['field_name'] = field_name.lower()
                    field.widget.attrs['model_name'] = self.model_name.lower()

                # Добавляем CSS-класс для поля автозаполнения
                field.widget.attrs['class'] = 'single_line_add'

    def clean(self):
        cleaned_data = super().clean()
        if self.unique_fields and not self.instance.pk:
            model_class = self._meta.model
            filter_args = {field: cleaned_data.get(field) for field in self.unique_fields}
            if model_class.objects.filter(**filter_args).exists():
                raise forms.ValidationError("Такая запись уже существует!")
        return cleaned_data

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     for field in self.fields:
    #         setattr(instance, field, self.cleaned_data.get(field))
    #     if commit:
    #         instance.save()
    #     return instance


class DepartmentsForm(AutoCompleteForms):
    class Meta:
        model = Departments
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          **kwargs)


class CategoriesForm(AutoCompleteForms):
    class Meta:
        model = Categories
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          **kwargs)


class CustomUserChangeForm(UserChangeForm, AutoCompleteForms):

    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          unique_fields=['username'],
                          auto_fields=['username', 'first_name', 'last_name', 'position_name'],
                          **kwargs)


class CustomUserCreationForm(UserCreationForm, AutoCompleteForms):

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'department', 'position_name', 'tel', 'tg')

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          unique_fields=['username'],
                          auto_fields=['username', 'first_name', 'last_name', 'position_name'],
                          **kwargs)


class ProductsForm(AutoCompleteForms):
    class Meta:
        model = Products
        exclude = ['near_products']

    supplier = forms.ModelChoiceField(
        queryset=Suppliers.objects.all(),
        label='Поставщик',
        widget=forms.TextInput(attrs={'class': 'single_line_add'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            unique_fields=['name', 'supplier'],
            auto_fields=['name', 'supplier'],
            related_model_mapping={'supplier': ['Suppliers', 'name']},
            **kwargs
        )

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #
    #     # Преобразование значения supplier в объект Suppliers
    #     supplier_id = self.cleaned_data.get('supplier')
    #     if supplier_id:
    #         try:
    #             supplier_instance = Suppliers.objects.get(id=supplier_id)
    #             instance.supplier = supplier_instance
    #         except Suppliers.DoesNotExist:
    #             raise forms.ValidationError(f"Поставщик с id {supplier_id} не найден.")
    #
    #     if commit:
    #         instance.save()
    #     return instance


class SuppliersForm(AutoCompleteForms):
    class Meta:
        model = Suppliers
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          **kwargs)


class StorageCellsForm(AutoCompleteForms):
    class Meta:
        model = StorageCells
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name', 'info'],
                          **kwargs)


class ProjectsForm(AutoCompleteForms):
    class Meta:
        model = Projects
        exclude = ['creation_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          **kwargs)


class OrdersForm(AutoCompleteForms):
    class Meta:
        model = Orders
        fields = '__all__'
        # exclude = ['order_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          **kwargs)


class ProductMoviesForm(AutoCompleteForms):
    class Meta:
        model = ProductMovies
        fields = '__all__'
        exclude = ['record_date']
        widgets = {
            'reason_id': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                          unique_fields=['name'],
                          auto_fields=['name'],
                          **kwargs)
        self.fields['reason_id'].required = False


class PivotTableForm(AutoCompleteForms):
    product_name = forms.ModelChoiceField(
        queryset=Products.objects.all(),
        widget=autocomplete.ModelSelect2(url='names-autocomplete'),
        label="Наименование",
        required=True
    )
    responsible = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        widget=autocomplete.ModelSelect2(url='users-autocomplete'),
        label="Ответственный",
        required=False
    )

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


class ProductRequestForm(forms.ModelForm):
    class Meta:
        model = ProductRequest
        exclude = ['request_date']


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
