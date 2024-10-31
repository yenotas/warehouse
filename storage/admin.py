from django.urls import path
from django.contrib import admin
from .forms import *
from .models import *
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin


class MyAdminSite(admin.AdminSite):
    site_header = "ЗАКУПКИ | СКЛАД"
    site_title = "Панель управления товарной номенклатурой"
    index_title = "Управление складом и закупками."

    def get_app_list(self, request, app_label=None):  # добавлен app_label
        app_list = super().get_app_list(request, app_label=app_label)

        # Список названий моделей, который определяет порядок сортировки
        model_order = ['PivotTable', 'Products', 'ProductRequest', 'Orders', 'ProductMovies', 'Projects', 'StorageCells', 'Departments', 'Suppliers']

        # Сортировка списка моделей в админке по названию модели
        for app in app_list:
            app['models'].sort(key=lambda x: model_order.index(x['object_name'])
                               if x['object_name'] in model_order else len(model_order))

        return app_list


# Создаем экземпляр
admin_site = MyAdminSite(name='myadmin')

admin_site.register(Departments)


class CustomUserAdmin(UserAdmin):
    form = CustomUserForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'tg', 'department', 'position_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'full_name', 'department_display', 'email')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Имя и Фамилия'

    # Метод для отображения отдела
    def department_display(self, obj):
        return obj.department.department if obj.department else "—"
    department_display.short_description = 'Отдел/Цех'

    def get_actions(self, request):
        return []

    class Media:
        js = ('admin/js/admin/AddDepartment.js',)


admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Group, GroupAdmin)


# class SuppliersInline(admin.TabularInline):
#     model = Suppliers
#     extra = 1
#     form = SuppliersForm
#     fields = ('name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg')
#
#     def get_actions(self, request):
#         return []


class SuppliersAdmin(admin.ModelAdmin):
    form = SuppliersForm
    list_display = ('name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg')
    fields = ('name', 'inn', 'ogrn', 'address', 'contact_person', 'website', 'email', 'phone', 'tg')
    search_fields = ['name', 'inn', 'ogrn', 'address', 'contact_person', 'website']
    ordering = ('name',)
    list_filter = ('name',)

    def get_actions(self, request):
        return []


class ProductAdmin(admin.ModelAdmin):
    form = ProductForm

    list_display = ('name', 'product_sku', 'product_link', 'product_image', 'category', 'supplier')
    fields = ('name', 'product_sku', 'product_link', 'product_image', 'category', 'supplier', 'packaging_unit',
              'quantity_in_package', 'near_products')
    search_fields = ['category__name', 'name', 'supplier__name', 'product_sku']
    ordering = ('category__name', 'name', 'supplier__name')
    list_filter = ('category__name', 'name', 'supplier__name')

    class Media:
        js = ('admin/js/admin/AddCategory.js',)

    def get_actions(self, request):
        return []


