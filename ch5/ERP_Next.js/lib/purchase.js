import { db, nextDocNo } from './db';
import { getItem, receiveInventory } from './inventory';

const APPROVAL_THRESHOLD = 100000;

// ---------- Suppliers ----------
export function listSuppliers({ activeOnly = false } = {}) {
  const where = activeOnly ? 'WHERE is_active = 1' : '';
  return db.prepare(`SELECT * FROM suppliers ${where} ORDER BY supplier_code`).all();
}

export function getSupplier(id) {
  return db.prepare('SELECT * FROM suppliers WHERE id = ?').get(id);
}

export function createSupplier(data) {
  if (!data.supplierCode || !data.supplierName) throw new Error('Supplier code and name are required');
  const result = db
    .prepare(
      `INSERT INTO suppliers (supplier_code, supplier_name, payment_terms, credit_limit, contact_person, email, rating)
       VALUES (?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      data.supplierCode,
      data.supplierName,
      data.paymentTerms || null,
      data.creditLimit || 0,
      data.contactPerson || null,
      data.email || null,
      data.rating || 0
    );
  return result.lastInsertRowid;
}

export function updateSupplier(id, data) {
  const supplier = getSupplier(id);
  if (!supplier) throw new Error('Supplier not found');
  db.prepare(
    `UPDATE suppliers SET supplier_name = ?, payment_terms = ?, credit_limit = ?, contact_person = ?,
       email = ?, rating = ?, is_active = ? WHERE id = ?`
  ).run(
    data.supplierName ?? supplier.supplier_name,
    data.paymentTerms ?? supplier.payment_terms,
    data.creditLimit ?? supplier.credit_limit,
    data.contactPerson ?? supplier.contact_person,
    data.email ?? supplier.email,
    data.rating ?? supplier.rating,
    data.isActive !== undefined ? (data.isActive ? 1 : 0) : supplier.is_active,
    id
  );
}

// ---------- Purchase requisitions ----------
export function createPurchaseRequisition({ requesterId, department, requiredDate, budgetCode, reason, lines }) {
  if (!lines?.length) throw new Error('At least one line item is required');
  for (const line of lines) {
    if (!getItem(line.itemId)) throw new Error(`Item #${line.itemId} not found`);
    if (!(line.quantity > 0)) throw new Error('Line quantity must be greater than zero');
  }

  const txn = db.transaction(() => {
    const prId = db
      .prepare(
        `INSERT INTO purchase_requisitions (pr_no, requester_id, department, required_date, budget_code, reason)
         VALUES (?, ?, ?, ?, ?, ?)`
      )
      .run(nextDocNo('PR'), requesterId, department || null, requiredDate || null, budgetCode || null, reason || null)
      .lastInsertRowid;

    const insertLine = db.prepare(
      'INSERT INTO pr_lines (pr_id, item_id, quantity, warehouse_id) VALUES (?, ?, ?, ?)'
    );
    for (const line of lines) insertLine.run(prId, line.itemId, line.quantity, line.warehouseId || null);
    return prId;
  });
  return txn();
}

export function approvePurchaseRequisition(prId, approverId) {
  const pr = db.prepare('SELECT * FROM purchase_requisitions WHERE id = ?').get(prId);
  if (!pr) throw new Error('Purchase requisition not found');
  if (pr.status !== 'draft') throw new Error('Only draft requisitions can be approved');
  db.prepare('UPDATE purchase_requisitions SET status = ? WHERE id = ?').run('approved', prId);
  return approverId;
}

export function listPurchaseRequisitions() {
  return db
    .prepare(
      `SELECT pr.*, u.full_name AS requester_name FROM purchase_requisitions pr
       JOIN users u ON u.id = pr.requester_id ORDER BY pr.created_at DESC`
    )
    .all();
}

export function getPurchaseRequisition(id) {
  const pr = db.prepare('SELECT * FROM purchase_requisitions WHERE id = ?').get(id);
  if (!pr) return null;
  const lines = db
    .prepare(
      `SELECT prl.*, i.item_code, i.item_name FROM pr_lines prl
       JOIN items i ON i.id = prl.item_id WHERE prl.pr_id = ?`
    )
    .all(id);
  return { ...pr, lines };
}

