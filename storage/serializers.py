from rest_framework import serializers
from .models import Products, ProductRequest, Orders, Projects, ProductMovies, StorageCells, Suppliers


class PivotTableSerializer(serializers.Serializer):
    product_name = serializers.CharField(source='name')
    product_link = serializers.URLField(source='product_link')
    order_about = serializers.CharField(source='productrequest_set__order_about')
    packaging_unit = serializers.CharField(source='packaging_unit')
    project_code = serializers.CharField(source='projects__project_code')
    detail_code = serializers.CharField(source='projects__detail_code')
    product_image = serializers.ImageField(source='product_image')
    request_date = serializers.DateField(source='productrequest_set__request_date')
    responsible_employee = serializers.CharField(source='productrequest_set__responsible_employee')
    delivery_location = serializers.CharField(source='productrequest_set__delivery_location')
    deadline_delivery_date = serializers.DateField(source='productrequest_set__deadline_delivery_date')
    waiting_date = serializers.DateField(source='orders__waiting_date')
    supplier_name = serializers.CharField(source='suppliers__name')
    invoice_number = serializers.CharField(source='orders__invoice_number')
    delivery_status = serializers.CharField(source='orders__delivery_status')
    documents = serializers.CharField(source='orders__documents')
    order_quantity = serializers.IntegerField(source='productrequest_set__order_quantity')
    record_date = serializers.DateField(source='productmovies_set__record_date')
    movie_quantity = serializers.IntegerField(source='productmovies_set__movie_quantity')
    employee = serializers.CharField(source='productmovies_set__employee')
    return_to_supplier_reason = serializers.CharField(source='productmovies_set__return_to_supplier_reason')
    cell_address = serializers.CharField(source='storagecells__cell_address')
