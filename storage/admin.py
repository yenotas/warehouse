from django.http import HttpResponseRedirect
from django.urls import path
from django.urls import reverse
from django.contrib import admin

from .forms import *
from .views import complex_table_view


class MyAdminSite(admin.AdminSite):
    site_header = "ЗАКУПКИ | СКЛАД"
    site_title = "Панель управления товарной номенклатурой"
    index_title = "Управление складом и закупками."

    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        user_groups = request.user.groups.values_list('name', flat=True)

        if 'admin' in user_groups:
            self.site_header = "Архитекция: Панель управления [АДМИН]"
            return app_list

        filtered_app_list = []
        for app in app_list:
            filtered_models = []
            for model in app['models']:
                if model['perms']['view'] or model['perms']['add']:  # Права на просмотр или добавление
                    filtered_models.append(model)
            if filtered_models:
                app['models'] = filtered_models
                filtered_app_list.append(app)

        print(user_groups)
        print(filtered_app_list)

        if 'manager' in user_groups:
            return [app for app in filtered_app_list if app['name'] == 'Orders' or app['name'] == 'Products']

        if 'purchase' in user_groups:
            return [app for app in filtered_app_list if app['name'] == 'ProductRequest' or app['name'] == 'Suppliers']

        if 'storage' in user_groups:
            return [app for app in filtered_app_list if app['name'] == 'Warehouse' or app['name'] == 'StorageCells']

        if 'planner' in user_groups:
            return [app for app in filtered_app_list if app['name'] == 'Projects' or app['name'] == 'Products']

        return []

    def has_permission(self, request):
        user_groups = request.user.groups.values_list('name', flat=True)
        allowed_groups = ['admin', 'manager', 'purchase', 'storage', 'planner']
        return bool(set(user_groups).intersection(allowed_groups)) or request.user.is_superuser


# admin_site = MyAdminSite(name='myadmin')

admin_site = admin.site
admin_site.site_header = "ЗАКУПКИ | СКЛАД"
admin_site.site_title = "Панель управления товарной номенклатурой"
admin_site.index_title = "Управление складом и закупками."

admin_site.register(AccessLevels)
# admin_site.register(PivotTable)


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


admin_site.register(Products, ProductAdmin)
admin_site.register(Categories, CategoriesAdmin)
admin_site.register(Employees, EmployeesAdmin)
admin_site.register(Suppliers, SuppliersAdmin)
admin_site.register(Projects, ProjectsAdmin)
admin_site.register(ProductRequest, ProductRequestAdmin)
admin_site.register(Orders, OrdersAdmin)
admin_site.register(ProductMovies, ProductMoviesAdmin)
admin_site.register(StorageCells, StorageCellsAdmin)


class PivotTableAdmin(admin.ModelAdmin):
    change_list_template = "admin/storage/complex_table.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('admin/storage/', self.admin_site.admin_view(complex_table_view), name='complex_table'),
            path('pivottable-test/', self.admin_site.admin_view(complex_table_view), name='complex_table'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        if request.GET.get("next") == "complex_table":
            return HttpResponseRedirect(reverse('admin:complex_table'))
        return super().changelist_view(request, extra_context)

    def get_actions(self, request):
        return []
    search_fields = ['product']


admin.site.register(PivotTable, PivotTableAdmin)

from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin


