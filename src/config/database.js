const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'nodejs_crud',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

const createProductsTable = async (connection) => {
  const createTableSQL = `
    CREATE TABLE IF NOT EXISTS products (
      id INT AUTO_INCREMENT PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      description TEXT,
      price DECIMAL(10, 2) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
  `;
  await connection.query(createTableSQL);
  console.log('Products table created or already exists');
};

const connectToDatabase = async () => {
  try {
    const connection = await pool.getConnection();
    console.log('Successfully connected to the database');
    await createProductsTable(connection);
    connection.release();
  } catch (error) {
    console.error('Error connecting to the database:', error.message);
    process.exit(1);
  }
};

module.exports = {
  pool,
  connectToDatabase
};