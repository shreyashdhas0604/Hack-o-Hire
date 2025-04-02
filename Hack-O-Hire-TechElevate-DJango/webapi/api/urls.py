from django.urls import path
from .views import create_product, list_products, product_detail, update_product, delete_product

urlpatterns = [
    path("products/", list_products, name="list_products"),
    path("products/create/", create_product, name="create_product"),
    path("products/<int:product_id>/", product_detail, name="product_detail"),
    path("products/<int:product_id>/update/", update_product, name="update_product"),
    path("products/<int:product_id>/delete/", delete_product, name="delete_product"),
]