class ProjectsAdmin(admin.ModelAdmin):
    form = ProjectsForm
    list_display = (
    'id', 'creation_date', 'name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code')
    fields = (
    'name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code')
    search_fields = ['name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code']
    ordering = ('name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code')
    list_filter = ('name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = CustomUser.objects.filter(username=request.user.username).first()
        role = None
        if user and user.groups.exists():
            role = user.groups.first().name
        if role == 'Склад':
            fields_to_disable = ['creation_date', 'name', 'detail_full_name', 'manager', 'engineer', 'project_code', 'detail_name', 'detail_code']
            for field in fields_to_disable:
                form.base_fields[field].disabled = True
                form.base_fields[field].widget.attrs['style'] = 'background-color: #f0f0f0;'
        return form

    def get_actions(self, request):
        return []


class ProductRequestAdmin(admin.ModelAdmin):
    form = ProductRequestForm
    list_display = (
    'id', 'request_date', 'product', 'request_about', 'request_quantity', 'project', 'responsible_employee', 'delivery_location',
    'delivery_address', 'deadline_delivery_date')
    fields = (
    'product', 'request_about', 'request_quantity', 'project', 'responsible_employee', 'delivery_location',
    'delivery_address', 'deadline_delivery_date')
    search_fields = ['product', 'project']
    ordering = ('id', 'request_date', 'product', 'project')
    list_filter = ('request_date', 'product', 'project')

    def get_actions(self, request):
        return []

    class Media:
        js = ('admin/js/admin/ChangeProductRequest.js',)


class OrdersAdmin(admin.ModelAdmin):
    form = OrdersForm
    list_display = ('id', 'order_date', 'product_request', 'manager', 'accounted_in_1c', 'invoice_number', 'delivery_status',
                    'documents', 'waiting_date')
    fields = ('product_request', 'manager', 'accounted_in_1c', 'invoice_number', 'delivery_status', 'documents',
                     'waiting_date')
    search_fields = ['delivery_status', 'product_request', 'manager', 'invoice_number']
    ordering = ('id', 'delivery_status', 'order_date', 'product_request', 'waiting_date')
    list_filter = ('order_date', 'manager', 'product_request', 'delivery_status')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = CustomUser.objects.filter(username=request.user.username).first()
        role = None
        if user and user.groups.exists():
            role = user.groups.first().name
        if role not in ['Администратор', 'Менеджер', 'Закупка']:
            fields_to_disable = ['product_request', 'manager', 'accounted_in_1c', 'invoice_number', 'delivery_status',
                    'documents', 'waiting_date']
            for field in fields_to_disable:
                if field != 'creation_date1':
                    form.base_fields[field].disabled = True
                    form.base_fields[field].widget.attrs['style'] = 'background-color: #f0f0f0;'
        return form

    def get_actions(self, request):
        return []


class StorageCellsAdmin(admin.ModelAdmin):
    form = StorageCellsForm
    list_display = ('cell_address', 'info')
    fields = ('cell_address', 'info')
    search_fields = ['cell_address', 'info']
    ordering = ('cell_address',)
    list_filter = ('cell_address',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = CustomUser.objects.filter(username=request.user.username).first()
        role = None
        if user and user.groups.exists():
            role = user.groups.first().name
        if role not in ['Администратор', 'Склад']:
            print('NOT ADMIN!!!!')
            fields_to_disable = ['cell_address', 'info']
            for field in fields_to_disable:
                form.base_fields[field].disabled = True
                form.base_fields[field].widget.attrs['style'] = 'background-color: #f0f0f0;'
        else:
            print('IS ADMIN!!!!')
        return form

    def get_actions(self, request):
        return []


class ProductMoviesAdmin(admin.ModelAdmin):
    form = ProductMoviesForm
    list_display = ('record_date', 'product', 'process_type', 'return_to_supplier_reason', 'movie_quantity', 'new_cell',
                    'reason')
    fields = ('product', 'process_type', 'return_to_supplier_reason', 'movie_quantity', 'new_cell',
              'reason')
    search_fields = ['product', 'process_type', 'new_cell']
    list_filter = ('product', 'process_type', 'new_cell')
    ordering = ('product', 'process_type', 'new_cell')

    def get_actions(self, request):
        return []
    class Media:
        js = ('admin/js/admin/ChangeProductMovieType.js',)


class PivotTableAdmin(admin.ModelAdmin):
    change_list_template = "admin/storage/complex_table.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('complex-table/', self.admin_site.admin_view(self.changelist_view), name='complex_table'),
        ]
        return custom_urls + urls

    def get_actions(self, request):
        return []
    search_fields = ['product', 'project', 'responsible_employee', 'invoice_number', 'storage_cell', 'detail_name', 'detail_code']


admin_site.register(StorageCells, StorageCellsAdmin)
admin_site.register(Suppliers, SuppliersAdmin)
admin_site.register(PivotTable, PivotTableAdmin)
admin_site.register(Products, ProductAdmin)
admin_site.register(Projects, ProjectsAdmin)
admin_site.register(ProductRequest, ProductRequestAdmin)
admin_site.register(Orders, OrdersAdmin)
admin_site.register(ProductMovies, ProductMoviesAdmin)