// ---------- RFQ / quotations ----------
export function createRFQ({ prId, quoteDueDate }) {
  const result = db
    .prepare('INSERT INTO rfqs (rfq_no, pr_id, quote_due_date) VALUES (?, ?, ?)')
    .run(nextDocNo('RFQ'), prId || null, quoteDueDate || null);
  return result.lastInsertRowid;
}

export function sendRFQ({ rfqId, supplierIds }) {
  const insert = db.prepare('INSERT INTO rfq_suppliers (rfq_id, supplier_id, status) VALUES (?, ?, ?)');
  const txn = db.transaction(() => {
    for (const supplierId of supplierIds) insert.run(rfqId, supplierId, 'sent');
  });
  txn();
}

// Records a supplier's quoted price for one line item of the RFQ.
export function recordQuotation({ rfqId, supplierId, itemId, unitPrice, leadTimeDays, paymentTerms, warranty, freightCost }) {
  db.prepare(
    `INSERT INTO quotations (rfq_id, supplier_id, item_id, unit_price, lead_time_days, payment_terms, warranty, freight_cost)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
  ).run(rfqId, supplierId, itemId, unitPrice, leadTimeDays || 0, paymentTerms || null, warranty || null, freightCost || 0);
  db.prepare(`UPDATE rfq_suppliers SET status = 'responded' WHERE rfq_id = ? AND supplier_id = ?`).run(rfqId, supplierId);
}

export function compareQuotations(rfqId) {
  const rows = db
    .prepare(
      `SELECT q.*, s.supplier_name, s.rating FROM quotations q
       JOIN suppliers s ON s.id = q.supplier_id WHERE q.rfq_id = ?`
    )
    .all(rfqId);

  const bySupplier = new Map();
  for (const row of rows) {
    if (!bySupplier.has(row.supplier_id)) {
      bySupplier.set(row.supplier_id, {
        supplierId: row.supplier_id,
        supplierName: row.supplier_name,
        rating: row.rating,
        totalCost: 0,
        avgLeadTime: 0,
        lines: [],
      });
    }
    const entry = bySupplier.get(row.supplier_id);
    entry.totalCost += row.unit_price + row.freight_cost;
    entry.lines.push(row);
  }
  const results = [...bySupplier.values()].map((e) => ({
    ...e,
    avgLeadTime: e.lines.reduce((s, l) => s + l.lead_time_days, 0) / e.lines.length,
  }));
  results.sort((a, b) => a.totalCost - b.totalCost);
  return results;
}

export function recommendSupplier(rfqId) {
  const ranked = compareQuotations(rfqId);
  return ranked[0] || null;
}

export function listRFQs() {
  return db.prepare('SELECT * FROM rfqs ORDER BY created_at DESC').all();
}

export function getRFQ(id) {
  const rfq = db.prepare('SELECT * FROM rfqs WHERE id = ?').get(id);
  if (!rfq) return null;
  const suppliers = db
    .prepare(
      `SELECT rs.*, s.supplier_name FROM rfq_suppliers rs
       JOIN suppliers s ON s.id = rs.supplier_id WHERE rs.rfq_id = ?`
    )
    .all(id);
  return { ...rfq, suppliers, comparison: compareQuotations(id) };
}

// ---------- Purchase orders ----------
function computePoTotal(lines) {
  return lines.reduce((sum, l) => sum + l.quantity * l.unitPrice * (1 - (l.discount || 0) / 100), 0);
}

export function createPurchaseOrder({ supplierId, prId, requiredDate, buyerId, paymentTerms, shippingAddress, lines }) {
  const supplier = getSupplier(supplierId);
  if (!supplier || !supplier.is_active) throw new Error('Supplier is invalid or inactive');
  if (!lines?.length) throw new Error('At least one line item is required');

  const total = computePoTotal(lines);
  const txn = db.transaction(() => {
    const poId = db
      .prepare(
        `INSERT INTO purchase_orders
          (po_no, supplier_id, pr_id, required_date, buyer_id, payment_terms, shipping_address, total_amount)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
      )
      .run(nextDocNo('PO'), supplierId, prId || null, requiredDate || null, buyerId || null, paymentTerms || null, shippingAddress || null, total)
      .lastInsertRowid;

    const insertLine = db.prepare(
      `INSERT INTO po_lines (po_id, item_id, description, quantity, unit_price, discount, warehouse_id)
       VALUES (?, ?, ?, ?, ?, ?, ?)`
    );
    for (const line of lines) {
      if (!getItem(line.itemId)) throw new Error(`Item #${line.itemId} not found`);
      insertLine.run(poId, line.itemId, line.description || null, line.quantity, line.unitPrice, line.discount || 0, line.warehouseId || null);
    }
    return poId;
  });
  return txn();
}

