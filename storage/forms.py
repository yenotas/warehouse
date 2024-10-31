from .models import *
from dal import autocomplete
from django import forms


class CustomUserForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Departments.objects.all(),
        widget=autocomplete.ModelSelect2(url='departments-autocomplete'),
        label="Отдел/Цех"
    )

    class Meta:
        model = CustomUser
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





