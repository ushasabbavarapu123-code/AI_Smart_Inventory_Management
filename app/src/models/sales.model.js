// app/src/models/sales.model.js

const { getDatabase } = require('../database');
const crypto = require('crypto');
const uuidv4 = () => crypto.randomUUID();

async function getAllSales(filters = {}) {
  const db = getDatabase();
  let sql = `SELECT s.*, p.name as product_name, p.sku FROM sales s
             JOIN products p ON s.product_id = p.product_id`;
  const conditions = [];
  const params = [];

  if (filters.product_id) {
    conditions.push('s.product_id = ?');
    params.push(filters.product_id);
  }
  if (filters.from) {
    conditions.push('s.sale_date >= ?');
    params.push(filters.from);
  }
  if (filters.to) {
    conditions.push('s.sale_date <= ?');
    params.push(filters.to);
  }

  if (conditions.length > 0) {
    sql += ` WHERE ` + conditions.join(' AND ');
  }

  sql += ` ORDER BY s.sale_date DESC`;

  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

async function createSale(saleData, user_id = 'system') {
  const db = getDatabase();
  const { product_id, sale_date, quantity, unit_price, customer_type = 'Retail' } = saleData;
  const sale_id = uuidv4();
  const created_at = new Date().toISOString();

  return new Promise((resolve, reject) => {
    db.serialize(() => {
      // 1. Verify product exists
      db.get(`SELECT * FROM products WHERE product_id = ?`, [product_id], (err, product) => {
        if (err) return reject(err);
        if (!product) {
          const error = new Error('Product not found');
          error.statusCode = 404;
          return reject(error);
        }

        // 2. Check inventory quantity
        db.get(`SELECT * FROM inventory WHERE product_id = ?`, [product_id], (err, inv) => {
          if (err) return reject(err);
          if (!inv || inv.quantity < quantity) {
            const error = new Error(`Insufficient stock. Available: ${inv ? inv.quantity : 0}`);
            error.statusCode = 400;
            return reject(error);
          }

          // Start SQLite transaction manually
          db.run('BEGIN TRANSACTION;', (err) => {
            if (err) return reject(err);

            // 3. Decrement inventory
            const newQty = inv.quantity - quantity;
            const updateInvSql = `UPDATE inventory SET quantity = ?, last_updated = ? WHERE inventory_id = ?`;
            db.run(updateInvSql, [newQty, created_at, inv.inventory_id], (err) => {
              if (err) {
                db.run('ROLLBACK;');
                return reject(err);
              }

              // 4. Record the sale
              const insertSaleSql = `INSERT INTO sales (sale_id, product_id, sale_date, quantity, unit_price, customer_type, created_at)
                                     VALUES (?, ?, ?, ?, ?, ?, ?)`;
              db.run(insertSaleSql, [sale_id, product_id, sale_date, quantity, unit_price, customer_type, created_at], (err) => {
                if (err) {
                  db.run('ROLLBACK;');
                  return reject(err);
                }

                // 5. Create audit log entry
                const log_id = uuidv4();
                const insertLogSql = `INSERT INTO audit_logs (log_id, user_id, action, entity, entity_id, old_value, new_value, timestamp)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)`;
                const oldVal = JSON.stringify({ quantity: inv.quantity });
                const newVal = JSON.stringify({ quantity: newQty, sale_id });

                db.run(insertLogSql, [log_id, user_id, 'CREATE_SALE', 'sales', sale_id, oldVal, newVal, created_at], (err) => {
                  if (err) {
                    db.run('ROLLBACK;');
                    return reject(err);
                  }

                  // Commit transaction
                  db.run('COMMIT;', (err) => {
                    if (err) return reject(err);
                    resolve({
                      sale_id,
                      product_id,
                      sale_date,
                      quantity,
                      unit_price,
                      customer_type,
                      created_at
                    });
                  });
                });
              });
            });
          });
        });
      });
    });
  });
}

module.exports = {
  getAllSales,
  createSale
};
