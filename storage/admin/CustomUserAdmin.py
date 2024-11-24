
from .outer_modules import (UserAdmin, Concat, Value, CharField, messages, _, PermissionDenied, AdminPasswordChangeForm, redirect,
                            TemplateResponse)
from .__AutoCompleteAdmins import AutoCompleteAdmins
from ..forms import CustomUserChangeForm, CustomUserCreationForm


class CustomUserAdmin(UserAdmin, AutoCompleteAdmins):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('full_name_display', 'username_display', 'department_display', 'email', 'groups_display')

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

    def get_queryset(self, request):
        # Добавляем аннотации для виртуальных полей
        qs = super().get_queryset(request)
        return qs.annotate(
            full_name=Concat(
                'first_name', Value(' '), 'last_name',
                output_field=CharField()  # Указываем тип аннотированного поля
            )
        ).order_by('full_name', 'department__name')

    def username_display(self, obj):
        return obj.username
    username_display.short_description = "Логин"
    username_display.admin_order_field = 'username'

    def full_name_display(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name_display.short_description = 'Имя и Фамилия'
    full_name_display.admin_order_field = 'full_name'

    def department_display(self, obj):
        return obj.department.name if obj.department else "—"
    department_display.short_description = 'Отдел/Цех'
    department_display.admin_order_field = 'department__name'

    def groups_display(self, obj):
        return ", ".join([group.name for group in obj.groups.all()]) if obj.groups.exists() else "—"
    groups_display.short_description = 'Группы доступа'

    def get_fieldsets(self, request, obj=None):
        if not request.user.is_superuser and not request.user.groups.filter(name__in=['Администраторы', 'Кадры']).exists():
            # Добавляем поле 'password' для отображения ссылки «Сменить пароль»
            return (
                (None, {'fields': ('username', 'password')}),
                ('Личная информация', {'fields': ('first_name', 'last_name', 'email', 'tel', 'tg', 'department', 'position_name')}),
            )
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы', 'Кадры']).exists():
            return self.readonly_fields
        else:
            readonly_fields = [f.name for f in self.model._meta.fields if f.name not in ('first_name', 'last_name', 'email', 'tel', 'tg', 'department', 'position_name', 'password')]
            readonly_fields += ['is_superuser']
            print('readonly_fields', readonly_fields)
            return readonly_fields

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы', 'Кадры']).exists():
            return True
        if obj is None or obj == request.user:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы', 'Кадры']).exists():
            return True
        if obj == request.user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы', 'Кадры']).exists()

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Администраторы', 'Кадры']).exists()

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and not request.user.groups.filter(name__in=['Администраторы']).exists():
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def user_change_password(self, request, id, form_url=''):
        user = self.get_object(request, id)
        if not self.has_change_permission(request, user):
            raise PermissionDenied

        if request.method == 'POST':
            form = AdminPasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _('Пароль успешно изменен.'))
                return redirect('myadmin:storage_customuser_change', user.pk)
        else:
            form = AdminPasswordChangeForm(user)

        context = {
            'title': _('Изменить пароль пользователя'),
            'form': form,
            'is_popup': '_popup' in request.POST or '_popup' in request.GET,
            'opts': self.model._meta,
            'original': user,
            'media': self.media + form.media,
        }
        return TemplateResponse(request, 'admin/auth/user/change_password.html', context)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request  # Передаём объект запроса в форму
        return form
