# products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    
    # API endpoints
    path('api/products/', views.product_list_create, name='product-list-create'),        # GET & POST
    path('api/products/<int:id>/', views.product_detail, name='product-detail'),         # GET, PUT, PATCH, DELETE
    path('api/products/feed/', views.product_feed, name='product-feed'),                 # public feed
    
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('page/', views.products_page, name='products-page'),  # for products.html
]



from django.urls import path
from . import views










