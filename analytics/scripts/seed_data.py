import os
import sys
import sqlite3
import uuid
import random
from datetime import datetime, timedelta

def get_db_path():
    # Resolve the database path. Try to look at ../app/.env first.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(script_dir)) # Up 2 levels to project root
    
    env_path = os.path.join(project_dir, 'app', '.env')
    db_path = None
    
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('DB_PATH='):
                        val = line.strip().split('=', 1)[1]
                        # Resolve path relative to app folder
                        db_path = os.path.abspath(os.path.join(project_dir, 'app', val))
                        break
        except Exception as e:
            print(f"Error reading app/.env: {e}")
            
    if not db_path:
        # Default fallback
        db_path = os.path.abspath(os.path.join(project_dir, 'data', 'inventory.db'))
        
    return db_path

def main():
    db_path = get_db_path()
    print(f"Target Database File: {db_path}")
    
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable FKs
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    try:
        # Clear existing data to ensure repeatable runs
        print("Clearing existing data...")
        tables = ['audit_logs', 'purchase_orders', 'sales', 'forecasts', 'inventory', 'products', 'suppliers', 'users']
        for t in tables:
            try:
                cursor.execute(f"DELETE FROM {t};")
            except sqlite3.OperationalError as e:
                print(f"Table {t} might not exist yet: {e}")
        
        conn.commit()
        
        # 1. Generate Users (5 users)
        print("Generating users...")
        users = [
            (str(uuid.uuid4()), "admin@smartinventory.com", "$2b$10$eFytJDGtjbThpOaW/gTte.N.gR2B4OIQyE3l062wXG/5W7N9pC5O2", "Alice Admin", "Admin", 1, datetime.now().isoformat(), None),
            (str(uuid.uuid4()), "manager@smartinventory.com", "$2b$10$eFytJDGtjbThpOaW/gTte.N.gR2B4OIQyE3l062wXG/5W7N9pC5O2", "Bob Manager", "Manager", 1, datetime.now().isoformat(), None),
            (str(uuid.uuid4()), "planner@smartinventory.com", "$2b$10$eFytJDGtjbThpOaW/gTte.N.gR2B4OIQyE3l062wXG/5W7N9pC5O2", "Charlie Planner", "Planner", 1, datetime.now().isoformat(), None),
            (str(uuid.uuid4()), "analyst@smartinventory.com", "$2b$10$eFytJDGtjbThpOaW/gTte.N.gR2B4OIQyE3l062wXG/5W7N9pC5O2", "David Analyst", "Analyst", 1, datetime.now().isoformat(), None),
            (str(uuid.uuid4()), "staff@smartinventory.com", "$2b$10$eFytJDGtjbThpOaW/gTte.N.gR2B4OIQyE3l062wXG/5W7N9pC5O2", "Emily Staff", "Planner", 1, datetime.now().isoformat(), None)
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?);", users)
        
        # 2. Generate Suppliers (10 suppliers)
        print("Generating suppliers...")
        supplier_categories = ["Electronics", "Food", "Apparel", "Home", "Sports"]
        suppliers = []
        for i in range(1, 11):
            s_id = str(uuid.uuid4())
            name = f"Supplier {i} ({random.choice(supplier_categories)})"
            contact_person = f"Contact Person {i}"
            contact_email = f"contact{i}@supplier{i}.com"
            contact_phone = f"+91 {9876500000 + i}"
            lead_time_days = random.randint(2, 14)
            rating = round(random.uniform(3.5, 5.0), 1)
            created_at = datetime.now().isoformat()
            suppliers.append((s_id, name, contact_person, contact_email, contact_phone, lead_time_days, rating, created_at))
            
        cursor.executemany("INSERT INTO suppliers VALUES (?, ?, ?, ?, ?, ?, ?, ?);", suppliers)
        
        # 3. Generate Products (50 products)
        print("Generating products...")
        categories = ["Electronics", "Food", "Apparel", "Home", "Sports"]
        products = []
        product_ids = []
        
        sku_counters = {cat: 100 for cat in categories}
        
        product_names_pool = {
            "Electronics": ["Smartphone X", "Laptop Pro", "Wireless Earbuds", "Smart Watch", "Tablet S", "Bluetooth Speaker", "Charger Hub", "Keyboard Mech", "Gaming Mouse", "Display 4K"],
            "Food": ["Organic Oats 1kg", "Almond Milk 1L", "Whole Wheat Bread", "Greek Yogurt", "Olive Oil 500ml", "Dark Chocolate", "Green Tea", "Avocado Pack", "Spaghetti 500g", "Honey Jar"],
            "Apparel": ["Cotton T-Shirt", "Denim Jacket", "Running Shoes", "Active Shorts", "Socks Pack", "Leather Belt", "Winter Beanie", "Puffer Vest", "Sneakers Classic", "Yoga Pants"],
            "Home": ["Scented Candle", "Desk Lamp LED", "Storage Bins", "Cushion Cover", "Bath Towel Set", "Coffee Mug Cer", "Wall Clock", "Bake Ware Set", "Hanger Pack", "Water Bottle Metal"],
            "Sports": ["Dumbbell 5kg", "Yoga Mat", "Resistance Bands", "Soccer Ball", "Waterproof Backpack", "Skipping Rope", "Tennis Racket", "Foam Roller", "Cycling Helmet", "Gym Gloves"]
        }
        
        for i in range(50):
            p_id = str(uuid.uuid4())
            category = categories[i % len(categories)]
            
            sku_counters[category] += 1
            sku = f"{category[:3].upper()}-{sku_counters[category]}"
            
            # Select unique names if possible
            pool = product_names_pool[category]
            name = pool[i // len(categories) % len(pool)]
            # If name is already taken, add a variation
            if name in [p[2] for p in products]:
                name = f"{name} Plus"
                
            # Pricing rules
            if category == "Electronics":
                unit_cost = round(random.uniform(1000, 15000), 2)
            elif category == "Food":
                unit_cost = round(random.uniform(20, 250), 2)
            elif category == "Apparel":
                unit_cost = round(random.uniform(150, 1200), 2)
            elif category == "Home":
                unit_cost = round(random.uniform(100, 800), 2)
            else: # Sports
                unit_cost = round(random.uniform(200, 2000), 2)
                
            reorder_point = random.choice([5, 10, 15, 20, 30])
            created_at = (datetime.now() - timedelta(days=365)).isoformat()
            
            products.append((p_id, sku, name, category, unit_cost, reorder_point, created_at))
            product_ids.append(p_id)
            
        cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?);", products)
        
        # 4. Generate Inventory (50 records - 1 per product)
        print("Generating inventory...")
        inventory_records = []
        for p_id in product_ids:
            inv_id = str(uuid.uuid4())
            location = random.choice(["Warehouse-A", "Warehouse-B"])
            # Keep quantity above reorder point to start
            quantity = random.randint(15, 300)
            last_updated = datetime.now().isoformat()
            inventory_records.append((inv_id, p_id, location, quantity, last_updated))
            
        cursor.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?, ?);", inventory_records)
        
        # 5. Generate Sales (500+ records, let's do ~800 to be safe and span 12 months)
        print("Generating sales...")
        sales_records = []
        # Span 365 days
        start_date = datetime.now() - timedelta(days=365)
        
        # For each product, let's generate some sales
        for p_id in product_ids:
            # Retrieve cost to make price reasonable
            prod_cost = [p[4] for p in products if p[0] == p_id][0]
            # Retail price has a markup of 20% to 50%
            unit_price = round(prod_cost * random.uniform(1.2, 1.5), 2)
            
            # Number of sales for this product (between 10 and 25)
            num_sales = random.randint(12, 25)
            
            # Generate random sale dates spread across the year
            sale_offsets = sorted(random.sample(range(1, 365), num_sales))
            
            for offset in sale_offsets:
                s_date = start_date + timedelta(days=offset)
                sale_id = str(uuid.uuid4())
                qty = random.randint(1, 10)
                cust_type = random.choice(["Retail", "Retail", "Retail", "Wholesale"])
                
                # Wholesale orders have a discount and larger quantity
                if cust_type == "Wholesale":
                    qty = random.randint(15, 50)
                    price = round(unit_price * 0.85, 2) # 15% discount
                else:
                    price = unit_price
                    
                created_at = s_date.isoformat()
                sale_date_str = s_date.strftime("%Y-%m-%d")
                
                sales_records.append((sale_id, p_id, sale_date_str, qty, price, cust_type, created_at))
                
        cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?);", sales_records)
        print(f"Generated {len(sales_records)} sales records.")
        
        # 6. Generate Purchase Orders (100 POs)
        print("Generating purchase orders...")
        po_records = []
        # Get suppliers map by category to select supplier realistically
        suppliers_by_cat = {cat: [] for cat in categories}
        for s in suppliers:
            # Extract category name from rating/details or random
            for cat in categories:
                if cat in s[1]:
                    suppliers_by_cat[cat].append(s[0])
                    
        # Fallback if no matching supplier
        for cat in categories:
            if not suppliers_by_cat[cat]:
                suppliers_by_cat[cat] = [s[0] for s in suppliers]
                
        # Generate 100 POs distributed across the year
        po_statuses = ["Received", "Received", "Received", "Sent", "Pending", "Cancelled"]
        
        for i in range(100):
            po_id = str(uuid.uuid4())
            p_id = random.choice(product_ids)
            p_cost = [p[4] for p in products if p[0] == p_id][0]
            p_cat = [p[3] for p in products if p[0] == p_id][0]
            
            s_id = random.choice(suppliers_by_cat[p_cat])
            qty = random.randint(50, 200)
            
            # Purchase date
            po_offset = random.randint(10, 350)
            o_date = start_date + timedelta(days=po_offset)
            order_date_str = o_date.strftime("%Y-%m-%d")
            
            status = random.choice(po_statuses)
            # If PO is from the recent month, it might be Sent or Pending, otherwise Received
            days_ago = (datetime.now() - o_date).days
            if days_ago > 30 and status in ["Sent", "Pending"]:
                status = "Received"
                
            lead_time = [s[5] for s in suppliers if s[0] == s_id][0]
            
            expected_delivery = (o_date + timedelta(days=lead_time)).strftime("%Y-%m-%d")
            
            if status == "Received":
                actual_delivery = (o_date + timedelta(days=lead_time + random.randint(-2, 2))).strftime("%Y-%m-%d")
            elif status == "Cancelled":
                actual_delivery = None
            else:
                actual_delivery = None
                
            notes = f"Auto-generated replenishment PO. Lead time: {lead_time} days."
            created_at = o_date.isoformat()
            
            po_records.append((po_id, s_id, p_id, qty, p_cost, order_date_str, expected_delivery, actual_delivery, status, notes, created_at))
            
        cursor.executemany("INSERT INTO purchase_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", po_records)
        print(f"Generated {len(po_records)} purchase orders.")
        
        # 7. Generate initial Audit Logs (10+ logs)
        print("Generating audit logs...")
        audit_logs = []
        user_ids = [u[0] for u in users]
        entities = ["products", "suppliers", "inventory", "users"]
        actions = ["CREATE", "UPDATE"]
        
        for i in range(15):
            log_id = str(uuid.uuid4())
            u_id = random.choice(user_ids)
            action = random.choice(actions)
            entity = random.choice(entities)
            entity_id = str(uuid.uuid4())
            old_value = None if action == "CREATE" else '{"status": "old_value"}'
            new_value = '{"status": "new_value"}'
            ip_address = f"192.168.1.{random.randint(10, 100)}"
            timestamp = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            
            audit_logs.append((log_id, u_id, action, entity, entity_id, old_value, new_value, ip_address, timestamp))
            
        cursor.executemany("INSERT INTO audit_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", audit_logs)
        
        conn.commit()
        print("Database successfully seeded with clean enterprise data!")
        
    except Exception as e:
        conn.rollback()
        print(f"Seeding failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
