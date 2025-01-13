from django.contrib.auth.models import Group, Permission
from django.utils.html import format_html

from .__CustomAdminSite import admin_site
from .ManageAdmins import ManageAdmins
from .CustomUserAdmin import CustomUserAdmin
from .TableModelAdmin import TableModelAdmin
from .PivotTableAdmin import PivotTableAdmin
from .ModelAccessControlAdmin import RestrictedGroupAdmin, RestrictedPermissionAdmin, ModelAccessControlAdmin

from storage.forms import CategoriesForm, DepartmentsForm, StorageCellsForm, ProjectsForm, \
    ProductRequestForm, OrdersForm, ProductMoviesForm, SuppliersForm, ProductsForm
from storage.models import Suppliers, Categories, Departments, StorageCells, Projects, Products, ProductRequest, \
    Orders, ProductMovies, PivotTable, CustomUser, ModelAccessControl

admin_site.register(Group, RestrictedGroupAdmin)
admin_site.register(Permission, RestrictedPermissionAdmin)
admin_site.register(ModelAccessControl, ModelAccessControlAdmin)
admin_site.register(CustomUser, CustomUserAdmin)


class SuppliersAdmin(TableModelAdmin):
    form = SuppliersForm
    change_list_template = "admin/table_view.html"
    add_form_template = "admin/table_add.html"
    list_display = ['id', 'name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg']
    search_fields = ['name', 'inn', 'ogrn', 'address', 'contact_person', 'website']
    list_filter = ['name']


admin_site.register(Suppliers, SuppliersAdmin)


class ProductsAdmin(TableModelAdmin):
    form = ProductsForm
    # change_form_template = 'admin/table_view.html'
    list_display = ['id', 'name', 'product_sku', 'packaging_unit', 'supplier', 'product_url', 'get_product_image_tag']
    # 'display_categories' пока не выводим
    search_fields = ['name', 'product_sku']  # 'categories' пока не выводим
    ordering = ['-id']
    list_filter = ['supplier']

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = "Категории / признаки"

    def get_product_image_tag(self, obj):
        print(f"Calling product_image_tag for {obj}")
        if obj.product_image:
            return format_html(
                '<a href="#" onclick="window.open(\'{}\', \'ImageView\', \'width=500,height=500,toolbar=no,location=no,menubar=no,scrollbars=no,resizable=yes\'); return false;">'
                '<img src="{}" class="img-preview" /></a>',
                obj.product_image.url,
                obj.product_image.url
            )
        return "—"
    get_product_image_tag.short_description = 'Фото товара'


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
    list_display = ['id', 'creation_date', 'name', 'detail_fullname', 'manager', 'engineer', 'project_code',
                    'detail', 'detail_code']
    search_fields = ['name', 'detail_fullname', 'project_code', 'detail', 'detail_code']
    ordering = ['-id']
    list_filter = ['creation_date', 'name', 'detail_fullname', 'manager', 'engineer', 'project_code', 'detail',
                   'detail_code']

    def save_model(self, request, obj, form, change):
        # Добавляем отладочную информацию
        print(f"Before save: manager={obj.manager}, engineer={obj.engineer}")

        if not change:
            if not obj.manager:
                obj.manager = request.user
            if not obj.engineer:
                obj.engineer = request.user

        # Отладочная информация после возможных изменений
        print(f"After save: manager={obj.manager}, engineer={obj.engineer}")

        super().save_model(request, obj, form, change)


admin_site.register(Projects, ProjectsAdmin)


class ProductRequestAdmin(TableModelAdmin):
    form = ProductRequestForm
    tabled_add = True
    list_display = ['id', 'request_date', 'product', 'request_about', 'request_quantity', 'project',
                    'responsible', 'delivery_location', 'delivery_address', 'deadline_delivery_date', 'buyer']
    search_fields = ['product__name']
    ordering = ['-id']
    list_filter = ['request_date', 'product', 'project', 'buyer']
    readonly_fields = ('request_date',)

    def save_model(self, request, obj, form, change):
        if not obj.responsible and request.user.has_perm('storage.change_responsible'):
            obj.responsible = request.user or None
        else:
            obj.responsible = None
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj and request.user.has_perm('storage.change_responsible'):
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
            kwargs['queryset'] = CustomUser.objects.exclude(groups__name__in=['ПДО']).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.manager and request.user.has_perm('storage.change_responsible'):  # Только при создании нового объекта
            obj.manager = request.user or None
        else:
            obj.responsible = None
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj and request.user.has_perm('storage.change_responsible'):  # Только при создании нового объекта
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


