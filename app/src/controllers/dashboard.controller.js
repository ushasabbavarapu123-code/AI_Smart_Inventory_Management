// app/src/controllers/dashboard.controller.js

const { getDatabase } = require('../database');

function dbAll(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}

function dbGet(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
}

async function getSummary(req, res, next) {
  try {
    const db = getDatabase();

    // Total products
    const productCountRow = await dbGet(db, `SELECT COUNT(*) as count FROM products`);
    const total_products = productCountRow.count;

    // Low stock count (quantity < reorder_point)
    const lowStockRow = await dbGet(db, `
      SELECT COUNT(*) as count FROM inventory i
      JOIN products p ON i.product_id = p.product_id
      WHERE i.quantity < p.reorder_point
    `);
    const low_stock_count = lowStockRow.count;

    // Total inventory value (quantity * unit_cost)
    const invValueRow = await dbGet(db, `
      SELECT SUM(i.quantity * p.unit_cost) as total_value FROM inventory i
      JOIN products p ON i.product_id = p.product_id
    `);
    const total_inventory_value = Math.round((invValueRow.total_value || 0) * 100) / 100;

    // Pending purchase orders
    const pendingPORow = await dbGet(db, `SELECT COUNT(*) as count FROM purchase_orders WHERE status = 'Pending'`);
    const pending_orders = pendingPORow.count;

    // Stockout rate (products with 0 stock / total products * 100)
    const stockoutRow = await dbGet(db, `SELECT COUNT(*) as count FROM inventory WHERE quantity = 0`);
    const stockout_rate = total_products > 0 ? Math.round((stockoutRow.count / total_products) * 1000) / 10 : 0;

    // Monthly sales total (current calendar month)
    const now = new Date();
    const monthStart = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
    const monthlySalesRow = await dbGet(db, `
      SELECT SUM(quantity * unit_price) as monthly_total FROM sales
      WHERE sale_date >= ?
    `, [monthStart]);
    const monthly_sales_total = Math.round((monthlySalesRow.monthly_total || 0) * 100) / 100;

    // Total sales transactions
    const salesCountRow = await dbGet(db, `SELECT COUNT(*) as count FROM sales`);
    const total_sales_transactions = salesCountRow.count;

    // Total suppliers
    const supplierCountRow = await dbGet(db, `SELECT COUNT(*) as count FROM suppliers`);
    const total_suppliers = supplierCountRow.count;

    res.json({
      success: true,
      data: {
        total_products,
        total_suppliers,
        low_stock_count,
        total_inventory_value,
        pending_orders,
        stockout_rate,
        monthly_sales_total,
        total_sales_transactions
      }
    });
  } catch (err) {
    next(err);
  }
}

module.exports = {
  getSummary
};
