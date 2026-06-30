// app/src/models/inventory.model.js

const { getDatabase } = require('../database');
const { v4: uuidv4 } = require('uuid');

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

// CRUD operations for inventory
async function createInventory({ product_id, location = 'Warehouse-A', quantity }) {
  const db = getDatabase();
  const inventory_id = uuidv4();
  const last_updated = new Date().toISOString();
  const sql = `INSERT INTO inventory (inventory_id, product_id, location, quantity, last_updated)
               VALUES (?, ?, ?, ?, ?)`;
  await run(db, sql, [inventory_id, product_id, location, quantity, last_updated]);
  return { inventory_id, product_id, location, quantity, last_updated };
}

async function getAllInventory() {
  const db = getDatabase();
  const sql = `SELECT * FROM inventory`;
  return await all(db, sql);
}

async function getInventoryById(inventory_id) {
  const db = getDatabase();
  const sql = `SELECT * FROM inventory WHERE inventory_id = ?`;
  return await get(db, sql, [inventory_id]);
}

async function updateInventory(inventory_id, fields) {
  const db = getDatabase();
  const allowed = ['product_id', 'location', 'quantity'];
  const sets = [];
  const params = [];
  for (const key of allowed) {
    if (fields[key] !== undefined) {
      sets.push(`${key} = ?`);
      params.push(fields[key]);
    }
  }
  if (sets.length === 0) return getInventoryById(inventory_id);
  const sql = `UPDATE inventory SET ${sets.join(', ')}, last_updated = ? WHERE inventory_id = ?`;
  const now = new Date().toISOString();
  params.push(now, inventory_id);
  await run(db, sql, params);
  return getInventoryById(inventory_id);
}

async function deleteInventory(inventory_id) {
  const db = getDatabase();
  const sql = `DELETE FROM inventory WHERE inventory_id = ?`;
  await run(db, sql, [inventory_id]);
  return { success: true };
}

module.exports = {
  createInventory,
  getAllInventory,
  getInventoryById,
  updateInventory,
  deleteInventory,
};
