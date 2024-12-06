import logging

from django.contrib import messages
# from dal import autocomplete
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt

from .models import Products, Orders, Projects, StorageCells, Suppliers, Categories, ModelAccessControl, CustomUser, \
    PivotTable, ProductMovies, Departments

from django.views import View
from django.http import JsonResponse
from django.apps import apps


class AutocompleteView(View):
    def get(self, request):
        term = request.GET.get('term', '')
        model_name = request.GET.get('model', '')
        field_name = request.GET.get('field', '')
        app_label = 'storage'
        print(model_name, field_name, term)

        if not term or not model_name or not field_name:
            return JsonResponse([], safe=False)

        # Получаем модель
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            return JsonResponse([], safe=False)

        filter_kwargs = {f'{field_name}__icontains': term}
        qs = model.objects.filter(**filter_kwargs)[:10]

        results = []
        for obj in qs:
            label = getattr(obj, field_name)
            results.append({
                'id': obj.id,
                'label': label,
                'value': label
            })

        return JsonResponse(results, safe=False)

# def add_multiple_categories_view(request):
#     if request.method == 'POST':
#         form = MultipleCategoriesForm(request.POST)
#         if form.is_valid():
#             categories_text = form.cleaned_data['categories']
#             categories_list = [cat.strip() for cat in categories_text.replace('\n', ',').split(',') if cat.strip()]
#
#             created = 0
#             for category in categories_list:
#                 if not Categories.objects.filter(name__iexact=category).exists():
#                     Categories.objects.create(name=category)
#                     created += 1
#             messages.success(request, f"Добавлено {created} новых категорий.")
#             return redirect('/admin/storage/categories/')  # Переход в админку
#     else:
#         form = MultipleCategoriesForm()
#
#     return render(request, 'admin/add_bulk_categories.html', {'form': form})


def get_reason_choices(request):
    process_type = request.GET.get('process_type')
    choices = []

    if process_type == 'warehouse':
        objects = Orders.objects.all()
    elif process_type == 'distribute':
        objects = CustomUser.objects.all()
    elif process_type == 'return':
        objects = Projects.objects.all()
    elif process_type == 'sup_return':
        objects = Suppliers.objects.all()
    elif process_type == 'move':
        objects = ProductMovies.objects.all()
    else:
        objects = []

    for obj in objects:
        choices.append({'id': obj.id, 'text': str(obj)})

    return JsonResponse({'choices': choices})


@csrf_exempt
def pivot_table_update(request):
    if request.method == 'POST':
        item_id = request.POST.get('id')
        field = request.POST.get('field')
        value = request.POST.get('value')

        try:
            item = PivotTable.objects.get(id=item_id)
            setattr(item, field, value)
            item.save()
            return JsonResponse({'status': 'success'})
        except PivotTable.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Запись не найдена'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})


def get_saved_fields(request):
    rule_id = request.GET.get('rule_id')
    if rule_id:
        try:
            rule = ModelAccessControl.objects.get(id=rule_id)
            saved_fields = rule.fields_to_disable
            return JsonResponse({'fields_to_disable': saved_fields})
        except ModelAccessControl.DoesNotExist:
            return JsonResponse({'fields_to_disable': []})
    return JsonResponse({'fields_to_disable': []})


def get_model_fields(request):
    model_id = request.GET.get('model_id')
    if model_id:
        model_class = ContentType.objects.get(id=model_id).model_class()
        fields = [{'name': field.name, 'verbose_name': field.verbose_name} for field in model_class._meta.fields]
        return JsonResponse({'fields': fields})
    return JsonResponse({'fields': []})


@login_required
def autocomplete(request):
    if 'term' in request.GET or 'item_id' in request.GET:
        model_name = request.GET.get('model_name')
        field_name = request.GET.get('field_name')
        search_term = request.GET.get('term', None)
        item_id = request.GET.get('item_id', None)

        model_class = ContentType.objects.get(model=model_name).model_class()
        if item_id:
            try:
                item = model_class.objects.filter(id=item_id).first()
                result = {"id": item.id, "text": getattr(item, field_name)}
                print('autocomplete / загрузка формы:', model_name, field_name, item_id)
            except Exception as e:
                item = model_class.objects.filter(**{field_name: item_id}).first()
                result = {'text': getattr(item, field_name)}
                print('autocomplete / item_id = строка:', e, result)

            return JsonResponse(result)

        if search_term:
            filter_kwargs = {f"{field_name}__icontains": search_term}
            qs = model_class.objects.filter(**filter_kwargs)
            result = [{"id": item.id, "text": getattr(item, field_name)} for item in qs]
            print('autocomplete / ввод:', model_name, field_name, result)
            return JsonResponse(result, safe=False)

    return JsonResponse([], safe=False)


logger = logging.getLogger(__name__)

@login_required
def autocompleteJ(request):
    if 'term' in request.GET or 'item_id' in request.GET:
        try:
            model_name = request.GET.get('model_name')
            field_name = request.GET.get('field_name')
            search_term = request.GET.get('term', None)
            item_id = request.GET.get('item_id', None)

            model_class = ContentType.objects.get(model=model_name).model_class()

            if item_id:
                try:
                    item = model_class.objects.filter(id=item_id).first()
                    result = {"id": item.id, "text": getattr(item, field_name)}
                    logger.debug(f'autocomplete / загрузка формы: {model_name}, {field_name}, {item_id}')
                except AttributeError as e:
                    logger.error(f'autocomplete / AttributeError: {e}')
                    return JsonResponse({'error': str(e)}, status=400)
                except Exception as e:
                    logger.error(f'autocomplete / item_id = строка: {e}')
                    return JsonResponse({'error': str(e)}, status=400)

                return JsonResponse(result)

            if search_term:
                filter_kwargs = {f"{field_name}__icontains": search_term}
                qs = model_class.objects.filter(**filter_kwargs)
                result = [{"id": item.id, "text": getattr(item, field_name)} for item in qs]
                logger.debug(f'autocomplete / ввод: {model_name}, {field_name}, {result}')
                return JsonResponse(result, safe=False)

        except ContentType.DoesNotExist as e:
            logger.error(f'autocomplete / ContentType.DoesNotExist: {e}')
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logger.error(f'autocomplete / ошибка: {e}')
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse([], safe=False)


@csrf_exempt
def get_product_data(request, product_id):
    product = Products.objects.get(id=product_id)
    supplier = Suppliers.objects.get(id=product.supplier_id)  # Или другой метод получения поставщика
    storage_cell = StorageCells.objects.get(id=product.storage_cell_id)  # Аналогично для ячейки хранения

    data = {
        'supplier': supplier.name,
        'cell_address': storage_cell.cell_address,
        'stock_quantity': product.stock_quantity,  # Здесь предполагается, что поле количества на складе есть в модели
    }
    return JsonResponse(data)



