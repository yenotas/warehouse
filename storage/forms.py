from django import forms
from .models import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = '__all__'


class EmployeesForm(forms.ModelForm):
    class Meta:
        model = Employees
        fields = ['name', 'email', 'tg', 'department', 'position_name']


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


class StorageCellsForm(forms.ModelForm):
    class Meta:
        model = StorageCells
        fields = '__all__'
        exclude = ['record_date']


# class PivotTableForm(forms.ModelForm):
#     class Meta:
#         model = PivotTable
#         fields = '__all__'


class CategoriesForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['name']


class ProductRequestForm(forms.ModelForm):
    class Meta:
        model = ProductRequest
        fields = '__all__'
        exclude = ['request_date']


class CustomForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Products.objects.all())
    supplier = forms.ModelChoiceField(queryset=Suppliers.objects.all())
    responsible_employee = forms.ModelChoiceField(queryset=Employees.objects.all())
    custom_field = forms.CharField(max_length=255)


