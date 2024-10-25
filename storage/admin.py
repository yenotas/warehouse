# from django.http import HttpResponseRedirect
from django.urls import path, include
# from django.urls import reverse
from django.contrib import admin

# from warehouse.urls import router
from .forms import *
from .views import PivotTableViewSet

# from .views import complex_table_view



admin.site.site_header = "ЗАКУПКИ | СКЛАД"
admin.site.site_title = "Панель управления товарной номенклатурой"
admin.site.index_title = "Управление складом и закупками."

admin.site.register(AccessLevels)


class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ('name', 'product_image', 'category', 'supplier', 'product_link', 'product_sku', 'packaging_unit', 'quantity_in_package')
    fields = ('name', 'product_image', 'category', 'supplier', 'product_link', 'product_sku', 'packaging_unit', 'quantity_in_package', 'near_products')

    def get_actions(self, request):
        return []
    search_fields = ['category__name', 'product_name', 'supplier__name']

    class Media:
        js = ('admin/js/add_del_near.js',)


class CategoriesAdmin(admin.ModelAdmin):
    form = CategoriesForm
    list_display = ('name',)
    fields = ('name',)

    def get_actions(self, request):
        return []
    search_fields = ['name']


class EmployeesAdmin(admin.ModelAdmin):
    form = EmployeesForm
    list_display = ('name', 'email', 'tg', 'department', 'position_name')
    fields = ('name', 'email', 'tg', 'department', 'position_name')

    def get_actions(self, request):
        return []
    search_fields = ['name', 'department', 'position_name']


class SuppliersAdmin(admin.ModelAdmin):
    form = SuppliersForm
    list_display = ('name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg')
    fields = ('name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg')

    def get_actions(self, request):
        return []
    search_fields = ['name', 'inn', 'ogrn', 'address', 'contact_person', 'website']


class ProjectsAdmin(admin.ModelAdmin):
    form = ProjectsForm
    list_display = (
    'creation_date', 'name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code')
    fields = (
    'name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code')

    def get_actions(self, request):
        return []
    search_fields = ['name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code']


class ProductRequestAdmin(admin.ModelAdmin):
    form = ProductRequestForm
    list_display = (
    'request_date', 'product', 'project', 'order_about', 'order_quantity', 'responsible_employee', 'delivery_location',
    'delivery_address', 'deadline_delivery_date')
    fields = (
    'product', 'project', 'order_about', 'order_quantity', 'responsible_employee', 'delivery_location',
    'delivery_address', 'deadline_delivery_date')

    def get_actions(self, request):
        return []
    search_fields = ['product', 'project', 'order_about']

    class Media:
        js = ('admin/js/custom_admin.js',)


class OrdersAdmin(admin.ModelAdmin):
    form = OrdersForm
    list_display = (
    'order_date', 'purchase', 'manager', 'accounted_in_1c', 'invoice_number', 'delivery_status', 'documents',
    'waiting_date')
    fields = ('purchase', 'manager', 'accounted_in_1c', 'invoice_number', 'delivery_status', 'documents',
              'waiting_date')

    def get_actions(self, request):
        return []
    search_fields = ['purchase', 'manager', 'invoice_number']


class ProductMoviesAdmin(admin.ModelAdmin):
    form = ProductMoviesForm
    list_display = (
    'record_date', 'product', 'process_type', 'return_to_supplier_reason', 'document_flow', 'employee', 'project',
    'movie_quantity', 'from_cell')
    fields = (
    'product', 'process_type', 'return_to_supplier_reason', 'document_flow', 'employee', 'project',
    'movie_quantity', 'from_cell')

    def get_actions(self, request):
        return []
    search_fields = ['product', 'process_type', 'employee', 'project']


class StorageCellsAdmin(admin.ModelAdmin):
    form = StorageCellsForm
    list_display = ('record_date', 'process_entry', 'stock_quantity', 'cell_address', 'old_cell_address')
    fields = ('process_entry', 'stock_quantity', 'cell_address', 'old_cell_address')

    def get_actions(self, request):
        return []
    search_fields = ['process_entry', 'cell_address', 'old_cell_address']


admin.site.register(Products, ProductAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Employees, EmployeesAdmin)
admin.site.register(Suppliers, SuppliersAdmin)
admin.site.register(Projects, ProjectsAdmin)
admin.site.register(ProductRequest, ProductRequestAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(ProductMovies, ProductMoviesAdmin)
admin.site.register(StorageCells, StorageCellsAdmin)


class PivotTableAdmin(admin.ModelAdmin):
    change_list_template = "complex_table.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('complex-table/',  PivotTableViewSet.as_view({'get': 'list'}), name='complex_table'),
        ]
        return custom_urls + urls
    # PivotTableViewSet.as_view({'get': 'list'}), name='complex_table'),

    # def get_actions(self, request):
    #     return []
    # search_fields = ['name']

admin.site.register(PivotTable, PivotTableAdmin)

from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin


