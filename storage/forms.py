import json

from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import modelformset_factory

from .models import *
from dal import autocomplete
from django import forms
from django.contrib.contenttypes.models import ContentType


class CustomUserChangeForm(UserChangeForm):
    department = forms.ModelChoiceField(
        queryset=Departments.objects.all(),
        widget=autocomplete.ModelSelect2(url='departments-autocomplete'),
        label="Отдел/Цех",
        required=False
    )

    class Meta:
        model = CustomUser
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    department = forms.ModelChoiceField(
        queryset=Departments.objects.all(),
        widget=autocomplete.ModelSelect2(url='departments-autocomplete'),
        label="Отдел/Цех",
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'department', 'position_name', 'tel', 'tg')


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Categories.objects.all(),
        widget=autocomplete.ModelSelect2(url='categories-autocomplete'),
        label="Категория"
    )

    class Meta:
        model = Products
        exclude = ['near_products']


class SuppliersForm(forms.ModelForm):
    class Meta:
        model = Suppliers
        fields = '__all__'


class ProjectsForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = '__all__'
        exclude = ['creation_date']


class OrdersForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = '__all__'
        exclude = ['order_date']


class ProductMoviesForm(forms.ModelForm):
    class Meta:
        model = ProductMovies
        fields = '__all__'
        exclude = ['record_date']
        widgets = {
            'reason_id': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason_id'].required = False


class StorageCellsForm(forms.ModelForm):
    class Meta:
        model = StorageCells
        fields = '__all__'


class PivotTableForm(forms.ModelForm):
    product_name = forms.ModelChoiceField(
        queryset=Products.objects.all(),
        widget=autocomplete.ModelSelect2(url='products-autocomplete'),
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
                # Заполните другие необходимые поля
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
                # Заполните другие необходимые поля
            )
            instance.order = order

        # Сохраняем и синхронизируем связанные модели
        if commit:
            instance.save()
        return instance


# PivotTableFormSet = modelformset_factory(PivotTable, form=PivotTableForm, extra=0)


class CategoriesForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['name']


class ProductRequestForm(forms.ModelForm):
    class Meta:
        model = ProductRequest
        fields = '__all__'
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
