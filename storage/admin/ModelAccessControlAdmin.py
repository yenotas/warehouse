from django.utils.safestring import mark_safe
import json
from .outer_modules import admin, ContentType, DefaultGroupAdmin
from ..forms import ModelAccessControlForm


class RestrictedGroupAdmin(DefaultGroupAdmin):
    """
    Ограничение доступа к редактированию групп
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
    """
    Ограничение доступа к редактированию разрешений
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


# Админская модель для ModelAccessControl
class ModelAccessControlAdmin(admin.ModelAdmin):
    form = ModelAccessControlForm
    add_form_template = 'admin/add_form.html'
    change_form_template = 'admin/add_form.html'
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