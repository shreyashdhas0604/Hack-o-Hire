const Product = require('../models/product.model');

class ProductController {
  static async getAllProducts(req, res) {
    try {
      const products = await Product.findAll();
      res.json(products);
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  }

  static async getProductById(req, res) {
    try {
      const product = await Product.findById(req.params.id);
      if (!product) {
        return res.status(404).json({ message: 'Product not found' });
      }
      res.json(product);
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  }

  static async createProduct(req, res) {
    try {
      const { name, description, price } = req.body;
      if (!name || !price) {
        return res.status(400).json({ message: 'Name and price are required' });
      }
      const product = await Product.create({ name, description, price });
      res.status(201).json(product);
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  }

  static async updateProduct(req, res) {
    try {
      const { name, description, price } = req.body;
      if (!name || !price) {
        return res.status(400).json({ message: 'Name and price are required' });
      }
      const product = await Product.update(req.params.id, { name, description, price });
      if (!product) {
        return res.status(404).json({ message: 'Product not found' });
      }
      res.json(product);
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  }

  static async deleteProduct(req, res) {
    try {
      const success = await Product.delete(req.params.id);
      if (!success) {
        return res.status(404).json({ message: 'Product not found' });
      }
      res.status(204).send();
    } catch (error) {
      res.status(500).json({ message: error.message });
    }
  }
}

module.exports = ProductController;