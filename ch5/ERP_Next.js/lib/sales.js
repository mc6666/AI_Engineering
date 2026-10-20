import { db, nextDocNo } from './db';
import { getItem, searchInventory, reserveInventory, releaseReservation, issueInventory } from './inventory';

const APPROVAL_THRESHOLD = 100000;
const VAT_RATE = 0.05;

// ---------- Customers ----------
export function listCustomers({ activeOnly = false } = {}) {
  const where = activeOnly ? 'WHERE is_active = 1' : '';
  return db.prepare(`SELECT * FROM customers ${where} ORDER BY customer_code`).all();
}

export function getCustomer(id) {
  return db.prepare('SELECT * FROM customers WHERE id = ?').get(id);
}

export function createCustomer(data) {
  if (!data.customerCode || !data.customerName) throw new Error('Customer code and name are required');
  const result = db
    .prepare(
      `INSERT INTO customers (customer_code, customer_name, credit_limit, payment_terms, shipping_address)
       VALUES (?, ?, ?, ?, ?)`
    )
    .run(data.customerCode, data.customerName, data.creditLimit || 0, data.paymentTerms || null, data.shippingAddress || null);
  return result.lastInsertRowid;
}

export function updateCustomer(id, data) {
  const customer = getCustomer(id);
  if (!customer) throw new Error('Customer not found');
  db.prepare(
    `UPDATE customers SET customer_name = ?, credit_limit = ?, payment_terms = ?, shipping_address = ?, is_active = ?
     WHERE id = ?`
  ).run(
    data.customerName ?? customer.customer_name,
    data.creditLimit ?? customer.credit_limit,
    data.paymentTerms ?? customer.payment_terms,
    data.shippingAddress ?? customer.shipping_address,
    data.isActive !== undefined ? (data.isActive ? 1 : 0) : customer.is_active,
    id
  );
}

export function getCustomerCredit(customerId) {
  const customer = getCustomer(customerId);
  if (!customer) throw new Error('Customer not found');
  const overdue = db
    .prepare(
      `SELECT COALESCE(SUM(amount), 0) AS total FROM ar_invoices
       WHERE customer_id = ? AND status = 'open' AND invoice_date <= date('now', '-30 day')`
    )
    .get(customerId).total;
  return {
    creditLimit: customer.credit_limit,
    arBalance: customer.ar_balance,
    availableCredit: customer.credit_limit - customer.ar_balance,
    overdue,
    frozen: customer.ar_balance >= customer.credit_limit,
  };
}

// ---------- Pricing / tax ----------
export function calculatePricing({ lines, discount = 0, freight = 0 }) {
  const subtotal = lines.reduce((sum, l) => sum + l.quantity * l.unitPrice * (1 - (l.discount || 0) / 100), 0);
  const totalAmount = subtotal - discount + freight;
  return { subtotal, discount, freight, totalAmount };
}

// VAT is included in the total amount (只在列印發票才需考慮), so this splits it
// out rather than adding it on top.
export function calculateTax(totalAmount) {
  const vatAmount = (totalAmount * VAT_RATE) / (1 + VAT_RATE);
  return { vatAmount, netAmount: totalAmount - vatAmount };
}

// ---------- Inventory check ----------
export function checkInventory({ itemId, warehouseId }) {
  const stockRows = searchInventory({ warehouseId }).filter((s) => s.item_id === itemId);
  const available = stockRows.reduce((sum, s) => sum + (s.qty_on_hand - s.qty_reserved), 0);
  const reserved = stockRows.reduce((sum, s) => sum + s.qty_reserved, 0);
  const onOrder = db
    .prepare(
      `SELECT COALESCE(SUM(pol.quantity - pol.received_qty), 0) AS qty, MIN(po.required_date) AS eta
       FROM po_lines pol JOIN purchase_orders po ON po.id = pol.po_id
       WHERE pol.item_id = ? AND pol.warehouse_id = ?
         AND po.status IN ('approved', 'sent', 'partially_received')`
    )
    .get(itemId, warehouseId);
  return { available, reserved, onOrder: onOrder.qty, expectedArrival: onOrder.eta };
}

