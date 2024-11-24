from django.contrib.auth.models import Group, Permission

from .CustomUserAdmin import CustomUserAdmin
from .ProductsAdmin import ProductsAdmin
from .PivotTableAdmin import PivotTableAdmin
from .__CustomAdminSite import admin_site
from .__AutoCompleteAdmins import AutoCompleteAdmins
from .ModelAccessControlAdmin import RestrictedGroupAdmin, RestrictedPermissionAdmin, ModelAccessControlAdmin

from storage.forms import SuppliersForm, CategoriesForm, DepartmentsForm, StorageCellsForm, ProjectsForm, \
    ProductRequestForm, OrdersForm, ProductMoviesForm
from storage.models import Suppliers, Categories, Departments, StorageCells, Projects, Products, ProductRequest, \
    Orders, ProductMovies, PivotTable, CustomUser, ModelAccessControl


admin_site.register(Group, RestrictedGroupAdmin)
admin_site.register(Permission, RestrictedPermissionAdmin)
admin_site.register(ModelAccessControl, ModelAccessControlAdmin)
admin_site.register(CustomUser, CustomUserAdmin)


class SuppliersAdmin(AutoCompleteAdmins):
    form = SuppliersForm
    list_display = ('name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg')
    fields = ('name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg')
    search_fields = ['name', 'inn', 'ogrn', 'address', 'contact_person', 'website']
    ordering = ('name',)
    list_filter = ('name',)


admin_site.register(Suppliers, SuppliersAdmin)


class CategoriesAdmin(AutoCompleteAdmins):
    one_line_add = True
    form = CategoriesForm
    fields = ('name',)
    list_display = ('name',)
    ordering = ['name']


admin_site.register(Categories, CategoriesAdmin)


class DepartmentsAdmin(AutoCompleteAdmins):
    one_line_add = True
    form = DepartmentsForm
    fields = ('name',)
    list_display = ('name',)
    ordering = ['name']


admin_site.register(Departments, DepartmentsAdmin)


class StorageCellsAdmin(AutoCompleteAdmins):
    one_line_add = True
    form = StorageCellsForm
    list_display = ('name', 'info')
    fields = ('name', 'info')
    ordering = ('name',)
    list_filter = ('name',)


admin_site.register(StorageCells, StorageCellsAdmin)


class ProjectsAdmin(AutoCompleteAdmins):
    form = ProjectsForm
    list_display = (
    'id', 'creation_date', 'name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code')
    fields = (
    'name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code')
    search_fields = ['name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code']
    ordering = ('name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code')
    list_filter = ('name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'manager':
            kwargs['queryset'] = CustomUser.objects.filter(groups__name='Менеджеры')
        elif db_field.name == 'engineer':
            kwargs['queryset'] = CustomUser.objects.filter(groups__name='Инженеры')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.manager = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['manager'].initial = request.user
        return form

    def get_actions(self, request):
        return []


admin_site.register(Projects, ProjectsAdmin)

admin_site.register(Products, ProductsAdmin)


class ProductRequestAdmin(AutoCompleteAdmins):
    form = ProductRequestForm
    list_display = (
    'id', 'request_date', 'product', 'request_about', 'request_quantity', 'project', 'responsible', 'delivery_location',
    'delivery_address', 'deadline_delivery_date')
    fields = (
    'product', 'request_about', 'request_quantity', 'project', 'responsible', 'delivery_location',
    'delivery_address', 'deadline_delivery_date')
    search_fields = ['product__name', 'project__project_code']
    ordering = ('id', 'request_date', 'product', 'project')
    list_filter = ('request_date', 'product', 'project')

    def get_actions(self, request):
        return []

    def save_model(self, request, obj, form, change):
        if not change:
            obj.responsible = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['responsible'].initial = request.user
        return form


admin_site.register(ProductRequest, ProductRequestAdmin)


class OrdersAdmin(AutoCompleteAdmins):
    form = OrdersForm
    list_display = ('id', 'order_date', 'product_request', 'manager', 'accounted_in_1c', 'invoice_number', 'delivery_status',
                    'documents', 'waiting_date')
    fields = ('product_request', 'manager', 'accounted_in_1c', 'invoice_number', 'delivery_status', 'documents',
                     'waiting_date')
    # search_fields = ['delivery_status', 'product_request', 'manager', 'invoice_number']
    # ordering = ('id', 'delivery_status', 'order_date', 'product_request', 'waiting_date')
    # list_filter = ('order_date', 'manager', 'product_request', 'delivery_status')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'manager':
            kwargs['queryset'] = CustomUser.objects.exclude(groups__name__in=['Инженеры']).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:  # Только при создании нового объекта
            obj.manager = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Только при создании нового объекта
            form.base_fields['manager'].initial = request.user
        return form

    def get_actions(self, request):
        return []


admin_site.register(Orders, OrdersAdmin)


class ProductMoviesAdmin(AutoCompleteAdmins):
    form = ProductMoviesForm
    list_display = ('record_date', 'product', 'process_type', 'return_to_supplier_reason', 'movie_quantity', 'new_cell',
                    'reason_id')
    fields = ('product', 'process_type', 'return_to_supplier_reason', 'movie_quantity', 'new_cell',
              'reason_id')
    search_fields = ['product', 'process_type', 'new_cell']
    list_filter = ('product', 'process_type', 'new_cell')
    ordering = ('product', 'process_type', 'new_cell')

    def get_actions(self, request):
        return []

    class Media:
        js = ('admin/js/admin/ChangeProductMovies.js',)


admin_site.register(ProductMovies, ProductMoviesAdmin)
admin_site.register(PivotTable, PivotTableAdmin)

from django.apps import apps
storage_models = apps.get_app_config('storage').get_models()
print('\n\n', storage_models)
print('\n\n')
for model, model_admin in admin_site._registry.items():
    opts = model._meta
    print('%s:%s_%s_change' % (admin_site.name, opts.app_label, opts.model_name))

