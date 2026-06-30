const fs = require('fs');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

// Resolve DB path. If it's relative in .env, resolve it from the app directory (process.cwd() or parent of src)
const envDbPath = process.env.DB_PATH || '../data/inventory.db';
const dbPath = path.isAbsolute(envDbPath) ? envDbPath : path.resolve(__dirname, '..', envDbPath);

// Ensure the directory exists
const dbDir = path.dirname(dbPath);
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

let db;

function initDatabase() {
  return new Promise((resolve, reject) => {
    db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('Error opening database:', err.message);
        return reject(err);
      }
      console.log(`Database connected successfully at: ${dbPath}`);

      // Enable WAL mode and foreign key constraints
      db.serialize(() => {
        db.run('PRAGMA journal_mode = WAL;', (err) => {
          if (err) console.error('Error enabling WAL mode:', err.message);
          else console.log('SQLite WAL mode enabled.');
        });

        db.run('PRAGMA foreign_keys = ON;', (err) => {
          if (err) console.error('Error enabling foreign keys:', err.message);
          else console.log('SQLite foreign key constraints enabled.');
        });

        // Run migrations/schema initialization
        createTables(resolve, reject);
      });
    });
  });
}

function createTables(resolve, reject) {
  db.serialize(() => {
    // 1. Products table
    db.run(`
      CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        sku TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT,
        unit_cost REAL NOT NULL CHECK (unit_cost >= 0),
        reorder_point INTEGER NOT NULL DEFAULT 10,
        created_at TEXT NOT NULL
      )
    `);

    // 2. Inventory table
    db.run(`
      CREATE TABLE IF NOT EXISTS inventory (
        inventory_id TEXT PRIMARY KEY,
        product_id TEXT NOT NULL,
        location TEXT NOT NULL DEFAULT 'Warehouse-A',
        quantity INTEGER NOT NULL CHECK (quantity >= 0),
        last_updated TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE RESTRICT
      )
    `);

    // 3. Sales table
    db.run(`
      CREATE TABLE IF NOT EXISTS sales (
        sale_id TEXT PRIMARY KEY,
        product_id TEXT NOT NULL,
        sale_date TEXT NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        unit_price REAL NOT NULL CHECK (unit_price > 0),
        customer_type TEXT DEFAULT 'Retail',
        created_at TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
      )
    `);

    // 4. Forecasts table
    db.run(`
      CREATE TABLE IF NOT EXISTS forecasts (
        forecast_id TEXT PRIMARY KEY,
        product_id TEXT NOT NULL,
        forecast_date TEXT NOT NULL,
        predicted_qty INTEGER NOT NULL CHECK (predicted_qty >= 0),
        confidence_low INTEGER NOT NULL,
        confidence_high INTEGER NOT NULL,
        model_used TEXT NOT NULL DEFAULT 'ARIMA',
        generated_at TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (product_id)
      )
    `);

    // 5. Suppliers table
    db.run(`
      CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        contact_person TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        lead_time_days INTEGER NOT NULL CHECK (lead_time_days > 0),
        rating REAL CHECK (rating >= 1.0 AND rating <= 5.0),
        created_at TEXT NOT NULL
      )
    `);

    // 6. Purchase Orders table
    db.run(`
      CREATE TABLE IF NOT EXISTS purchase_orders (
        po_id TEXT PRIMARY KEY,
        supplier_id TEXT NOT NULL,
        product_id TEXT NOT NULL,
        quantity INTEGER NOT NULL CHECK (quantity > 0),
        unit_cost REAL NOT NULL,
        order_date TEXT NOT NULL,
        expected_delivery TEXT,
        actual_delivery TEXT,
        status TEXT NOT NULL CHECK (status IN ('Pending','Sent','Received','Cancelled')),
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
      )
    `);

    // 7. Users table
    db.run(`
      CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('Manager','Planner','Analyst','Admin')),
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        last_login TEXT
      )
    `);

    // 8. Audit Logs table
    db.run(`
      CREATE TABLE IF NOT EXISTS audit_logs (
        log_id TEXT PRIMARY KEY,
        user_id TEXT,
        action TEXT NOT NULL,
        entity TEXT NOT NULL,
        entity_id TEXT,
        old_value TEXT,
        new_value TEXT,
        ip_address TEXT,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
      )
    `);

    // Create Indexes
    db.run(`CREATE INDEX IF NOT EXISTS idx_products_sku ON products (sku)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_products_category ON products (category)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory (product_id)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_inventory_location ON inventory (location)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales (product_id)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales (sale_date)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_sales_product_date ON sales (product_id, sale_date)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_forecasts_product_id ON forecasts (product_id)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_forecasts_forecast_date ON forecasts (forecast_date)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_po_supplier_id ON purchase_orders (supplier_id)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_po_product_id ON purchase_orders (product_id)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_po_status ON purchase_orders (status)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_users_role ON users (role)`, (err) => {
      if (err) {
        console.error('Error creating schemas:', err.message);
        return reject(err);
      }
      console.log('Database tables and indexes created/verified.');
      resolve();
    });
  });
}

function getDatabase() {
  if (!db) {
    throw new Error('Database not initialized. Call initDatabase() first.');
  }
  return db;
}

function closeDatabase() {
  return new Promise((resolve, reject) => {
    if (db) {
      db.close((err) => {
        if (err) {
          console.error('Error closing database:', err.message);
          return reject(err);
        }
        console.log('Database connection closed.');
        db = null;
        resolve();
      });
    } else {
      resolve();
    }
  });
}

module.exports = {
  initDatabase,
  getDatabase,
  closeDatabase,
  dbPath
};