// ---------- Sales orders ----------
export function createSalesOrder({ customerId, salespersonId, requiredDate, shippingAddress, lines }) {
  const customer = getCustomer(customerId);
  if (!customer || !customer.is_active) throw new Error('Customer is invalid or inactive');
  if (!lines?.length) throw new Error('At least one line item is required');
  for (const line of lines) {
    if (!getItem(line.itemId)) throw new Error(`Item #${line.itemId} not found`);
    if (!(line.quantity > 0)) throw new Error('Line quantity must be greater than zero');
  }

  const { totalAmount } = calculatePricing({ lines });
  const txn = db.transaction(() => {
    const soId = db
      .prepare(
        `INSERT INTO sales_orders (so_no, customer_id, salesperson_id, required_date, shipping_address, total_amount)
         VALUES (?, ?, ?, ?, ?, ?)`
      )
      .run(nextDocNo('SO'), customerId, salespersonId || null, requiredDate || null, shippingAddress || customer.shipping_address, totalAmount)
      .lastInsertRowid;

    const insertLine = db.prepare(
      `INSERT INTO so_lines (so_id, item_id, description, quantity, unit_price, discount, warehouse_id)
       VALUES (?, ?, ?, ?, ?, ?, ?)`
    );
    for (const line of lines) {
      insertLine.run(soId, line.itemId, line.description || null, line.quantity, line.unitPrice, line.discount || 0, line.warehouseId || null);
    }
    return soId;
  });
  return txn();
}

export function updateSalesOrder(id, { requiredDate, shippingAddress, lines }) {
  const so = getSalesOrder(id);
  if (!so) throw new Error('Sales order not found');
  if (so.status !== 'draft') throw new Error('Only draft sales orders can be modified');

  const txn = db.transaction(() => {
    if (lines?.length) {
      db.prepare('DELETE FROM so_lines WHERE so_id = ?').run(id);
      const insertLine = db.prepare(
        `INSERT INTO so_lines (so_id, item_id, description, quantity, unit_price, discount, warehouse_id)
         VALUES (?, ?, ?, ?, ?, ?, ?)`
      );
      for (const line of lines) {
        insertLine.run(id, line.itemId, line.description || null, line.quantity, line.unitPrice, line.discount || 0, line.warehouseId || null);
      }
      db.prepare('UPDATE sales_orders SET total_amount = ? WHERE id = ?').run(calculatePricing({ lines }).totalAmount, id);
    }
    db.prepare('UPDATE sales_orders SET required_date = ?, shipping_address = ? WHERE id = ?').run(
      requiredDate ?? so.required_date,
      shippingAddress ?? so.shipping_address,
      id
    );
  });
  txn();
}

export function deleteSalesOrder(id) {
  const so = getSalesOrder(id);
  if (!so) throw new Error('Sales order not found');
  if (so.status !== 'draft') throw new Error('Only draft sales orders can be deleted');
  db.prepare('DELETE FROM sales_orders WHERE id = ?').run(id);
}

export function submitOrder(id) {
  const so = getSalesOrder(id);
  if (!so) throw new Error('Sales order not found');
  if (so.status !== 'draft') throw new Error('Only draft sales orders can be submitted');

  const credit = getCustomerCredit(so.customer_id);
  if (so.total_amount > credit.availableCredit) {
    throw new Error('Order exceeds customer available credit');
  }
  for (const line of so.lines) {
    const inv = checkInventory({ itemId: line.item_id, warehouseId: line.warehouse_id });
    if (inv.available < line.quantity) {
      throw new Error(`Insufficient available inventory for ${line.item_code}: available ${inv.available}`);
    }
  }
  db.prepare(`UPDATE sales_orders SET status = 'open' WHERE id = ?`).run(id);
}

