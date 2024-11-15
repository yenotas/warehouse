from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import *
from .mixins import AccessControlMixin
from .models import CustomUser, ModelAccessControl, Departments
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin, GroupAdmin as DefaultGroupAdmin
from django.apps import apps
from django.contrib.admin import ModelAdmin
import json


class AutoCompleteAdmins(AccessControlMixin, admin.ModelAdmin):

    change_list_template = "admin/change_list.html"  # стандартный шаблон по умолчанию

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, 'one_line_add', False):
            self.change_list_template = "admin/one_line_add.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        form = self.form(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                self.message_user(request, "Добавлено успешно")
                return redirect(request.path)

        extra_context['form'] = form
        return super().changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and not request.user.groups.filter(name__in=['Администраторы']).exists():
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    class Media:
        js = ('admin/js/admin/AutoFields.js',)

    def has_add_permission(self, request, obj=None):
        if getattr(self, 'one_line_add', False) and request.path.endswith(f'/{self.model._meta.model_name}/'):
            return False
        return super().has_add_permission(request)
        # return request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы']).exists()


class RestrictedGroupAdmin(DefaultGroupAdmin):
    """
    Класс для ограничения доступа к редактированию групп и разрешений
    """
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_actions(self, request):
        return []


class RestrictedPermissionAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Админская модель для ModelAccessControl
class ModelAccessControlAdmin(admin.ModelAdmin):
    form = ModelAccessControlForm
    list_display = ['get_verbose_model_name', 'display_groups', 'get_disabled_fields_list']

    def get_verbose_model_name(self, obj):
        content_type = ContentType.objects.get_for_id(obj.model_name_id)
        return content_type.model_class()._meta.verbose_name_plural

    get_verbose_model_name.short_description = "Правило для формы"

    def get_disabled_fields_list(self, obj):
        fields = json.loads(obj.fields_to_disable) if isinstance(obj.fields_to_disable, str) else obj.fields_to_disable
        verbose_names = []

        content_type = ContentType.objects.get_for_id(obj.model_name_id)
        model_class = content_type.model_class()
        for field_name in fields:
            field = model_class._meta.get_field(field_name)
            verbose_names.append(str(field.verbose_name).capitalize())

        return ", ".join(verbose_names)

    get_disabled_fields_list.short_description = "Отключаемые поля для остальных"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        instance = self.get_object(request, object_id)
        extra_context = extra_context or {}
        if instance:
            saved_fields = instance.fields_to_disable
            if isinstance(saved_fields, str):
                try:
                    saved_fields = json.loads(saved_fields)
                except json.JSONDecodeError:
                    saved_fields = []
            extra_context['model_id'] = instance.model_name.id
            extra_context['fields_to_disable'] = mark_safe(json.dumps(saved_fields))
        return super().change_view(request, object_id, form_url, extra_context)

    def get_actions(self, request):
        return []

    class Media:
        js = ('admin/js/admin/getModelFields.js',)


# Кастомный класс AdminSite
class CustomAdminSite(admin.AdminSite):
    site_header = "ЗАКУПКИ | СКЛАД"
    site_title = "Панель управления товарной номенклатурой"
    index_title = "Управление складом и закупками."

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label=app_label)

        model_order = ['PivotTable', 'Products', 'Suppliers', 'Categories', 'ProductRequest', 'Orders', 'ProductMovies', 'Projects', 'StorageCells', 'Users', 'Groups' 'Departments',]
        if not request.user.is_superuser:
            for app in app_list:
                app['models'] = [
                    model for model in app['models']
                    if model['object_name'] not in ['LogEntry', 'Session', 'ContentType', 'Group', 'Permission']
                ]
        for app in app_list:
            app['models'].sort(key=lambda x: model_order.index(x['object_name'])
                               if x['object_name'] in model_order else len(model_order))
        return app_list


# Создаем экземпляр кастомного AdminSite
admin_site = CustomAdminSite(name='myadmin')
admin_site.register(Group, RestrictedGroupAdmin)
admin_site.register(Permission, RestrictedPermissionAdmin)
admin_site.register(ModelAccessControl, ModelAccessControlAdmin)


