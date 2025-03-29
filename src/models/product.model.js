const { pool } = require('../config/database');

class Product {
  static async findAll() {
    const [rows] = await pool.query('SELECT * FROM products');
    return rows;
  }

  static async findById(id) {
    const [rows] = await pool.query('SELECT * FROM products WHERE id = ?', [id]);
    return rows[0];
  }

  static async create(productData) {
    const { name, description, price } = productData;
    const [result] = await pool.query(
      'INSERT INTO products (name, description, price) VALUES (?, ?, ?)',
      [name, description, price]
    );
    return { id: result.insertId, ...productData };
  }

  static async update(id, productData) {
    const { name, description, price } = productData;
    await pool.query(
      'UPDATE products SET name = ?, description = ?, price = ? WHERE id = ?',
      [name, description, price, id]
    );
    return this.findById(id);
  }

  static async delete(id) {
    const [result] = await pool.query('DELETE FROM products WHERE id = ?', [id]);
    return result.affectedRows > 0;
  }
}

module.exports = Product;