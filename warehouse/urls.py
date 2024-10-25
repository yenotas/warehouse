from django.conf.urls.static import static

from django.contrib import admin
from storage.admin import admin_site
from storage.views import pageNotFound, delete_near_product, complex_table_view

from warehouse import settings
from django.urls import path, include


urlpatterns = [
    path('admin/', admin_site.urls),
    path('admin/storage/delete-near-product/', delete_near_product, name='delete_near_product'),
    path('admin/storage/', complex_table_view, name='pivottable'),
    path('pivottable-test/', complex_table_view, name='pivottable_test')
]

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls))
#     ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = pageNotFound()
