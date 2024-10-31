# from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound

# from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# import pandas as pd
# from django.shortcuts import render

from .models import Products, ProductRequest, Orders, Projects, ProductMovies, StorageCells, Suppliers, Categories
from dal import autocomplete
from .models import Departments


@csrf_exempt
def add_department(request):
    if request.method == 'POST':
        department_name = request.POST.get('department', None)
        if department_name:
            department, created = Departments.objects.get_or_create(department=department_name)
            return JsonResponse({'id': department.id, 'name': department.department})
    return JsonResponse({'error': 'Invalid request'}, status=400)


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


# если 'Прием на склад', то в reason должны открываться заказы на закупку и подставляться Orders.id
# 'Выдача со склада' - ищем среди сотрудников и подставляем Employees.name
# 'Возврат на склад' - должны открываться проекты и подставляться Projects.name
# 'Возврат поставщику' - ищем среди поставщиков и подставляем Suppliers.name
# 'Перемещение из ячейки' подставляем текущее значение new_cell, а если его нет - делаем опцию неактивной
# В случаях 'Перемещение из ячейки', 'Прием на склад' и 'Выдача со склада' поле reason не может быть пустым


@csrf_exempt
def get_reason_choices(request):

    process_type = request.GET.get('process_type', None)
    print('process_type', process_type)
    choices = []

    if process_type == 'warehouse':
        choices = [{"id": str(order.id), "name": str(order.product_request)} for order in Orders.objects.all()]
    elif process_type == 'distribute':
        choices = [{"id": str(emp.id), "name": str(emp.name)} for emp in Employees.objects.all()]
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
