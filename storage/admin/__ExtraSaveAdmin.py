from datetime import datetime
from .outer_modules import messages, reverse, HttpResponseRedirect
from django.db import models

class ExtraSaveAdmin():
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        class ModelFormWithRequest(form):
            def __init__(self, *args, **kwargs):
                self.request = request
                super().__init__(*args, **kwargs)

        return ModelFormWithRequest

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" in request.POST:
            # Сохраняем данные объекта в сессии
            initial_data = {}
            for field in obj._meta.fields:
                field_name = field.name
                if field_name not in ['id', 'name']:
                    value = getattr(obj, field_name)
                    if value is not None:
                        if isinstance(field, models.ForeignKey):
                            initial_data[field_name] = value.pk
                        elif isinstance(field, models.ImageField):
                            # Сохраняем путь к файлу изображения
                            initial_data[field_name] = value.name  # или value.url
                        else:
                            # Преобразуем значение в строку, если это необходимо
                            if isinstance(value, (datetime.date, datetime.datetime)):
                                initial_data[field_name] = value.isoformat()
                            else:
                                initial_data[field_name] = value

            # Обработка ManyToMany полей
            m2m_fields = {}
            for field in obj._meta.many_to_many:
                field_name = field.name
                value = getattr(obj, field_name).all()
                if value.exists():
                    m2m_fields[field_name] = [item.pk for item in value]

            # Сохраняем данные в сессии
            request.session['initial_data'] = {
                'fields': initial_data,
                'm2m': m2m_fields,
            }
            print('Data to be saved in session:', {'fields': initial_data, 'm2m': m2m_fields})

            self.message_user(request, "Запись сохранена!",
                              messages.SUCCESS) # "Следующая создана на ее основе - проверьте все поля!",
            add_url = reverse('admin:%s_%s_add' % (self.model._meta.app_label, self.model._meta.model_name))
            return HttpResponseRedirect(add_url)
        else:
            return super().response_add(request, obj, post_url_continue)