export function updatePurchaseOrder(id, { requiredDate, paymentTerms, shippingAddress, lines }) {
  const po = getPurchaseOrder(id);
  if (!po) throw new Error('Purchase order not found');
  if (po.status !== 'draft') throw new Error('Only draft purchase orders can be modified');

  const txn = db.transaction(() => {
    if (lines?.length) {
      db.prepare('DELETE FROM po_lines WHERE po_id = ?').run(id);
      const insertLine = db.prepare(
        `INSERT INTO po_lines (po_id, item_id, description, quantity, unit_price, discount, warehouse_id)
         VALUES (?, ?, ?, ?, ?, ?, ?)`
      );
      for (const line of lines) {
        insertLine.run(id, line.itemId, line.description || null, line.quantity, line.unitPrice, line.discount || 0, line.warehouseId || null);
      }
      db.prepare('UPDATE purchase_orders SET total_amount = ? WHERE id = ?').run(computePoTotal(lines), id);
    }
    db.prepare(
      'UPDATE purchase_orders SET required_date = ?, payment_terms = ?, shipping_address = ? WHERE id = ?'
    ).run(requiredDate ?? po.required_date, paymentTerms ?? po.payment_terms, shippingAddress ?? po.shipping_address, id);
  });
  txn();
}

export function submitPurchaseOrder(id) {
  const po = getPurchaseOrder(id);
  if (!po) throw new Error('Purchase order not found');
  if (po.status !== 'draft') throw new Error('Only draft purchase orders can be submitted');
  db.prepare('UPDATE purchase_orders SET status = ? WHERE id = ?').run('submitted', id);
}

export function approvePurchaseOrder(id, approverId) {
  const po = getPurchaseOrder(id);
  if (!po) throw new Error('Purchase order not found');
  if (po.status !== 'submitted') throw new Error('Only submitted purchase orders can be approved');
  if (po.total_amount > APPROVAL_THRESHOLD && !approverId) {
    throw new Error('Purchase orders above the approval threshold require a manager approver');
  }
  db.prepare('UPDATE purchase_orders SET status = ? WHERE id = ?').run('approved', id);
}

export function sendPurchaseOrder(id) {
  const po = getPurchaseOrder(id);
  if (!po) throw new Error('Purchase order not found');
  if (po.status !== 'approved') throw new Error('Only approved purchase orders can be sent');
  db.prepare(`UPDATE purchase_orders SET status = 'sent', sent_at = datetime('now') WHERE id = ?`).run(id);
}

export function trackPurchaseOrder(id) {
  const po = getPurchaseOrder(id);
  if (!po) return null;
  const receipts = db
    .prepare('SELECT * FROM goods_receipts WHERE po_id = ? ORDER BY received_date')
    .all(id);
  const invoices = db.prepare('SELECT * FROM supplier_invoices WHERE po_id = ?').all(id);
  return { ...po, receipts, invoices };
}

export function cancelPurchaseOrder(id) {
  const po = getPurchaseOrder(id);
  if (!po) throw new Error('Purchase order not found');
  if (!['draft', 'submitted', 'approved'].includes(po.status)) {
    throw new Error('Only draft, submitted, or approved purchase orders can be cancelled');
  }
  db.prepare('UPDATE purchase_orders SET status = ? WHERE id = ?').run('cancelled', id);
}

