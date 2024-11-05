import json

from .admin import AccessControlMixin
from .models import *
from dal import autocomplete
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.contenttypes.models import ContentType
from .mixins import AccessControlMixin


class CustomUserForm(AccessControlMixin, forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Departments.objects.all(),
        widget=autocomplete.ModelSelect2(url='departments-autocomplete'),
        label="Отдел/Цех"
    )

    class Meta:
        model = CustomUser
        fields = '__all__'


class GroupForm(AccessControlMixin, forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Categories.objects.all(),
        widget=autocomplete.ModelSelect2(url='categories-autocomplete'),
        label="Категория"
    )

    class Meta:
        model = Products
        fields = '__all__'


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
            'reason': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].required = False


class StorageCellsForm(forms.ModelForm):
    class Meta:
        model = StorageCells
        fields = '__all__'


class PivotTableForm(forms.ModelForm):
    class Meta:
        model = PivotTable
        fields = '__all__'


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
