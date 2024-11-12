from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

# from .forms import PivotTableFormSet
from .models import Products, Orders, Projects, StorageCells, Suppliers, Categories, ModelAccessControl, CustomUser, \
    PivotTable, ProductMovies
from dal import autocomplete
from .models import Departments


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


class CategoriesAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Categories.objects.none()

        qs = Categories.objects.all().order_by('name')

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        if not qs.exists() and self.request.GET.get('create') == '1':
            new_category = Categories.objects.create(name=self.q)
            return Categories.objects.filter(id=new_category.id)

        return qs

    def get_result_label(self, item):
        return item.name

    def get_selected_result_label(self, item):
        return item.name


class ProductsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Products.objects.none()
        qs = Products.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class DepartmentsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Departments.objects.none()

        qs = Departments.objects.all().order_by('department')

        if self.q:
            qs = qs.filter(department__icontains=self.q)

        # Если совпадений нет и запрос включает создание отдела
        print('Autocomplete', self.q)
        create_if_missing = self.request.GET.get('create')
        print('create_if_missing', create_if_missing)
        if not qs.exists() and create_if_missing == '1':
            department_name = self.q
            new_department = Departments.objects.create(department=department_name)
            return Departments.objects.filter(id=new_department.id)  # Возвращаем только что созданный отдел

        return qs


    def get_result(self, obj):
        return {
            "id": obj.id,
            "text": obj.department,  # Название, отображаемое в select2
        }

    def get_result_label(self, item):
        return item.department

    def get_selected_result_label(self, item):
        return item.department


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


@csrf_exempt
def get_reason_choices_s(request):

    process_type = request.GET.get('process_type', None)
    print('process_type', process_type)
    choices = []

    if process_type == 'warehouse':
        choices = [{"id": str(order.id), "name": str(order.product_request)} for order in Orders.objects.all()]
    elif process_type == 'distribute':
        choices = [{"id": str(emp.id), "name": str(emp.name)} for emp in CustomUser.objects.all()]
    elif process_type == 'return':
        choices = [{"id": str(proj.id), "name": str(proj.name)} for proj in Projects.objects.all()]
    elif process_type == 'sup_return':
        choices = [{"id": str(supp.id), "name": str(supp.name)} for supp in Suppliers.objects.all()]
    elif process_type == 'move':
        choices = [{"id": str(cell.id), "name": str(cell.cell_address)} for cell in StorageCells.objects.all()]
    else:
        choices = []

    print('choices', choices)

    return JsonResponse({'choices': choices})