export function approveOrder(id, approverId) {
  const so = getSalesOrder(id);
  if (!so) throw new Error('Sales order not found');
  if (so.status !== 'open') throw new Error('Only open sales orders can be approved');
  if (so.total_amount > APPROVAL_THRESHOLD && !approverId) {
    throw new Error('Orders above the approval threshold require a manager approver');
  }

  const txn = db.transaction(() => {
    for (const line of so.lines) {
      reserveInventory({ itemId: line.item_id, warehouseId: line.warehouse_id, quantity: line.quantity, referenceDoc: so.so_no });
    }
    db.prepare(`UPDATE sales_orders SET status = 'approved' WHERE id = ?`).run(id);
  });
  txn();
}

export function cancelOrder(id) {
  const so = getSalesOrder(id);
  if (!so) throw new Error('Sales order not found');
  if (!['draft', 'open', 'approved'].includes(so.status)) {
    throw new Error('Only draft, open, or approved sales orders can be cancelled');
  }

  const txn = db.transaction(() => {
    if (so.status === 'approved') {
      for (const line of so.lines) {
        releaseReservation({ itemId: line.item_id, warehouseId: line.warehouse_id, quantity: line.quantity, referenceDoc: so.so_no });
      }
    }
    db.prepare(`UPDATE sales_orders SET status = 'cancelled' WHERE id = ?`).run(id);
  });
  txn();
}

export function closeOrder(id) {
  const so = getSalesOrder(id);
  if (!so) throw new Error('Sales order not found');
  const fullyShipped = so.lines.every((l) => l.shipped_qty >= l.quantity);
  const invoiced = db.prepare(`SELECT COUNT(*) AS n FROM ar_invoices WHERE so_id = ?`).get(id).n > 0;
  if (!fullyShipped) throw new Error('Cannot close: not all lines fully shipped');
  if (!invoiced) throw new Error('Cannot close: order has not been invoiced');
  db.prepare(`UPDATE sales_orders SET status = 'closed' WHERE id = ?`).run(id);
}

export function generatePickingList(soId) {
  const so = getSalesOrder(soId);
  if (!so) throw new Error('Sales order not found');
  return so.lines.map((l) => ({
    itemCode: l.item_code,
    itemName: l.item_name,
    warehouseId: l.warehouse_id,
    quantity: l.quantity - l.shipped_qty,
  }));
}

export function createShipment({ soId, trackingNo, carrier, shipDate, userId }) {
  const so = getSalesOrder(soId);
  if (!so) throw new Error('Sales order not found');
  if (!['approved', 'picking'].includes(so.status)) throw new Error('Sales order is not ready to ship');

  const txn = db.transaction(() => {
    const shipmentId = db
      .prepare('INSERT INTO shipments (shipment_no, so_id, tracking_no, carrier, ship_date) VALUES (?, ?, ?, ?, ?)')
      .run(nextDocNo('SHP'), soId, trackingNo || null, carrier || null, shipDate || null).lastInsertRowid;

    for (const line of so.lines) {
      const qty = line.quantity - line.shipped_qty;
      if (qty <= 0) continue;
      releaseReservation({ itemId: line.item_id, warehouseId: line.warehouse_id, quantity: qty, referenceDoc: so.so_no });
      issueInventory({ itemId: line.item_id, warehouseId: line.warehouse_id, quantity: qty, referenceDoc: so.so_no, userId, notes: 'Sales shipment' });
      db.prepare('UPDATE so_lines SET shipped_qty = shipped_qty + ? WHERE id = ?').run(qty, line.id);
    }
    db.prepare(`UPDATE sales_orders SET status = 'shipped' WHERE id = ?`).run(soId);
    return shipmentId;
  });
  return txn();
}

export function createInvoice({ soId }) {
  const so = getSalesOrder(soId);
  if (!so) throw new Error('Sales order not found');
  if (so.status !== 'shipped') throw new Error('Only shipped sales orders can be invoiced');

  const { vatAmount } = calculateTax(so.total_amount);
  const txn = db.transaction(() => {
    const invoiceId = db
      .prepare(
        `INSERT INTO ar_invoices (invoice_no, so_id, customer_id, amount, vat_amount) VALUES (?, ?, ?, ?, ?)`
      )
      .run(nextDocNo('INV'), soId, so.customer_id, so.total_amount, vatAmount).lastInsertRowid;
    db.prepare('UPDATE customers SET ar_balance = ar_balance + ? WHERE id = ?').run(so.total_amount, so.customer_id);
    db.prepare(`UPDATE sales_orders SET status = 'invoiced' WHERE id = ?`).run(soId);
    return invoiceId;
  });
  return txn();
}

