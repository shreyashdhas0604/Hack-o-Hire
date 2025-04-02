const express = require('express');
const ProductController = require('../controllers/product.controller');

const router = express.Router();

// GET /api/products - Get all products
router.get('/', ProductController.getAllProducts);

// GET /api/products/:id - Get a single product by ID
router.get('/:id', ProductController.getProductById);

// POST /api/products - Create a new product
router.post('/', ProductController.createProduct);

// PUT /api/products/:id - Update a product
router.put('/:id', ProductController.updateProduct);

// DELETE /api/products/:id - Delete a product
router.delete('/:id', ProductController.deleteProduct);

module.exports = router;