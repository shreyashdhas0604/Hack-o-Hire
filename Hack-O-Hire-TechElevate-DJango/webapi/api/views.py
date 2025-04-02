import logging
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Product
from django.views.decorators.csrf import csrf_exempt
from opentelemetry import trace
import structlog

# Configure Logger
logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)

# Create Product
@csrf_exempt
def create_product(request):
    if request.method == "POST":
        try:
            body_unicode = request.body.decode("utf-8")
            logger.info("Raw request body", body=body_unicode)

            data = json.loads(body_unicode)
            logger.info("Parsed data", data=data)

            name = data.get("name")
            description = data.get("description", "")
            price = data.get("price")

            if not name or not price:
                logger.error("Missing required fields", error="Name and price required")
                return JsonResponse({"error": "Name and price are required"}, status=400)

            product = Product.objects.create(name=name, description=description, price=price)
            logger.info("Product created", product_id=product.id)

            return JsonResponse({"message": "Product created", "id": product.id}, status=201)

        except json.JSONDecodeError:
            logger.error("Invalid JSON format", error="JSONDecodeError")
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    logger.warning("Invalid request method", method=request.method)
    return JsonResponse({"error": "Invalid request method"}, status=405)

# List Products
def list_products(request):
    products = Product.objects.values()
    
    logger.info("Retrieved Product List")
    return JsonResponse(list(products), safe=False)

# Retrieve Product
@csrf_exempt
def product_detail(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)

        logger.info(f"Fetching product details: {product.id} - {product.name}")

        return JsonResponse({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": str(product.price),  # Convert Decimal to string for JSON
            "created_at": product.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": product.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }, status=200)

    except Exception as e:
        logger.error(f"Error fetching product details: {str(e)}")
        return JsonResponse({"error": "Product not found"}, status=404)

# Update Product
@csrf_exempt
def update_product(request, product_id):
    try:
        body_unicode = request.body.decode("utf-8")
        logger.info(f"Raw request body: {body_unicode}")  # Log raw request body

        data = json.loads(body_unicode)
        logger.info(f"Parsed data: {data}")  # Log parsed data

        product = get_object_or_404(Product, id=product_id)

        product.name = data.get("name", product.name)
        product.description = data.get("description", product.description)
        product.price = data.get("price", product.price)
        product.save()

        logger.info(f"Product updated: {product.id} - {product.name}")
        return JsonResponse({"message": "Product updated!", "id": product.id}, status=200)

    except json.JSONDecodeError:
        logger.error("Invalid JSON format")
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

# Delete Product
@csrf_exempt
def delete_product(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)

        logger.info(f"Deleting product: {product.id} - {product.name}")
        product.delete()

        return JsonResponse({"message": "Product deleted successfully!"}, status=200)

    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