export function closePurchaseOrder(id) {
  const po = getPurchaseOrder(id);
  if (!po) throw new Error('Purchase order not found');
  const fullyReceived = po.lines.every((l) => l.received_qty >= l.quantity);
  const invoiced = db.prepare(`SELECT COUNT(*) AS n FROM supplier_invoices WHERE po_id = ? AND status != 'paid'`).get(id).n === 0;
  if (!fullyReceived) throw new Error('Cannot close: not all lines fully received');
  if (!invoiced) throw new Error('Cannot close: outstanding supplier invoices remain');
  db.prepare('UPDATE purchase_orders SET status = ? WHERE id = ?').run('closed', id);
}

export function listPurchaseOrders() {
  return db
    .prepare(
      `SELECT po.*, s.supplier_name FROM purchase_orders po
       JOIN suppliers s ON s.id = po.supplier_id ORDER BY po.created_at DESC`
    )
    .all();
}

export function getPurchaseOrder(id) {
  const po = db.prepare('SELECT * FROM purchase_orders WHERE id = ?').get(id);
  if (!po) return null;
  const supplier = getSupplier(po.supplier_id);
  const lines = db
    .prepare(
      `SELECT pol.*, i.item_code, i.item_name, i.uom FROM po_lines pol
       JOIN items i ON i.id = pol.item_id WHERE pol.po_id = ?`
    )
    .all(id);
  return { ...po, supplier, lines };
}

export function searchPurchaseOrders({ poNo, supplierId, buyerId, status, dateFrom, dateTo } = {}) {
  const conditions = [];
  const args = [];
  if (poNo) {
    conditions.push('po.po_no LIKE ?');
    args.push(`%${poNo}%`);
  }
  if (supplierId) {
    conditions.push('po.supplier_id = ?');
    args.push(supplierId);
  }
  if (buyerId) {
    conditions.push('po.buyer_id = ?');
    args.push(buyerId);
  }
  if (status) {
    conditions.push('po.status = ?');
    args.push(status);
  }
  if (dateFrom) {
    conditions.push('po.order_date >= ?');
    args.push(dateFrom);
  }
  if (dateTo) {
    conditions.push('po.order_date <= ?');
    args.push(dateTo);
  }
  const where = conditions.length ? `WHERE ${conditions.join(' AND ')}` : '';
  return db
    .prepare(
      `SELECT po.*, s.supplier_name FROM purchase_orders po
       JOIN suppliers s ON s.id = po.supplier_id ${where}
       ORDER BY po.created_at DESC`
    )
    .all(...args);
}

// ---------- Goods receipt / quality / returns ----------
// Handles both full and partial receipts: a receipt whose line quantities
// don't cover the remaining ordered quantity simply leaves the PO "partially_received".
export function receiveGoods({ poId, warehouseId, receivedBy, lines }) {
  const po = getPurchaseOrder(poId);
  if (!po) throw new Error('Purchase order not found');
  if (!['approved', 'sent', 'partially_received'].includes(po.status)) {
    throw new Error('Purchase order is not in a receivable state');
  }

  const txn = db.transaction(() => {
    const grnId = db
      .prepare('INSERT INTO goods_receipts (grn_no, po_id, warehouse_id, received_by) VALUES (?, ?, ?, ?)')
      .run(nextDocNo('GRN'), poId, warehouseId, receivedBy || null).lastInsertRowid;

    const insertLine = db.prepare(
      `INSERT INTO grn_lines (grn_id, po_line_id, item_id, received_qty, inspection_result)
       VALUES (?, ?, ?, ?, 'pending')`
    );
    for (const line of lines) {
      const poLine = po.lines.find((l) => l.id === line.poLineId);
      if (!poLine) throw new Error(`PO line #${line.poLineId} not found`);
      const remaining = poLine.quantity - poLine.received_qty;
      if (line.receivedQty > remaining) {
        throw new Error(`Received quantity exceeds remaining ordered quantity for ${poLine.item_code}`);
      }
      insertLine.run(grnId, line.poLineId, poLine.item_id, line.receivedQty);
      db.prepare('UPDATE po_lines SET received_qty = received_qty + ? WHERE id = ?').run(line.receivedQty, line.poLineId);
    }

    const updatedLines = db.prepare('SELECT * FROM po_lines WHERE po_id = ?').all(poId);
    const fullyReceived = updatedLines.every((l) => l.received_qty >= l.quantity);
    db.prepare('UPDATE purchase_orders SET status = ? WHERE id = ?').run(
      fullyReceived ? 'received' : 'partially_received',
      poId
    );
    return grnId;
  });
  return txn();
}

