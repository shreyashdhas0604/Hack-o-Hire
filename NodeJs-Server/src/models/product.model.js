const { pool } = require('../config/database');
const opentelemetry = require('@opentelemetry/api');
const tracer = opentelemetry.trace.getTracer('product-operations');

class Product {
  static async findAll() {
    const span = tracer.startSpan('Product.findAll');
    try {
      const [rows] = await pool.query('SELECT * FROM products');
      span.setAttributes({
        'db.rowCount': rows.length,
        'db.operation': 'SELECT',
        'db.table': 'products'
      });
      return rows;
    } catch (error) {
      span.setStatus({
        code: opentelemetry.SpanStatusCode.ERROR,
        message: error.message
      });
      throw error;
    } finally {
      span.end();
    }
  }

  static async create(productData) {
    const span = tracer.startSpan('Product.create');
    try {
      span.setAttributes({
        'product.name': productData.name,
        'product.price': productData.price
      });
      
      const { name, description, price } = productData;
      const [result] = await pool.query(
        'INSERT INTO products (name, description, price) VALUES (?, ?, ?)',
        [name, description, price]
      );
      
      span.setAttributes({
        'db.insertId': result.insertId
      });
      return { id: result.insertId, ...productData };
    } catch (error) {
      span.setStatus({
        code: opentelemetry.SpanStatusCode.ERROR,
        message: error.message
      });
      throw error;
    } finally {
      span.end();
    }
  }

  static async findById(id) {
    const span = tracer.startSpan('Product.findById');
    try {
      span.setAttributes({
        'product.id': id,
        'db.operation': 'SELECT',
        'db.table': 'products'
      });

      const [rows] = await pool.query('SELECT * FROM products WHERE id = ?', [id]);
      
      if (rows.length === 0) {
        return null;
      }

      span.setAttributes({
        'db.rowCount': rows.length
      });

      return rows[0];
    } catch (error) {
      span.setStatus({
        code: opentelemetry.SpanStatusCode.ERROR,
        message: error.message
      });
      throw error;
    } finally {
      span.end();
    }
  }

  static async update(id, productData) {
    const span = tracer.startSpan('Product.update');
    try {
      span.setAttributes({
        'product.id': id,
        'product.name': productData.name,
        'product.price': productData.price,
        'db.operation': 'UPDATE',
        'db.table': 'products'
      });

      const { name, description, price } = productData;
      const [result] = await pool.query(
        'UPDATE products SET name = ?, description = ?, price = ? WHERE id = ?',
        [name, description, price, id]
      );

      if (result.affectedRows === 0) {
        return null;
      }

      span.setAttributes({
        'db.affectedRows': result.affectedRows
      });

      return { id, ...productData };
    } catch (error) {
      span.setStatus({
        code: opentelemetry.SpanStatusCode.ERROR,
        message: error.message
      });
      throw error;
    } finally {
      span.end();
    }
  }

  static async delete(id) {
    const span = tracer.startSpan('Product.delete');
    try {
      span.setAttributes({
        'product.id': id,
        'db.operation': 'DELETE',
        'db.table': 'products'
      });

      const [result] = await pool.query('DELETE FROM products WHERE id = ?', [id]);

      span.setAttributes({
        'db.affectedRows': result.affectedRows
      });

      return result.affectedRows > 0;
    } catch (error) {
      span.setStatus({
        code: opentelemetry.SpanStatusCode.ERROR,
        message: error.message
      });
      throw error;
    } finally {
      span.end();
    }
  }
}

module.exports = Product;