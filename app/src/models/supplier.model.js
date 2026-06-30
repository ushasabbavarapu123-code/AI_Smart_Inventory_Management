// app/src/models/supplier.model.js

const { getDatabase } = require('../database');
const crypto = require('crypto');
const uuidv4 = () => crypto.randomUUID();

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

// CRUD operations for suppliers
async function createSupplier({ name, contact_email, lead_time_days, rating }) {
  const db = getDatabase();
  const supplier_id = uuidv4();
  const created_at = new Date().toISOString();
  const sql = `INSERT INTO suppliers (supplier_id, name, contact_email, lead_time_days, rating, created_at)
               VALUES (?, ?, ?, ?, ?, ?)`;
  await run(db, sql, [supplier_id, name, contact_email, lead_time_days, rating, created_at]);
  return { supplier_id, name, contact_email, lead_time_days, rating, created_at };
}

async function getAllSuppliers() {
  const db = getDatabase();
  const sql = `SELECT * FROM suppliers`;
  return await all(db, sql);
}

async function getSupplierById(supplier_id) {
  const db = getDatabase();
  const sql = `SELECT * FROM suppliers WHERE supplier_id = ?`;
  return await get(db, sql, [supplier_id]);
}

async function updateSupplier(supplier_id, fields) {
  const db = getDatabase();
  const allowed = ['name', 'contact_email', 'lead_time_days', 'rating'];
  const sets = [];
  const params = [];
  for (const key of allowed) {
    if (fields[key] !== undefined) {
      sets.push(`${key} = ?`);
      params.push(fields[key]);
    }
  }
  if (sets.length === 0) return getSupplierById(supplier_id);
  const sql = `UPDATE suppliers SET ${sets.join(', ')} WHERE supplier_id = ?`;
  params.push(supplier_id);
  await run(db, sql, params);
  return getSupplierById(supplier_id);
}

async function deleteSupplier(supplier_id) {
  const db = getDatabase();
  const sql = `DELETE FROM suppliers WHERE supplier_id = ?`;
  await run(db, sql, [supplier_id]);
  return { success: true };
}

module.exports = {
  createSupplier,
  getAllSuppliers,
  getSupplierById,
  updateSupplier,
  deleteSupplier,
};
