from django.contrib.auth.models import Group, Permission

from .ManageAdmins import ManageAdmins
from .CustomUserAdmin import CustomUserAdmin
from .PivotTableAdmin import PivotTableAdmin
from .__CustomAdminSite import admin_site

from .ModelAccessControlAdmin import RestrictedGroupAdmin, RestrictedPermissionAdmin, ModelAccessControlAdmin

from storage.forms import CategoriesForm, DepartmentsForm, StorageCellsForm, ProjectsForm, \
    ProductRequestForm, OrdersForm, ProductMoviesForm, SuppliersForm, ProductsForm
from storage.models import Suppliers, Categories, Departments, StorageCells, Projects, Products, ProductRequest, \
    Orders, ProductMovies, PivotTable, CustomUser, ModelAccessControl
from storage.admin.TableModelAdmin import TableModelAdmin

admin_site.register(Group, RestrictedGroupAdmin)
admin_site.register(Permission, RestrictedPermissionAdmin)
admin_site.register(ModelAccessControl, ModelAccessControlAdmin)
admin_site.register(CustomUser, CustomUserAdmin)


class SuppliersAdmin(TableModelAdmin):
    form = SuppliersForm
    change_list_template = "admin/table_view.html"
    add_form_template = "admin/table_add.html"
    list_display = ['name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg']
    search_fields = ['name', 'inn', 'ogrn', 'address', 'contact_person', 'website']
    list_filter = ['name']


admin_site.register(Suppliers, SuppliersAdmin)


class ProductsAdmin(TableModelAdmin):
    form = ProductsForm
    # change_form_template = 'admin/table_view.html'

    list_display = ['id', 'name', 'product_sku', 'packaging_unit', 'supplier', 'product_link', 'product_image_tag']
    # 'display_categories' пока не выводим
    search_fields = ['name', 'product_sku']  # 'categories' пока не выводим
    ordering = ['-id']
    list_filter = ['supplier']

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    display_categories.short_description = "Категории / признаки"


admin_site.register(Products, ProductsAdmin)


class CategoriesAdmin(ManageAdmins):
    one_line_add = True
    form = CategoriesForm
    list_display = ('name',)


admin_site.register(Categories, CategoriesAdmin)


class DepartmentsAdmin(ManageAdmins):
    one_line_add = True
    form = DepartmentsForm
    list_display = ['name']
    ordering = ['name']


admin_site.register(Departments, DepartmentsAdmin)


class StorageCellsAdmin(ManageAdmins):
    one_line_add = True
    form = StorageCellsForm
    list_display = ['name', 'info']
    fields = ['name', 'info']
    ordering = ['name']


admin_site.register(StorageCells, StorageCellsAdmin)


class ProjectsAdmin(TableModelAdmin):
    form = ProjectsForm
    tabled_add = True
    list_display = ['id', 'creation_date', 'name', 'detail_full_name', 'manager', 'engineer', 'project_code',
                    'detail_name', 'detail_code']
    search_fields = ['name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code']
    ordering = ['name']
    list_filter = ['creation_date', 'name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name',
                   'detail_code']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'manager':
            kwargs['queryset'] = CustomUser.objects.filter(groups__name='Менеджеры')
        elif db_field.name == 'engineer':
            kwargs['queryset'] = CustomUser.objects.filter(groups__name='Инженеры')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.manager = request.user
            obj.engineer = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Только при создании нового объекта
            form.base_fields['manager'].initial = request.user
            form.base_fields['engineer'].initial = request.user
        return form


admin_site.register(Projects, ProjectsAdmin)


class ProductRequestAdmin(TableModelAdmin):
    form = ProductRequestForm
    tabled_add = True
    list_display = ['id', 'request_date', 'product', 'request_about', 'request_quantity', 'project', 'responsible',
                    'delivery_location', 'delivery_address', 'deadline_delivery_date']
    search_fields = ['product__name', 'project__project_code']
    ordering = ['id', 'request_date', 'product', 'project']
    list_filter = ['request_date', 'product', 'project']


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


class OrdersAdmin(TableModelAdmin):
    form = OrdersForm
    tabled_add = True
    list_display = ['id', 'order_date', 'product_request', 'manager', 'accounted_in_1c', 'invoice_number',
                    'delivery_status', 'documents', 'waiting_date']
    search_fields = ['delivery_status', 'product_request', 'manager', 'invoice_number']
    ordering = ['id', 'delivery_status', 'order_date', 'product_request', 'waiting_date']
    list_filter = ['order_date', 'manager', 'product_request', 'delivery_status']

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


admin_site.register(Orders, OrdersAdmin)


class ProductMoviesAdmin(TableModelAdmin):
    form = ProductMoviesForm
    tabled_add = True
    list_display = ['id', 'record_date', 'product', 'process_type', 'return_to_supplier_reason', 'movie_quantity', 'new_cell',
                    'reason']
    search_fields = ['product', 'process_type', 'new_cell']
    list_filter = ['product', 'process_type', 'new_cell']
    ordering = ['id', 'product', 'process_type', 'new_cell']

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

