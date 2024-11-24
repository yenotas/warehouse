from .outer_modules import admin, redirect
from ..mixins import AccessControlMixin


class AutoCompleteAdmins(AccessControlMixin, admin.ModelAdmin):

    change_list_template = "admin/change_list.html"  # стандартный шаблон по умолчанию

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, 'one_line_add', False):
            self.change_list_template = "admin/one_line_add.html"
        if getattr(self, 'table_view', False):
            self.change_list_template = "admin/table_view_inputs.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Проверяем наличие формы
        if not hasattr(self, 'form') or self.form is None:
            raise ValueError("Форма не определена для автозаполнения.")

        form = self.form(request.POST or None)

        # Если метод POST, проверяем форму
        if request.method == 'POST':
            if form.is_valid():
                try:
                    form.save()
                    self.message_user(request, "Добавлено успешно")
                    return redirect(request.path)
                except Exception as e:
                    self.message_user(request, f"Ошибка при сохранении: {str(e)}", level="error")

        # Передаём форму в контекст
        extra_context['form'] = form
        if getattr(self, 'need_search', False):
            extra_context['search_fields_list'] = self.get_search_fields()

        return super().changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and not request.user.groups.filter(name__in=['Администраторы']).exists():
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def has_add_permission(self, request, obj=None):
        if ((getattr(self, 'table_view', False) or getattr(self, 'one_line_add', False)) and
                request.path.endswith(f'/{self.model._meta.model_name}/')):
            return False
        return super().has_add_permission(request)

    class Media:
        js = ('admin/js/admin/AutoFields.js',)
