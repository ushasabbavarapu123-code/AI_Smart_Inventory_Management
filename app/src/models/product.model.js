// app/src/models/product.model.js

const { getDatabase } = require('../database');
const { v4: uuidv4 } = require('uuid');

// Helper to run SQL with Promise
function run(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) reject(err);
      else resolve(this);
    });
  });
}

function all(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

function get(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

// CRUD operations
async function createProduct({ sku, name, category, unit_cost, reorder_point }) {
  const db = getDatabase();
  const product_id = uuidv4();
  const created_at = new Date().toISOString();
  const sql = `INSERT INTO products (product_id, sku, name, category, unit_cost, reorder_point, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)`;
  await run(db, sql, [product_id, sku, name, category, unit_cost, reorder_point, created_at]);
  return { product_id, sku, name, category, unit_cost, reorder_point, created_at };
}

async function getAllProducts() {
  const db = getDatabase();
  const sql = `SELECT * FROM products`;
  return await all(db, sql);
}

async function getProductById(product_id) {
  const db = getDatabase();
  const sql = `SELECT * FROM products WHERE product_id = ?`;
  return await get(db, sql, [product_id]);
}

async function updateProduct(product_id, fields) {
  const db = getDatabase();
  const allowed = ['sku', 'name', 'category', 'unit_cost', 'reorder_point'];
  const sets = [];
  const params = [];
  for (const key of allowed) {
    if (fields[key] !== undefined) {
      sets.push(`${key} = ?`);
      params.push(fields[key]);
    }
  }
  if (sets.length === 0) return getProductById(product_id);
  const sql = `UPDATE products SET ${sets.join(', ')} WHERE product_id = ?`;
  params.push(product_id);
  await run(db, sql, params);
  return getProductById(product_id);
}

async function deleteProduct(product_id) {
  const db = getDatabase();
  const sql = `DELETE FROM products WHERE product_id = ?`;
  await run(db, sql, [product_id]);
  return { success: true };
}

module.exports = {
  createProduct,
  getAllProducts,
  getProductById,
  updateProduct,
  deleteProduct,
};
