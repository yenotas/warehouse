from .__TableAdminForm import TableAdminForm
from storage.forms import ProductsForm


class ProductsAdmin(TableAdminForm):
    form = ProductsForm

    list_display = ('name', 'product_sku', 'supplier', 'product_link', 'product_image_tag', 'display_categories')
    fields = ('name', 'product_sku', 'supplier', 'product_link', 'product_image', 'categories', 'packaging_unit',
              'quantity_in_package',)
    search_fields = ['categories', 'name', 'supplier', 'product_sku']
    ordering = ('name', 'supplier')
    list_filter = ('categories', 'supplier')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.distinct()

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    display_categories.short_description = "Категории / признаки"
