from django.conf.urls.static import static

from django.contrib import admin

from storage.views import complex_table_view, delete_near_product
from warehouse import settings
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('storage/', include('storage.urls')),
    path('admin/storage/delete-near-product/', delete_near_product, name='delete_near_product'),
    path('pivottable-test/', complex_table_view, name='pivottable_test'),
    path('admin/storage/pivottable', complex_table_view, name='complex-table')
]

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('admin/storage/', complex_table_view, name='pivottable'),
#     path('pivottable-test/', complex_table_view, name='pivottable_test')
# ]

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls))
#     ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = pageNotFound()