export function listGoodsReceipts() {
  return db
    .prepare(
      `SELECT gr.*, po.po_no FROM goods_receipts gr JOIN purchase_orders po ON po.id = gr.po_id
       ORDER BY gr.received_date DESC`
    )
    .all();
}

export function getGoodsReceipt(id) {
  const grn = db.prepare('SELECT * FROM goods_receipts WHERE id = ?').get(id);
  if (!grn) return null;
  const lines = db
    .prepare(
      `SELECT gl.*, i.item_code, i.item_name, pol.unit_price FROM grn_lines gl
       JOIN items i ON i.id = gl.item_id
       JOIN po_lines pol ON pol.id = gl.po_line_id
       WHERE gl.grn_id = ?`
    )
    .all(id);
  return { ...grn, lines };
}

export function qualityInspection({ grnLineId, result, inspectedBy }) {
  const line = db
    .prepare(
      `SELECT gl.*, g.warehouse_id, pol.unit_price FROM grn_lines gl
       JOIN goods_receipts g ON g.id = gl.grn_id
       JOIN po_lines pol ON pol.id = gl.po_line_id
       WHERE gl.id = ?`
    )
    .get(grnLineId);
  if (!line) throw new Error('Goods receipt line not found');
  if (line.inspection_result !== 'pending') throw new Error('This line has already been inspected');

  const txn = db.transaction(() => {
    db.prepare('UPDATE grn_lines SET inspection_result = ? WHERE id = ?').run(result, grnLineId);
    if (result === 'pass') {
      receiveInventory({
        itemId: line.item_id,
        warehouseId: line.warehouse_id,
        quantity: line.received_qty,
        unitCost: line.unit_price,
        referenceDoc: `GRN-line-${grnLineId}`,
        userId: inspectedBy,
      });
    }
  });
  txn();
}

export function returnToSupplier({ grnLineId, quantity, reason }) {
  const result = db
    .prepare('INSERT INTO supplier_returns (return_no, grn_line_id, quantity, reason) VALUES (?, ?, ?, ?)')
    .run(nextDocNo('RTN'), grnLineId, quantity, reason);
  return result.lastInsertRowid;
}

// ---------- Three-way match / invoices / payments ----------
export function threeWayMatch({ poId, grnId, invoiceId }) {
  const po = getPurchaseOrder(poId);
  const grn = getGoodsReceipt(grnId);
  const invoice = db.prepare('SELECT * FROM supplier_invoices WHERE id = ?').get(invoiceId);
  if (!po || !grn || !invoice) throw new Error('Purchase order, receipt, or invoice not found');

  const receivedValue = grn.lines.reduce((sum, l) => sum + l.received_qty * l.unit_price, 0);
  const tolerance = 0.01;
  const supplierMatches = po.supplier_id === invoice.supplier_id;
  const amountMatches = Math.abs(receivedValue - invoice.amount) <= receivedValue * tolerance;

  return {
    matched: supplierMatches && amountMatches,
    supplierMatches,
    amountMatches,
    receivedValue,
    invoiceAmount: invoice.amount,
  };
}

