from .outer_modules import admin, redirect
from ..mixins import AccessControlMixin


class ManageAdmins(AccessControlMixin, admin.ModelAdmin):
    change_list_template = "admin/change_list.html"
    ordering = ['-id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, 'one_line_add', False):
            self.change_list_template = "admin/one_line_add.html"
        if getattr(self, 'tabled_add', False):
            self.add_form_template = "admin/table_add.html"
            self.change_list_template = "admin/table_view.html"
            # self.Media.js += ('admin/js/admin/TableView.js',)

    def changelist_view(self, request, extra_context=None):

        extra_context = extra_context or {}
        if not hasattr(self, 'form') or self.form is None:
            raise ValueError("Форма не определена для автозаполнения.")

        form = self.form(request.POST or None, request=request)

        if request.method == 'POST':
            if form.is_valid():
                try:
                    form.save()
                    self.message_user(request, "Добавлено успешно")
                    return redirect(request.path)
                except Exception as e:
                    self.message_user(request, f"Ошибка при сохранении: {str(e)}", level="error")

        extra_context['form'] = form
        extra_context['title'] = ""
        if form.related_models:
            extra_context['related_models'] = form.related_models

        print('extra_context', extra_context)

        return super().changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        actions = super().get_actions(request)

        if not request.user.is_superuser and not request.user.groups.filter(name__in=['Администраторы']).exists():
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def has_add_permission(self, request, obj=None):
        if getattr(self, 'one_line_add', False) and request.path.endswith(f'/{self.model._meta.model_name}/'):
            return False
        return super().has_add_permission(request)

    # class Media:
    #     js = ('admin/js/admin/SingleLineAdd.js', 'admin/js/admin/AutoFields.js',)

