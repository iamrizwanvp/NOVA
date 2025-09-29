# products/views.py
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from rest_framework.exceptions import PermissionDenied









from .models import Product
from .serializers import ProductSerializer

# API: list & create
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
@parser_classes([MultiPartParser, FormParser])
def product_list_create(request):
    if request.method == 'GET':
        if request.user.is_authenticated and request.GET.get('my') == 'true':
            products = Product.objects.filter(owner=request.user).order_by('-created_at')
        else:
            products = Product.objects.all().order_by('-created_at')
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST → create
    serializer = ProductSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API: retrieve, update, delete

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
@parser_classes([MultiPartParser, FormParser])
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'GET':
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method in ['PUT', 'PATCH']:
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.")
        if request.user != product.owner:
            raise PermissionDenied("Only the owner can update this product.")

        # ✅ bind serializer to existing product instance
        serializer = ProductSerializer(
            product,  # bind here
            data=request.data,
            partial=(request.method == 'PATCH'),
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()  # updates the existing product
            return Response({"message": "Product updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.")
        if request.user != product.owner:
            raise PermissionDenied("Only the owner can delete this product.")
        product.delete()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# API: feed (public)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_feed(request):
    products = Product.objects.all().order_by('-created_at')
    serializer = ProductSerializer(products, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# HTML dashboard view (protected; used under /products/dashboard/)
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'products/dashboard.html')



 # dashboard html page 
from django.shortcuts import render
from django.contrib.auth.decorators import login_required






from django.shortcuts import render


# HTML views
@login_required
def dashboard(request):
    return render(request, 'products/dashboard.html')

@login_required
def products_page(request):
    return render(request, 'products/products.html')



from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Product
from .serializers import ProductSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsOwnerOrReadOnly

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

