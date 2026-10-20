-- ============ AUTH / RBAC ============
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  full_name TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS roles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL,
  description TEXT
);

-- functions = permission nodes; mirrors the sidebar tree (module/menu items)
CREATE TABLE IF NOT EXISTS functions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  module TEXT NOT NULL, -- inventory | purchase | sales | admin
  parent_code TEXT
);

CREATE TABLE IF NOT EXISTS user_roles (
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS role_functions (
  role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  function_id INTEGER NOT NULL REFERENCES functions(id) ON DELETE CASCADE,
  PRIMARY KEY (role_id, function_id)
);

-- ============ INVENTORY ============
CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_code TEXT UNIQUE NOT NULL,
  item_name TEXT NOT NULL,
  category TEXT,
  uom TEXT NOT NULL DEFAULT 'EA',
  barcode TEXT,
  lot_managed INTEGER NOT NULL DEFAULT 0,
  serial_managed INTEGER NOT NULL DEFAULT 0,
  costing_method TEXT NOT NULL DEFAULT 'weighted_average', -- fifo | lifo | weighted_average | standard | moving_average
  standard_cost REAL NOT NULL DEFAULT 0,
  average_cost REAL NOT NULL DEFAULT 0,
  reorder_point REAL NOT NULL DEFAULT 0,
  safety_stock REAL NOT NULL DEFAULT 0,
  lead_time_days INTEGER NOT NULL DEFAULT 0,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS warehouses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  warehouse_code TEXT UNIQUE NOT NULL,
  warehouse_name TEXT NOT NULL,
  location TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bins (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
  bin_code TEXT NOT NULL,
  zone TEXT,
  UNIQUE(warehouse_id, bin_code)
);

-- one row per item/warehouse/lot/serial combination
CREATE TABLE IF NOT EXISTS stock (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id INTEGER NOT NULL REFERENCES items(id),
  warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
  bin_id INTEGER REFERENCES bins(id),
  lot_number TEXT,
  serial_number TEXT,
  expiration_date TEXT,
  qty_on_hand REAL NOT NULL DEFAULT 0,
  qty_reserved REAL NOT NULL DEFAULT 0,
  unit_cost REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'available' -- available | damaged | quarantined | expired
);

CREATE TABLE IF NOT EXISTS inventory_transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  txn_no TEXT UNIQUE NOT NULL,
  txn_type TEXT NOT NULL, -- receipt | issue | transfer_out | transfer_in | adjustment | reservation | release
  item_id INTEGER NOT NULL REFERENCES items(id),
  warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
  lot_number TEXT,
  serial_number TEXT,
  quantity REAL NOT NULL,
  unit_cost REAL NOT NULL DEFAULT 0,
  txn_date TEXT NOT NULL DEFAULT (datetime('now')),
  reference_doc TEXT,
  user_id INTEGER REFERENCES users(id),
  notes TEXT
);

CREATE TABLE IF NOT EXISTS cycle_counts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  count_no TEXT UNIQUE NOT NULL,
  warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
  method TEXT NOT NULL DEFAULT 'random', -- abc | random | high_value | expiring
  status TEXT NOT NULL DEFAULT 'open', -- open | approved | closed
  counted_by INTEGER REFERENCES users(id),
  approved_by INTEGER REFERENCES users(id),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS cycle_count_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cycle_count_id INTEGER NOT NULL REFERENCES cycle_counts(id) ON DELETE CASCADE,
  item_id INTEGER NOT NULL REFERENCES items(id),
  stock_id INTEGER REFERENCES stock(id),
  system_qty REAL NOT NULL,
  counted_qty REAL,
  variance REAL
);

CREATE TABLE IF NOT EXISTS physical_inventories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  count_no TEXT UNIQUE NOT NULL,
  warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
  status TEXT NOT NULL DEFAULT 'frozen', -- frozen | approved | completed
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS physical_inventory_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  physical_inventory_id INTEGER NOT NULL REFERENCES physical_inventories(id) ON DELETE CASCADE,
  item_id INTEGER NOT NULL REFERENCES items(id),
  stock_id INTEGER REFERENCES stock(id),
  system_qty REAL NOT NULL,
  counted_qty REAL,
  variance REAL
);

-- ============ PURCHASE ORDER ============
CREATE TABLE IF NOT EXISTS suppliers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  supplier_code TEXT UNIQUE NOT NULL,
  supplier_name TEXT NOT NULL,
  payment_terms TEXT,
  credit_limit REAL NOT NULL DEFAULT 0,
  contact_person TEXT,
  email TEXT,
  rating REAL NOT NULL DEFAULT 0,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS purchase_requisitions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pr_no TEXT UNIQUE NOT NULL,
  requester_id INTEGER NOT NULL REFERENCES users(id),
  department TEXT,
  required_date TEXT,
  budget_code TEXT,
  reason TEXT,
  status TEXT NOT NULL DEFAULT 'draft', -- draft | approved | rejected
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pr_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pr_id INTEGER NOT NULL REFERENCES purchase_requisitions(id) ON DELETE CASCADE,
  item_id INTEGER NOT NULL REFERENCES items(id),
  quantity REAL NOT NULL,
  warehouse_id INTEGER REFERENCES warehouses(id)
);

CREATE TABLE IF NOT EXISTS rfqs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rfq_no TEXT UNIQUE NOT NULL,
  pr_id INTEGER REFERENCES purchase_requisitions(id),
  quote_due_date TEXT,
  status TEXT NOT NULL DEFAULT 'open', -- open | closed
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS rfq_suppliers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rfq_id INTEGER NOT NULL REFERENCES rfqs(id) ON DELETE CASCADE,
  supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
  status TEXT NOT NULL DEFAULT 'sent' -- sent | responded
);