export function recordReceipt({ invoiceId, amount }) {
  const invoice = db.prepare('SELECT * FROM ar_invoices WHERE id = ?').get(invoiceId);
  if (!invoice) throw new Error('Invoice not found');

  const txn = db.transaction(() => {
    db.prepare('INSERT INTO ar_receipts (invoice_id, amount) VALUES (?, ?)').run(invoiceId, amount);
    db.prepare('UPDATE customers SET ar_balance = ar_balance - ? WHERE id = ?').run(amount, invoice.customer_id);
    const totalReceived = db
      .prepare('SELECT COALESCE(SUM(amount), 0) AS total FROM ar_receipts WHERE invoice_id = ?')
      .get(invoiceId).total;
    if (totalReceived >= invoice.amount) {
      db.prepare(`UPDATE ar_invoices SET status = 'paid' WHERE id = ?`).run(invoiceId);
    }
  });
  txn();
}

export function duplicateOrder(id) {
  const so = getSalesOrder(id);
  if (!so) throw new Error('Sales order not found');
  return createSalesOrder({
    customerId: so.customer_id,
    salespersonId: so.salesperson_id,
    requiredDate: null,
    shippingAddress: so.shipping_address,
    lines: so.lines.map((l) => ({
      itemId: l.item_id,
      description: l.description,
      quantity: l.quantity,
      unitPrice: l.unit_price,
      discount: l.discount,
      warehouseId: l.warehouse_id,
    })),
  });
}

export function listSalesOrders() {
  return db
    .prepare(
      `SELECT so.*, c.customer_name FROM sales_orders so
       JOIN customers c ON c.id = so.customer_id ORDER BY so.created_at DESC`
    )
    .all();
}

export function getSalesOrder(id) {
  const so = db.prepare('SELECT * FROM sales_orders WHERE id = ?').get(id);
  if (!so) return null;
  const customer = getCustomer(so.customer_id);
  const lines = db
    .prepare(
      `SELECT sol.*, i.item_code, i.item_name, i.uom FROM so_lines sol
       JOIN items i ON i.id = sol.item_id WHERE sol.so_id = ?`
    )
    .all(id);
  return { ...so, customer, lines };
}

export function getOrderStatus(id) {
  const so = getSalesOrder(id);
  if (!so) return null;
  return {
    status: so.status,
    totalShippedQty: so.lines.reduce((s, l) => s + l.shipped_qty, 0),
    totalOrderedQty: so.lines.reduce((s, l) => s + l.quantity, 0),
  };
}

export function searchSalesOrders({ soNo, customerId, status, dateFrom, dateTo, salespersonId } = {}) {
  const conditions = [];
  const args = [];
  if (soNo) {
    conditions.push('so.so_no LIKE ?');
    args.push(`%${soNo}%`);
  }
  if (customerId) {
    conditions.push('so.customer_id = ?');
    args.push(customerId);
  }
  if (status) {
    conditions.push('so.status = ?');
    args.push(status);
  }
  if (salespersonId) {
    conditions.push('so.salesperson_id = ?');
    args.push(salespersonId);
  }
  if (dateFrom) {
    conditions.push('so.order_date >= ?');
    args.push(dateFrom);
  }
  if (dateTo) {
    conditions.push('so.order_date <= ?');
    args.push(dateTo);
  }
  const where = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';
  return db
    .prepare(
      `SELECT so.*, c.customer_name FROM sales_orders so
       JOIN customers c ON c.id = so.customer_id ${where}
       ORDER BY so.created_at DESC`
    )
    .all(...args);
}

export function exportSalesOrders(filter = {}) {
  const orders = searchSalesOrders(filter);
  const header = 'so_no,customer_name,order_date,status,total_amount';
  const rows = orders.map((o) => [o.so_no, o.customer_name, o.order_date, o.status, o.total_amount].join(','));
  return [header, ...rows].join('\n');
}

