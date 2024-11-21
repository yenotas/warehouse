from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from .models import Products, Orders, Projects, StorageCells, Suppliers, Categories, ModelAccessControl, CustomUser, \
    PivotTable, ProductMovies, Departments
from dal import autocomplete


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


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ''
        qs = Departments.objects.all()
        if self.q:
            qs = qs.filter(first_name__icontains=self.q) | qs.filter(last_name__icontains=self.q)
        return qs


# @login_required
# def pivot_table_view(request):
#     if request.method == 'POST':
#         formset = PivotTableFormSet(request.POST)
#         if formset.is_valid():
#             formset.save()
#             return redirect('pivot_table')
#     else:
#         formset = PivotTableFormSet(queryset=PivotTable.objects.all())
#     return render(request, 'pivot_table.html', {'formset': formset})


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


# Попытки улучшить
# @csrf_exempt
# @login_required
# def autocomplete(request):
#     if 'term' in request.GET or 'item_id' in request.GET:
#         model_name = request.GET.get('model_name')
#         field_name = request.GET.get('field_name')
#         search_term = request.GET.get('term', None)
#         item_id = request.GET.get('item_id', None)
#
#         # Получаем список поисковых полей из запроса
#         allowed_fields = request.GET.getlist('allowed_fields[]', [])
#
#         try:
#             model_class = ContentType.objects.get(model=model_name).model_class()
#             if item_id:
#                 try:
#                     item = model_class.objects.get(id=item_id)
#                     return JsonResponse({'text': getattr(item, field_name), 'id': item.id})
#                 except model_class.DoesNotExist:
#                     return JsonResponse({'error': 'Item not found'}, status=404)
#
#             if search_term and field_name in allowed_fields:
#                 filter_kwargs = {f"{field_name}__icontains": search_term}
#                 qs = model_class.objects.filter(**filter_kwargs)
#                 results = [{"id": item.id, "text": getattr(item, field_name)} for item in qs]
#                 return JsonResponse(results, safe=False)
#
#         except ContentType.DoesNotExist:
#             return JsonResponse({'error': 'Invalid model'}, status=400)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#
#     return JsonResponse([], safe=False)


@login_required
def autocomplete(request):
    if 'term' in request.GET or 'item_id' in request.GET:
        model_name = request.GET.get('model_name')
        field_name = request.GET.get('field_name')
        search_term = request.GET.get('term', None)
        item_id = request.GET.get('item_id', None)

        try:
            model_class = ContentType.objects.get(model=model_name).model_class()
            if item_id:
                try:
                    item = model_class.objects.filter(id=item_id).first()
                    print('загрузка формы:',  model_name, field_name, item_id)
                except Exception as e:
                    print('item_id = строка:', e)
                    item = model_class.objects.filter(**{field_name: item_id}).first()
                    return JsonResponse({"id": item.id, "text": getattr(item, field_name)})
                if item:
                    return JsonResponse({'text': getattr(item, field_name)})
                return JsonResponse({'error': 'Item not found'}, status=404)

            if search_term:
                filter_kwargs = {f"{field_name}__icontains": search_term}
                qs = model_class.objects.filter(**filter_kwargs)
                results = [{"id": item.id, "text": getattr(item, field_name)} for item in qs]
                print('ввод:', model_name, field_name, results)
                return JsonResponse(results, safe=False)

        except Exception as e:
            print("Exception", str(e))

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



