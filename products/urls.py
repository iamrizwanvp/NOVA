  # PRODUCTS URLS

from django.urls import path
from .views import ProductListCreateView
from . import views
from .views import ProductListCreateView, publish_product


urlpatterns = [
    path("api/products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("publish/", publish_product, name="publish-product"),
]
