
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from .models import Products, Orders, Projects, StorageCells, Suppliers, Categories, ModelAccessControl, CustomUser, \
    PivotTable, ProductMovies
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
            return CustomUser.objects.none()
        qs = CustomUser.objects.all()
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


class NamesAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        if not self.request.user.is_authenticated:
            return None

        model_name = self.kwargs.get('model_name')
        try:
            model_class = ContentType.objects.get(model=model_name).model_class()
            print('\n\n')
            print('model_name', model_name)
            print('\n\n')

        except Exception:
            raise Http404("Model not found")

        qs = model_class.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        if not qs.exists() and self.request.GET.get('create') == '1':
            new_item = Categories.objects.create(name=self.q)
            return Categories.objects.filter(id=new_item.name)

        return qs

    def get_result_label(self, item):
        return item.name

    def get_selected_result_label(self, item):
        return item.name

    def get_result(self, obj):
        return {
            "id": obj.id,
            "text": obj.name,
        }


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



