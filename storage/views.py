from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound

from django.views.decorators.http import require_POST
from django.http import JsonResponse
import pandas as pd
from django.shortcuts import render

from .models import Products, ProductRequest, Orders, Projects, ProductMovies, StorageCells, Suppliers, Employees
from django.core.paginator import Paginator
from rest_framework import viewsets
from .serializers import PivotTableSerializer


# @login_required
class PivotTableViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()  # Основная модель, можно изменить
    serializer_class = PivotTableSerializer

    def get_queryset(self):
        # Логика объединения данных из различных моделей
        products = Products.objects.all()
        product_requests = ProductRequest.objects.all()
        orders = Orders.objects.all()
        projects = Projects.objects.all()
        product_movies = ProductMovies.objects.all()
        storage_cells = StorageCells.objects.all()
        suppliers = Suppliers.objects.all()

        data = {
            'Product_Name': [product.name for product in products],
            'Product_Link': [product.product_link for product in products],
            'Order_About': [pr.order_about for pr in product_requests],
            'Packaging_Unit': [product.packaging_unit for product in products],
            'Project_Code': [project.project_code for project in projects],
            'Detail_Code': [project.detail_code for project in projects],
            'Product_Image': [product.product_image for product in products],
            'Request_Date': [pr.request_date for pr in product_requests],
            'Responsible_Employee': [pr.responsible_employee for pr in product_requests],
            'Delivery_Location': [pr.delivery_location for pr in product_requests],
            'Deadline_Delivery Date': [pr.deadline_delivery_date for pr in product_requests],
            'Waiting_Date': [order.waiting_date for order in orders],
            'Supplier_Name': [supplier.name for supplier in suppliers],
            'Invoice_Number': [order.invoice_number for order in orders],
            'Delivery_Status': [order.delivery_status for order in orders],
            'Documents': [order.documents for order in orders],
            'Order_Quantity': [pr.order_quantity for pr in product_requests],
            'Record_Date': [pm.record_date for pm in product_movies],
            'Movie_Quantity': [pm.movie_quantity for pm in product_movies],
            'Employee': [pm.employee for pm in product_movies],
            'Return_To_Supplier_Reason': [pm.return_to_supplier_reason for pm in product_movies],
            'Cell_Address': [sc.cell_address for sc in storage_cells],
        }

        max_len = len(data['Product_Name'])
        print('max_len', max_len)

        for key, lst in data.items():
            if len(lst) < max_len:
                lst.extend([None] * (max_len - len(lst)))

        print('!!!!!!!!!!!!!!!!!!!!!!!\n\n', data['Product_Name'])

        return data


def pageNotFound(request, exception):
    return HttpResponseNotFound(f'<h1>Страница отсутствует :(</h1>\n<p>{exception}</p>')


@require_POST
def delete_near_product(request):
    product_id = request.POST.get('product_id')
    near_product_id = request.POST.get('near_product_id')
    try:
        product = Products.objects.get(id=product_id)
        near_product = Products.objects.get(id=near_product_id)

        # Удаляем связь ManyToMany
        product.near_products.remove(near_product)

        return JsonResponse({'success': True, 'message': 'Связь успешно удалена.'})
    except Products.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Продукт не найден.'})


@login_required
def complex_table_view(request):

    products = Products.objects.all()
    product_requests = ProductRequest.objects.all()
    orders = Orders.objects.all()
    projects = Projects.objects.all()
    product_movies = ProductMovies.objects.all()
    storage_cells = StorageCells.objects.all()
    suppliers = Suppliers.objects.all()

    print('products', products)

    # Создание DataFrame
    data = {
        'Product_Name': [product.name for product in products],
        'Product_Link': [product.product_link for product in products],
        'Order_About': [pr.order_about for pr in product_requests],
        'Packaging_Unit': [product.packaging_unit for product in products],
        'Project_Code': [project.project_code for project in projects],
        'Project_Code': [project.project_code for project in projects],
        'Detail_Code': [project.detail_code for project in projects],
        'Product_Image': [product.product_image for product in products],
        'Request_Date': [pr.request_date for pr in product_requests],
        'Responsible_Employee': [pr.responsible_employee for pr in product_requests],
        'Delivery_Location': [pr.delivery_location for pr in product_requests],
        'Deadline_Delivery Date': [pr.deadline_delivery_date for pr in product_requests],
        'Waiting_Date': [order.waiting_date for order in orders],
        'Supplier_Name': [supplier.name for supplier in suppliers],
        'Invoice_Number': [order.invoice_number for order in orders],
        'Delivery_Status': [order.delivery_status for order in orders],
        'Documents': [order.documents for order in orders],
        'Order_Quantity': [pr.order_quantity for pr in product_requests],
        'Record_Date': [pm.record_date for pm in product_movies],
        'Movie_Quantity': [pm.movie_quantity for pm in product_movies],
        'Employee': [pm.employee for pm in product_movies],
        'Return_To_Supplier_Reason': [pm.return_to_supplier_reason for pm in product_movies],
        'Cell_Address': [sc.cell_address for sc in storage_cells],
    }

    max_len = len(data['Product_Name'])
    print('max_len', max_len)

    # Дополнить списки до максимальной длины
    for key, lst in data.items():
        if len(lst) < max_len:
            lst.extend([None] * (max_len - len(lst)))

    df = pd.DataFrame(data)

    # Пагинация
    paginator = Paginator(df.to_dict('records'), 100)  # по 100 строк на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    print("DataFrame:", df)
    print("page_obj содержит:", page_obj)  # Проверка наличия данных

    context = {
        'page_obj': page_obj
    }
    return render(request, 'complex_table.html', context)