# Кастомная модель UserAdmin
class CustomUserAdmin(AutoCompleteAdmins):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'full_name', 'department_display', 'email')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'email', 'tel', 'tg', 'department', 'position_name')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'tel', 'tg', 'department', 'position_name'),
        }),
    )
    list_filter = ('department', 'groups')

    def get_fieldsets(self, request, obj=None):
        if not request.user.is_superuser and not request.user.groups.filter(name__in=['Администраторы', 'ОК']).exists():
            # Добавляем поле 'password' для отображения ссылки «Сменить пароль»
            return (
                (None, {'fields': ('username', 'password')}),
                ('Личная информация', {'fields': ('first_name', 'last_name', 'email', 'tel', 'tg', 'department', 'position_name')}),
            )
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы', 'ОК']).exists():
            return self.readonly_fields
        else:
            # Не делаем поле 'password' только для чтения
            readonly_fields = [f.name for f in self.model._meta.fields if f.name not in ('first_name', 'last_name', 'email', 'tel', 'tg', 'department', 'position_name', 'password')]
            return readonly_fields

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Имя и Фамилия'

    def department_display(self, obj):
        return obj.department if obj.department else "—"
    department_display.short_description = 'Отдел/Цех'

    # Методы разрешений остаются без изменений
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы', 'ОК']).exists():
            return True
        if obj is None or obj == request.user:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы', 'ОК']).exists():
            return True
        if obj == request.user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы', 'ОК']).exists()

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы', 'ОК']).exists()

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and not request.user.groups.filter(name__in=['Администраторы']).exists():
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions


admin_site.register(CustomUser, CustomUserAdmin)


class SuppliersAdmin(AutoCompleteAdmins):
    form = SuppliersForm
    list_display = ('name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg')
    fields = ('name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg')
    search_fields = ['name', 'inn', 'ogrn', 'address', 'contact_person', 'website']
    ordering = ('name',)
    list_filter = ('name',)


admin_site.register(Suppliers, SuppliersAdmin)


class ProductsAdmin(AutoCompleteAdmins):
    form = ProductsForm

    list_display = ('name', 'product_sku', 'product_link', 'product_image_tag', 'display_categories', 'supplier')
    fields = ('name', 'product_sku', 'product_link', 'product_image', 'categories', 'supplier', 'packaging_unit',
              'quantity_in_package',)
    search_fields = ['categories__name', 'name', 'supplier__name', 'product_sku']
    ordering = ('categories__name', 'name', 'supplier__name')
    # list_filter = ('category__name', 'name', 'supplier__name')
    # autocomplete_fields = ['name']

    def display_categories(self, obj): return ", ".join([category.name for category in obj.categories.all()])

    display_categories.short_description = "Категории / признаки"


admin_site.register(Products, ProductsAdmin)


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
    search_fields = ['delivery_status', 'product_request', 'manager', 'invoice_number']
    ordering = ('id', 'delivery_status', 'order_date', 'product_request', 'waiting_date')
    list_filter = ('order_date', 'manager', 'product_request', 'delivery_status')

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


admin.register(Orders, OrdersAdmin)


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


class PivotTableAdmin(AutoCompleteAdmins):
    form = PivotTableForm
    fields = ('product_name', 'product_link', 'request_about', 'packaging_unit', 'request_quantity',
        'project_code', 'detail_name', 'detail_code', 'request_date',
        'responsible', 'delivery_location', 'deadline_delivery_date', 'waiting_date', 'has_on_storage',
        'supplier', 'invoice_number', 'delivery_status', 'not_delivered_pcs',
        'document_flow', 'documents', 'accounted_in_1c', 'supply_date', 'supply_quantity', 'storage_cell',)
    list_display = (
        'product_name', 'product_link', 'request_about', 'packaging_unit', 'request_quantity',
        'project_code', 'detail_name', 'detail_code', 'product_image_tag', 'request_date',
        'responsible', 'delivery_location', 'deadline_delivery_date', 'waiting_date', 'has_on_storage',
        'order_complete', 'supplier', 'invoice_number', 'delivery_status', 'not_delivered_pcs',
        'document_flow', 'documents', 'accounted_in_1c', 'supply_date', 'supply_quantity', 'storage_cell',
    )
    list_editable = (
        'request_about', 'invoice_number', 'waiting_date', 'delivery_status', 'document_flow',
        'documents', 'accounted_in_1c'
    )
    autocomplete_fields = ['product_name']
    search_fields = ['product_name__name']
    list_filter = ('order__delivery_status', 'product_request__project__project_code')
    ordering = ('id',)

    def order_complete(self, obj):
        return obj.order_complete
    order_complete.short_description = 'Заказ оформлен'
    order_complete.boolean = True

    # Фильтрация по дате заявки
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            qs = qs.filter(
                Q(product_request__request_date__gte=start_date) &
                Q(product_request__request_date__lte=end_date)
            )
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.order:
            # Блокируем поля, если уже существует заказ
            readonly_fields += ['product_name', 'request_quantity', 'project_code', 'delivery_location',
                                'deadline_delivery_date']
        return readonly_fields

    class Media:
        js = ('admin/js/admin/AddPivotPosition.js',)  # Подключаем дополнительные скрипты для автозаполнения


admin_site.register(PivotTable, PivotTableAdmin)


storage_models = apps.get_app_config('storage').get_models()
print('\n\n', storage_models)
print('\n\n')
for model, model_admin in admin_site._registry.items():
    opts = model._meta
    print('%s:%s_%s_change' % (admin_site.name, opts.app_label, opts.model_name))

