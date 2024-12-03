from storage.admin import admin_site
from django.urls import path

from storage.models import Suppliers
from storage.views import (
    get_reason_choices,
    get_product_data,
    get_model_fields,
    get_saved_fields,
    autocompleteJ, create_supplier,
    # add_multiple_categories_view
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('get-model-fields/', get_model_fields, name='get_model_fields'),
    path('get-product-data/<int:product_id>/', get_product_data, name='get_product_data'),
    path('autocomplete/', autocompleteJ, name='autocomplete'),
    path('get-saved-fields/', get_saved_fields, name='get-saved-fields'),
    # path('users-autocomplete/', UserAutocomplete.as_view(), name='users-autocomplete'),
    path('create-supplier/', create_supplier, name='create_supplier'),
    path('get_reason_choices/', get_reason_choices, name='get_reason_choices'),
    # path('categories/add/', add_multiple_categories_view, name='add_multiple_categories'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [ path('', admin_site.urls), ]

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('admin/storage/', complex_table_view, name='pivottable'),
#     path('pivottable-test/', complex_table_view, name='pivottable_test')
# path('pivot_table/', pivot_table_view, name='pivot_table'),
# path('storage/', include('storage.urls')),
# path('delete-near-product/<int:product_id>/', delete_near_product, name='delete_near_product'),
# ]
# from django.contrib.staticfiles.views import serve
# if settings.DEBUG:
#     urlpatterns += [
#         re_path(rf'^{settings.MEDIA_URL.lstrip("/")}(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),
#     ]
# if settings.DEBUG:
#     import debug_toolbar_old
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar_old.urls))
#     ] + urlpatterns

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = pageNotFound()
