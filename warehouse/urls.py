from django.conf.urls.static import static
from storage.admin import admin_site
# from storage.views import get_product_data, get_reason_choices, test_view  # , delete_near_product

from django.urls import path, include

from storage.views import get_reason_choices, get_product_data, DepartmentsAutocomplete, \
    CategoriesAutocomplete, get_model_fields, get_saved_fields, ProductsAutocomplete, \
    UserAutocomplete   # , pivot_table_view
from warehouse import settings

urlpatterns = [
    path('admin/', admin_site.urls),
    path('get-model-fields/', get_model_fields, name='get_model_fields'),
    # path('get-reason_id-choices/', get_reason_choices, name='get_reason_choices'),
    path('get-product-data/<int:product_id>/', get_product_data, name='get_product_data'),
    path('departments-autocomplete/', DepartmentsAutocomplete.as_view(), name='departments-autocomplete'),
    path('categories-autocomplete/', CategoriesAutocomplete.as_view(), name='categories-autocomplete'),
    path('get-saved-fields/', get_saved_fields, name='get-saved-fields'),
    path('products-autocomplete/', ProductsAutocomplete.as_view(), name='products-autocomplete'),
    path('users-autocomplete/', UserAutocomplete.as_view(), name='users-autocomplete'),
    path('get_reason_choices/', get_reason_choices, name='get_reason_choices'),
    # path('pivot_table/', pivot_table_view, name='pivot_table'),
]


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('admin/storage/', complex_table_view, name='pivottable'),
#     path('pivottable-test/', complex_table_view, name='pivottable_test')
# path('storage/', include('storage.urls')),
# path('delete-near-product/<int:product_id>/', delete_near_product, name='delete_near_product'),
# ]

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls))
#     ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = pageNotFound()