// Each CSV row creates one single-line draft sales order.
export function importSalesOrders(rows) {
  const results = [];
  for (const row of rows) {
    try {
      const customer = db.prepare('SELECT * FROM customers WHERE customer_code = ?').get(row.customerCode);
      if (!customer) throw new Error(`Unknown customer code ${row.customerCode}`);
      const item = db.prepare('SELECT * FROM items WHERE item_code = ?').get(row.itemCode);
      if (!item) throw new Error(`Unknown item code ${row.itemCode}`);
      const warehouse = db.prepare('SELECT * FROM warehouses WHERE warehouse_code = ?').get(row.warehouseCode);
      if (!warehouse) throw new Error(`Unknown warehouse code ${row.warehouseCode}`);

      const soId = createSalesOrder({
        customerId: customer.id,
        lines: [{ itemId: item.id, quantity: Number(row.quantity), unitPrice: Number(row.unitPrice), warehouseId: warehouse.id }],
      });
      results.push({ row, success: true, soId });
    } catch (err) {
      results.push({ row, success: false, error: err.message });
    }
  }
  return results;
}

export function listShipments() {
  return db
    .prepare(
      `SELECT sh.*, so.so_no, c.customer_name FROM shipments sh
       JOIN sales_orders so ON so.id = sh.so_id
       JOIN customers c ON c.id = so.customer_id
       ORDER BY sh.created_at DESC`
    )
    .all();
}

export function listArInvoices() {
  return db
    .prepare(
      `SELECT ai.*, so.so_no, c.customer_name,
              COALESCE((SELECT SUM(amount) FROM ar_receipts WHERE invoice_id = ai.id), 0) AS received
       FROM ar_invoices ai
       JOIN sales_orders so ON so.id = ai.so_id
       JOIN customers c ON c.id = ai.customer_id
       ORDER BY ai.created_at DESC`
    )
    .all();
}

// ---------- Dashboard ----------
export function getSalesDashboard() {
  const todayOrders = db.prepare(`SELECT COUNT(*) AS n FROM sales_orders WHERE date(order_date) = date('now')`).get().n;
  const monthSales = db
    .prepare(
      `SELECT COALESCE(SUM(total_amount), 0) AS total FROM sales_orders
       WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now') AND status != 'cancelled'`
    )
    .get().total;
  const pendingShipment = db
    .prepare(`SELECT COUNT(*) AS n FROM sales_orders WHERE status IN ('approved', 'picking')`)
    .get().n;
  const pendingInvoice = db.prepare(`SELECT COUNT(*) AS n FROM sales_orders WHERE status = 'shipped'`).get().n;
  const cancelledToday = db
    .prepare(`SELECT COUNT(*) AS n FROM sales_orders WHERE status = 'cancelled' AND date(order_date) = date('now')`)
    .get().n;
  const topCustomers = db
    .prepare(
      `SELECT c.customer_name, SUM(so.total_amount) AS total FROM sales_orders so
       JOIN customers c ON c.id = so.customer_id
       WHERE so.status != 'cancelled' GROUP BY c.id ORDER BY total DESC LIMIT 10`
    )
    .all();
  const topItems = db
    .prepare(
      `SELECT i.item_code, i.item_name, SUM(sol.quantity) AS qty FROM so_lines sol
       JOIN items i ON i.id = sol.item_id
       JOIN sales_orders so ON so.id = sol.so_id
       WHERE so.status != 'cancelled' GROUP BY i.id ORDER BY qty DESC LIMIT 10`
    )
    .all();
  const revenueAndAvg = db
    .prepare(`SELECT COALESCE(SUM(total_amount),0) AS revenue, COALESCE(AVG(total_amount),0) AS avg FROM sales_orders WHERE status != 'cancelled'`)
    .get();

  return {
    todayOrders,
    monthSales,
    pendingShipment,
    pendingInvoice,
    cancelledToday,
    topCustomers,
    topItems,
    totalRevenue: revenueAndAvg.revenue,
    avgOrderAmount: revenueAndAvg.avg,
  };
}
