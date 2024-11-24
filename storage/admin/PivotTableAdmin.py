from .outer_modules import Q
from .__AutoCompleteAdmins import AutoCompleteAdmins
from ..forms import PivotTableForm


class PivotTableAdmin(AutoCompleteAdmins):
    form = PivotTableForm
    fields = ('product_name', 'product_link', 'request_about', 'packaging_unit', 'request_quantity',
        'project_code', 'detail_name', 'detail_code', 'request_date',
        'responsible', 'delivery_location', 'deadline_delivery_date', 'waiting_date', 'has_on_storage',
        'supplier', 'invoice_number', 'delivery_status', 'not_delivered_pcs',
        'document_flow', 'documents', 'accounted_in_1c', 'supply_date', 'supply_quantity', 'storage_cell',)
    list_display = (
        'product_name', 'product_link', 'request_about', 'packaging_unit', 'request_quantity',
        'project_code', 'detail_name', 'detail_code', 'product_image_tag', 'request_date',
        'responsible', 'delivery_location', 'deadline_delivery_date', 'waiting_date', 'has_on_storage',
        'order_complete', 'supplier', 'invoice_number', 'delivery_status', 'not_delivered_pcs',
        'document_flow', 'documents', 'accounted_in_1c', 'supply_date', 'supply_quantity', 'storage_cell',
    )
    list_editable = (
        'request_about', 'invoice_number', 'waiting_date', 'delivery_status', 'document_flow',
        'documents', 'accounted_in_1c'
    )
    autocomplete_fields = ['product_name']
    search_fields = ['product_name__name']
    list_filter = ('order__delivery_status', 'product_request__project__project_code')
    ordering = ('id',)

    def order_complete(self, obj):
        return obj.order_complete
    order_complete.short_description = 'Заказ оформлен'
    order_complete.boolean = True

    # Фильтрация по дате заявки
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            qs = qs.filter(
                Q(product_request__request_date__gte=start_date) &
                Q(product_request__request_date__lte=end_date)
            )
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.order:
            # Блокируем поля, если уже существует заказ
            readonly_fields += ['product_name', 'request_quantity', 'project_code', 'delivery_location',
                                'deadline_delivery_date']
        return readonly_fields

    class Media:
        js = ('admin/js/admin/AddPivotPosition.js',)  # Подключаем дополнительные скрипты для автозаполнения