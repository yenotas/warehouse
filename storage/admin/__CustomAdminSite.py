from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    site_header = "АРХИТЕКЦИЯ"
    site_title = "Управление складом и закупками"
    index_title = "Управление складом и закупками"

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label=app_label)

        # Группируем модели
        custom_structure = {
            "Оперативный учет": ['PivotTable'],
            "Закупки": ['ProductRequest', 'Orders'],
            "Склад": ['ProductMovies', 'StorageCells'],
            "Товары": ["Products", "Suppliers"],  # "Categories",
            "Организация": ['Projects', 'Departments', 'CustomUser', 'Group', 'ModelAccessControl'],
        }
        # Если `app_label` задан, возвращаем список моделей только для текущего приложения
        if app_label:
            for app in app_list:
                if app['app_label'] == app_label:
                    return [app]

        grouped_app_list = []
        for header, models in custom_structure.items():
            grouped_models = []
            for app in app_list:
                for model in app['models']:
                    if model['object_name'] in models:
                        grouped_models.append(model)

            # Сортируем модели в строгом соответствии с порядком в custom_structure
            grouped_models = sorted(
                grouped_models,
                key=lambda m: models.index(m['object_name'])
            )

            if grouped_models:
                grouped_app_list.append({'name': header, 'models': grouped_models})

        return grouped_app_list

    def each_context(self, request):
        context = super().each_context(request)
        if request.user.is_authenticated:
            context['user_groups'] = request.user.groups.values_list('name', flat=True)
            context['user_first_name'] = request.user.first_name
            context['user_last_name'] = request.user.last_name
        return context


admin_site = CustomAdminSite(name='myadmin')

