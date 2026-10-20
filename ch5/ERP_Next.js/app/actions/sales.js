'use server';

import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import { requirePermission } from '@/lib/auth';
import {
  createCustomer,
  updateCustomer,
  createSalesOrder,
  submitOrder,
  approveOrder,
  cancelOrder,
  closeOrder,
  createShipment,
  createInvoice,
  recordReceipt,
  duplicateOrder,
  importSalesOrders,
} from '@/lib/sales';

function num(formData, key) {
  const v = formData.get(key);
  return v === null || v === '' ? undefined : Number(v);
}

function parseLines(formData, fields) {
  const counts = formData.getAll(fields[0]).length;
  const lines = [];
  for (let i = 0; i < counts; i++) {
    const line = {};
    for (const f of fields) line[f] = formData.getAll(f)[i];
    lines.push(line);
  }
  return lines;
}

// ---------- Customers ----------
export async function createCustomerAction(formData) {
  await requirePermission('sales.customers');
  try {
    createCustomer({
      customerCode: formData.get('customerCode'),
      customerName: formData.get('customerName'),
      creditLimit: num(formData, 'creditLimit') || 0,
      paymentTerms: formData.get('paymentTerms') || null,
      shippingAddress: formData.get('shippingAddress') || null,
    });
  } catch (err) {
    redirect(`/portal/sales/customers/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/sales/customers');
  redirect('/portal/sales/customers');
}

export async function updateCustomerAction(formData) {
  await requirePermission('sales.customers');
  const id = Number(formData.get('id'));
  try {
    updateCustomer(id, {
      customerName: formData.get('customerName'),
      creditLimit: num(formData, 'creditLimit'),
      paymentTerms: formData.get('paymentTerms') || null,
      shippingAddress: formData.get('shippingAddress') || null,
      isActive: formData.get('isActive') === 'on',
    });
  } catch (err) {
    redirect(`/portal/sales/customers/${id}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/sales/customers');
  redirect(`/portal/sales/customers/${id}`);
}

// ---------- Sales orders ----------
export async function createSalesOrderAction(formData) {
  const user = await requirePermission('sales.orders');
  const lines = parseLines(formData, ['itemId', 'description', 'quantity', 'unitPrice', 'discount', 'warehouseId'])
    .filter((l) => Number(l.quantity) > 0)
    .map((l) => ({
      itemId: Number(l.itemId),
      description: l.description,
      quantity: Number(l.quantity),
      unitPrice: Number(l.unitPrice),
      discount: Number(l.discount || 0),
      warehouseId: l.warehouseId ? Number(l.warehouseId) : null,
    }));

  let id;
  try {
    id = createSalesOrder({
      customerId: num(formData, 'customerId'),
      salespersonId: user.id,
      requiredDate: formData.get('requiredDate') || null,
      shippingAddress: formData.get('shippingAddress') || null,
      lines,
    });
  } catch (err) {
    redirect(`/portal/sales/orders/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/sales/orders');
  redirect(`/portal/sales/orders/${id}`);
}

async function soWorkflowAction(formData, fn) {
  await requirePermission('sales.orders');
  const id = Number(formData.get('id'));
  try {
    fn(id);
  } catch (err) {
    redirect(`/portal/sales/orders/${id}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath(`/portal/sales/orders/${id}`);
  redirect(`/portal/sales/orders/${id}`);
}

export async function submitOrderAction(formData) {
  return soWorkflowAction(formData, submitOrder);
}

export async function approveOrderAction(formData) {
  const user = await requirePermission('sales.orders');
  const id = Number(formData.get('id'));
  try {
    approveOrder(id, user.id);
  } catch (err) {
    redirect(`/portal/sales/orders/${id}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath(`/portal/sales/orders/${id}`);
  redirect(`/portal/sales/orders/${id}`);
}

export async function cancelOrderAction(formData) {
  return soWorkflowAction(formData, cancelOrder);
}

export async function closeOrderAction(formData) {
  return soWorkflowAction(formData, closeOrder);
}

export async function duplicateOrderAction(formData) {
  await requirePermission('sales.orders');
  const id = Number(formData.get('id'));
  const newId = duplicateOrder(id);
  revalidatePath('/portal/sales/orders');
  redirect(`/portal/sales/orders/${newId}`);
}

// ---------- Shipments / invoices / receipts ----------
export async function createShipmentAction(formData) {
  const user = await requirePermission('sales.shipments');
  const soId = Number(formData.get('soId'));
  try {
    createShipment({
      soId,
      trackingNo: formData.get('trackingNo') || null,
      carrier: formData.get('carrier') || null,
      shipDate: formData.get('shipDate') || null,
      userId: user.id,
    });
  } catch (err) {
    redirect(`/portal/sales/orders/${soId}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath(`/portal/sales/orders/${soId}`);
  redirect(`/portal/sales/orders/${soId}`);
}

export async function createInvoiceAction(formData) {
  await requirePermission('sales.invoices');
  const soId = Number(formData.get('soId'));
  try {
    createInvoice({ soId });
  } catch (err) {
    redirect(`/portal/sales/orders/${soId}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath(`/portal/sales/orders/${soId}`);
  redirect('/portal/sales/invoices');
}

export async function recordReceiptAction(formData) {
  await requirePermission('sales.invoices');
  const invoiceId = Number(formData.get('invoiceId'));
  recordReceipt({ invoiceId, amount: num(formData, 'amount') });
  revalidatePath('/portal/sales/invoices');
  redirect('/portal/sales/invoices');
}

// ---------- Import ----------
export async function importSalesOrdersAction(formData) {
  await requirePermission('sales.orders');
  const csv = String(formData.get('csv') || '').trim();
  const lines = csv.split('\n').map((l) => l.trim()).filter(Boolean);
  const [, ...dataLines] = lines; // first line is the header
  const rows = dataLines.map((line) => {
    const [customerCode, itemCode, quantity, unitPrice, warehouseCode] = line.split(',').map((s) => s.trim());
    return { customerCode, itemCode, quantity, unitPrice, warehouseCode };
  });
  const results = importSalesOrders(rows);
  const summary = results.map((r) => (r.success ? `OK: ${r.row.customerCode}/${r.row.itemCode}` : `FAIL: ${r.error}`)).join('; ');
  revalidatePath('/portal/sales/orders');
  redirect(`/portal/sales/orders?message=${encodeURIComponent(summary)}`);
}
