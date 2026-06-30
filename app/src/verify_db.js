const { initDatabase, getDatabase } = require('./database');

async function verify() {
  try {
    console.log('--- Starting DB Verification ---');
    await initDatabase();
    const db = getDatabase();

    const tables = ['products', 'inventory', 'sales', 'forecasts', 'suppliers', 'purchase_orders', 'users', 'audit_logs'];

    for (const table of tables) {
      await new Promise((resolve, reject) => {
        db.get(`SELECT COUNT(*) as count FROM ${table}`, (err, row) => {
          if (err) {
            console.error(`❌ Table "${table}" verification failed:`, err.message);
            reject(err);
          } else {
            console.log(`✅ Table "${table}" exists. Record count: ${row.count}`);
            resolve();
          }
        });
      });
    }

    // Execute a sample SELECT query to verify joins are working
    console.log('\n--- Running Sample SELECT Query (Sales with Products) ---');
    await new Promise((resolve, reject) => {
      db.all(
        `SELECT s.sale_id, p.name, p.category, s.sale_date, s.quantity, s.unit_price 
         FROM sales s 
         JOIN products p ON s.product_id = p.product_id 
         LIMIT 5`,
        (err, rows) => {
          if (err) {
            console.error('❌ Sample query failed:', err.message);
            reject(err);
          } else {
            console.log('✅ Sample sales records retrieved successfully:');
            console.table(rows);
            resolve();
          }
        }
      );
    });

    console.log('\n--- DB Verification Successful! ---');
    process.exit(0);
  } catch (error) {
    console.error('❌ DB Verification Failed:', error);
    process.exit(1);
  }
}

verify();
