from storage.models import ModelAccessControl, CustomUser


class AccessControlMixin:
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = CustomUser.objects.filter(username=request.user.username).first()
        user_groups = set(user.groups.values_list('name', flat=True))
        model_name = self.model._meta.model_name

        access_controls = ModelAccessControl.objects.filter(model_name__model=model_name)

        # Делаем поле 'ID' неактивным для всех пользователей
        if 'id' in form.base_fields:
            form.base_fields['id'].disabled = True
            form.base_fields['id'].widget.attrs['style'] = 'background-color: #f0f0f0;'

        for access_control in access_controls:
            access_groups = set(access_control.groups.values_list('name', flat=True))
            if user_groups.isdisjoint(access_groups):
                for field in access_control.fields_to_disable:
                    if field in form.base_fields:
                        form.base_fields[field].disabled = True
                        form.base_fields[field].widget.attrs['style'] = 'background-color: #f0f0f0;'
        return form