require('dotenv').config();
const express = require('express');
const cors = require('cors');
const productRoutes = require('./routes/product.routes');
const { connectToDatabase } = require('./config/database');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/products', productRoutes);

// Database connection
connectToDatabase();

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});