export function processSupplierInvoice({ poId, invoiceNo, invoiceDate, amount, paymentTerms }) {
  const po = getPurchaseOrder(poId);
  if (!po) throw new Error('Purchase order not found');

  const txn = db.transaction(() => {
    const invoiceId = db
      .prepare(
        `INSERT INTO supplier_invoices (invoice_no, po_id, supplier_id, invoice_date, amount, payment_terms)
         VALUES (?, ?, ?, ?, ?, ?)`
      )
      .run(invoiceNo, poId, po.supplier_id, invoiceDate, amount, paymentTerms || po.payment_terms).lastInsertRowid;

    const latestGrn = db
      .prepare('SELECT id FROM goods_receipts WHERE po_id = ? ORDER BY id DESC LIMIT 1')
      .get(poId);
    if (latestGrn) {
      const match = threeWayMatch({ poId, grnId: latestGrn.id, invoiceId });
      db.prepare('UPDATE supplier_invoices SET matched = ?, status = ? WHERE id = ?').run(
        match.matched ? 1 : 0,
        match.matched ? 'matched' : 'exception',
        invoiceId
      );
    }
    return invoiceId;
  });
  return txn();
}

export function schedulePayment({ invoiceId, dueDate, amount }) {
  const invoice = db.prepare('SELECT * FROM supplier_invoices WHERE id = ?').get(invoiceId);
  if (!invoice) throw new Error('Supplier invoice not found');
  if (invoice.status !== 'matched') throw new Error('Invoice must pass three-way match before payment can be scheduled');

  const txn = db.transaction(() => {
    db.prepare('INSERT INTO ap_payments (invoice_id, due_date, amount) VALUES (?, ?, ?)').run(
      invoiceId,
      dueDate,
      amount
    );
    db.prepare(`UPDATE supplier_invoices SET status = 'scheduled' WHERE id = ?`).run(invoiceId);
  });
  txn();
}

export function listSupplierInvoices() {
  return db
    .prepare(
      `SELECT si.*, po.po_no, s.supplier_name FROM supplier_invoices si
       JOIN purchase_orders po ON po.id = si.po_id
       JOIN suppliers s ON s.id = si.supplier_id
       ORDER BY si.created_at DESC`
    )
    .all();
}

// ---------- Supplier scorecard / dashboard ----------
export function generateSupplierScorecard(supplierId) {
  const pos = db.prepare(`SELECT * FROM purchase_orders WHERE supplier_id = ?`).all(supplierId);
  const grnLines = db
    .prepare(
      `SELECT gl.* FROM grn_lines gl
       JOIN goods_receipts g ON g.id = gl.grn_id
       JOIN purchase_orders po ON po.id = g.po_id
       WHERE po.supplier_id = ?`
    )
    .all(supplierId);
  const returns = db
    .prepare(
      `SELECT sr.* FROM supplier_returns sr
       JOIN grn_lines gl ON gl.id = sr.grn_line_id
       JOIN goods_receipts g ON g.id = gl.grn_id
       JOIN purchase_orders po ON po.id = g.po_id
       WHERE po.supplier_id = ?`
    )
    .all(supplierId);

  const inspected = grnLines.filter((l) => l.inspection_result !== 'pending');
  const passed = grnLines.filter((l) => l.inspection_result === 'pass');
  const totalSpend = pos.reduce((s, po) => s + po.total_amount, 0);

  return {
    supplierId,
    totalPurchaseOrders: pos.length,
    totalSpend,
    qualityPassRate: inspected.length ? passed.length / inspected.length : null,
    returnRate: grnLines.length ? returns.length / grnLines.length : 0,
  };
}

export function getProcurementDashboard() {
  const openPRs = db.prepare(`SELECT COUNT(*) AS n FROM purchase_requisitions WHERE status = 'draft'`).get().n;
  const openRFQs = db.prepare(`SELECT COUNT(*) AS n FROM rfqs WHERE status = 'open'`).get().n;
  const posByStatus = db
    .prepare('SELECT status, COUNT(*) AS n, SUM(total_amount) AS total FROM purchase_orders GROUP BY status')
    .all();
  const pendingInvoices = db
    .prepare(`SELECT COUNT(*) AS n FROM supplier_invoices WHERE status IN ('pending', 'exception')`)
    .get().n;
  const topSuppliers = db
    .prepare(
      `SELECT s.supplier_name, SUM(po.total_amount) AS total_spend
       FROM purchase_orders po JOIN suppliers s ON s.id = po.supplier_id
       GROUP BY s.id ORDER BY total_spend DESC LIMIT 5`
    )
    .all();

  return { openPRs, openRFQs, posByStatus, pendingInvoices, topSuppliers };
}