CREATE TABLE IF NOT EXISTS quotations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  rfq_id INTEGER NOT NULL REFERENCES rfqs(id) ON DELETE CASCADE,
  supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
  item_id INTEGER NOT NULL REFERENCES items(id),
  unit_price REAL NOT NULL,
  lead_time_days INTEGER NOT NULL DEFAULT 0,
  payment_terms TEXT,
  warranty TEXT,
  freight_cost REAL NOT NULL DEFAULT 0,
  submitted_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS purchase_orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  po_no TEXT UNIQUE NOT NULL,
  supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
  pr_id INTEGER REFERENCES purchase_requisitions(id),
  order_date TEXT NOT NULL DEFAULT (datetime('now')),
  required_date TEXT,
  status TEXT NOT NULL DEFAULT 'draft',
  -- draft | submitted | approved | sent | partially_received | received | invoiced | closed | cancelled
  total_amount REAL NOT NULL DEFAULT 0,
  buyer_id INTEGER REFERENCES users(id),
  payment_terms TEXT,
  shipping_address TEXT,
  sent_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS po_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  po_id INTEGER NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
  item_id INTEGER NOT NULL REFERENCES items(id),
  description TEXT,
  quantity REAL NOT NULL,
  unit_price REAL NOT NULL,
  discount REAL NOT NULL DEFAULT 0,
  warehouse_id INTEGER REFERENCES warehouses(id),
  received_qty REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS goods_receipts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  grn_no TEXT UNIQUE NOT NULL,
  po_id INTEGER NOT NULL REFERENCES purchase_orders(id),
  warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
  received_date TEXT NOT NULL DEFAULT (datetime('now')),
  received_by INTEGER REFERENCES users(id),
  status TEXT NOT NULL DEFAULT 'pending_inspection' -- pending_inspection | passed | failed
);

CREATE TABLE IF NOT EXISTS grn_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  grn_id INTEGER NOT NULL REFERENCES goods_receipts(id) ON DELETE CASCADE,
  po_line_id INTEGER NOT NULL REFERENCES po_lines(id),
  item_id INTEGER NOT NULL REFERENCES items(id),
  received_qty REAL NOT NULL,
  inspection_result TEXT -- pending | pass | fail | return
);

CREATE TABLE IF NOT EXISTS supplier_returns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  return_no TEXT UNIQUE NOT NULL,
  grn_line_id INTEGER NOT NULL REFERENCES grn_lines(id),
  quantity REAL NOT NULL,
  reason TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'authorized',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS supplier_invoices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invoice_no TEXT UNIQUE NOT NULL,
  po_id INTEGER NOT NULL REFERENCES purchase_orders(id),
  supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
  invoice_date TEXT NOT NULL,
  amount REAL NOT NULL,
  payment_terms TEXT,
  matched INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending', -- pending | matched | exception | scheduled | paid
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ap_payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invoice_id INTEGER NOT NULL REFERENCES supplier_invoices(id),
  due_date TEXT NOT NULL,
  amount REAL NOT NULL,
  status TEXT NOT NULL DEFAULT 'scheduled', -- scheduled | paid
  paid_at TEXT
);

-- ============ SALES ORDER ============
CREATE TABLE IF NOT EXISTS customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_code TEXT UNIQUE NOT NULL,
  customer_name TEXT NOT NULL,
  credit_limit REAL NOT NULL DEFAULT 0,
  ar_balance REAL NOT NULL DEFAULT 0,
  payment_terms TEXT,
  shipping_address TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sales_orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  so_no TEXT UNIQUE NOT NULL,
  order_date TEXT NOT NULL DEFAULT (datetime('now')),
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  status TEXT NOT NULL DEFAULT 'draft',
  -- draft | open | approved | picking | packed | shipped | invoiced | closed | cancelled
  total_amount REAL NOT NULL DEFAULT 0,
  discount REAL NOT NULL DEFAULT 0,
  freight REAL NOT NULL DEFAULT 0,
  salesperson_id INTEGER REFERENCES users(id),
  required_date TEXT,
  shipping_address TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS so_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  so_id INTEGER NOT NULL REFERENCES sales_orders(id) ON DELETE CASCADE,
  item_id INTEGER NOT NULL REFERENCES items(id),
  description TEXT,
  quantity REAL NOT NULL,
  unit_price REAL NOT NULL,
  discount REAL NOT NULL DEFAULT 0,
  warehouse_id INTEGER REFERENCES warehouses(id),
  shipped_qty REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS shipments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  shipment_no TEXT UNIQUE NOT NULL,
  so_id INTEGER NOT NULL REFERENCES sales_orders(id),
  tracking_no TEXT,
  carrier TEXT,
  ship_date TEXT,
  status TEXT NOT NULL DEFAULT 'shipped',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ar_invoices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invoice_no TEXT UNIQUE NOT NULL,
  so_id INTEGER NOT NULL REFERENCES sales_orders(id),
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  invoice_date TEXT NOT NULL DEFAULT (datetime('now')),
  amount REAL NOT NULL,
  vat_amount REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'open', -- open | paid
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ar_receipts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invoice_id INTEGER NOT NULL REFERENCES ar_invoices(id),
  received_date TEXT NOT NULL DEFAULT (datetime('now')),
  amount REAL NOT NULL
);
