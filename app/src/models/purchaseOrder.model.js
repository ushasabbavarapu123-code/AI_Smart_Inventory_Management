// app/src/models/purchaseOrder.model.js

const { getDatabase } = require('../database');
const crypto = require('crypto');
const uuidv4 = () => crypto.randomUUID();

async function getAllPurchaseOrders(filters = {}) {
  const db = getDatabase();
  let sql = `SELECT po.*, p.name as product_name, p.sku, s.name as supplier_name FROM purchase_orders po
             JOIN products p ON po.product_id = p.product_id
             JOIN suppliers s ON po.supplier_id = s.supplier_id`;
  const conditions = [];
  const params = [];

  if (filters.status) {
    conditions.push('po.status = ?');
    params.push(filters.status);
  }
  if (filters.supplier_id) {
    conditions.push('po.supplier_id = ?');
    params.push(filters.supplier_id);
  }

  if (conditions.length > 0) {
    sql += ` WHERE ` + conditions.join(' AND ');
  }

  sql += ` ORDER BY po.order_date DESC`;

  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

async function getPurchaseOrderById(po_id) {
  const db = getDatabase();
  const sql = `SELECT po.*, p.name as product_name, p.sku, s.name as supplier_name FROM purchase_orders po
               JOIN products p ON po.product_id = p.product_id
               JOIN suppliers s ON po.supplier_id = s.supplier_id
               WHERE po.po_id = ?`;
  return new Promise((resolve, reject) => {
    db.get(sql, [po_id], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

async function createPurchaseOrder(poData) {
  const db = getDatabase();
  const { supplier_id, product_id, quantity, unit_cost, expected_delivery, notes } = poData;
  const po_id = uuidv4();
  const order_date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const created_at = new Date().toISOString();
  const status = 'Pending';

  const sql = `INSERT INTO purchase_orders (po_id, supplier_id, product_id, quantity, unit_cost, order_date, expected_delivery, status, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`;
  return new Promise((resolve, reject) => {
    db.run(sql, [po_id, supplier_id, product_id, quantity, unit_cost, order_date, expected_delivery, status, notes, created_at], function (err) {
      if (err) reject(err);
      else resolve({ po_id, supplier_id, product_id, quantity, unit_cost, order_date, expected_delivery, status, notes, created_at });
    });
  });
}

async function updatePurchaseOrderStatus(po_id, status, actual_delivery, user_id = 'system') {
  const db = getDatabase();
  const now = new Date().toISOString();

  return new Promise((resolve, reject) => {
    db.serialize(() => {
      db.get(`SELECT * FROM purchase_orders WHERE po_id = ?`, [po_id], (err, po) => {
        if (err) return reject(err);
        if (!po) {
          const error = new Error('Purchase order not found');
          error.statusCode = 404;
          return reject(error);
        }

        if (po.status === status) {
          return resolve(getPurchaseOrderById(po_id));
        }

        const isReceiving = (status === 'Received' && po.status !== 'Received');

        db.run('BEGIN TRANSACTION;', (err) => {
          if (err) return reject(err);

          const performUpdate = () => {
            const updatePOSql = `UPDATE purchase_orders SET status = ?, actual_delivery = ? WHERE po_id = ?`;
            db.run(updatePOSql, [status, actual_delivery || now.split('T')[0], po_id], (err) => {
              if (err) {
                db.run('ROLLBACK;');
                return reject(err);
              }

              const log_id = uuidv4();
              const insertLogSql = `INSERT INTO audit_logs (log_id, user_id, action, entity, entity_id, old_value, new_value, timestamp)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)`;
              db.run(insertLogSql, [log_id, user_id, 'UPDATE_PO_STATUS', 'purchase_orders', po_id, po.status, status, now], (err) => {
                if (err) {
                  db.run('ROLLBACK;');
                  return reject(err);
                }

                db.run('COMMIT;', (err) => {
                  if (err) return reject(err);
                  resolve(getPurchaseOrderById(po_id));
                });
              });
            });
          };

          if (isReceiving) {
            db.get(`SELECT * FROM inventory WHERE product_id = ?`, [po.product_id], (err, inv) => {
              if (err) {
                db.run('ROLLBACK;');
                return reject(err);
              }

              if (inv) {
                const newQty = inv.quantity + po.quantity;
                db.run(`UPDATE inventory SET quantity = ?, last_updated = ? WHERE inventory_id = ?`, [newQty, now, inv.inventory_id], (err) => {
                  if (err) {
                    db.run('ROLLBACK;');
                    return reject(err);
                  }

                  const invLogId = uuidv4();
                  const insertInvLogSql = `INSERT INTO audit_logs (log_id, user_id, action, entity, entity_id, old_value, new_value, timestamp)
                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`;
                  const oldVal = JSON.stringify({ quantity: inv.quantity });
                  const newVal = JSON.stringify({ quantity: newQty, po_id });

                  db.run(insertInvLogSql, [invLogId, user_id, 'PO_RECEIVED_STOCK_ADD', 'inventory', inv.inventory_id, oldVal, newVal, now], (err) => {
                    if (err) {
                      db.run('ROLLBACK;');
                      return reject(err);
                    }
                    performUpdate();
                  });
                });
              } else {
                const inv_id = uuidv4();
                db.run(`INSERT INTO inventory (inventory_id, product_id, location, quantity, last_updated) VALUES (?, ?, ?, ?, ?)`, [inv_id, po.product_id, 'Warehouse-A', po.quantity, now], (err) => {
                  if (err) {
                    db.run('ROLLBACK;');
                    return reject(err);
                  }

                  const invLogId = uuidv4();
                  const insertInvLogSql = `INSERT INTO audit_logs (log_id, user_id, action, entity, entity_id, old_value, new_value, timestamp)
                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`;
                  const newVal = JSON.stringify({ quantity: po.quantity, po_id });

                  db.run(insertInvLogSql, [invLogId, user_id, 'PO_RECEIVED_STOCK_CREATE', 'inventory', inv_id, null, newVal, now], (err) => {
                    if (err) {
                      db.run('ROLLBACK;');
                      return reject(err);
                    }
                    performUpdate();
                  });
                });
              }
            });
          } else {
            performUpdate();
          }
        });
      });
    });
  });
}

module.exports = {
  getAllPurchaseOrders,
  getPurchaseOrderById,
  createPurchaseOrder,
  updatePurchaseOrderStatus
};
