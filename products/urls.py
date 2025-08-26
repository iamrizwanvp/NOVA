  # PRODUCTS URLS

from django.urls import path
from .views import ProductListCreateView
from . import views


urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('publish/', views.publish_product, name='publish_product'),
]
