from .outer_modules import redirect
from .__AutoCompleteAdmins import AutoCompleteAdmins


class TableAdminForm(AutoCompleteAdmins):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_list_template = "admin/table_view_inputs.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Проверяем наличие формы
        if not hasattr(self, 'form') or self.form is None:
            raise ValueError("Форма не определена для табличного вида.")

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
        extra_context['search_fields_list'] = self.get_search_fields()

        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request, obj=None):
            return False

    # class Media:
    #     js = ('admin/js/admin/AutoFields.js',)
