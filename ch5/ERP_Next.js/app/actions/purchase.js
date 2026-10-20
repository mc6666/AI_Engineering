'use server';

import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import { requirePermission } from '@/lib/auth';
import {
  createSupplier,
  updateSupplier,
  createPurchaseRequisition,
  approvePurchaseRequisition,
  createRFQ,
  sendRFQ,
  recordQuotation,
  createPurchaseOrder,
  updatePurchaseOrder,
  submitPurchaseOrder,
  approvePurchaseOrder,
  sendPurchaseOrder,
  cancelPurchaseOrder,
  closePurchaseOrder,
  receiveGoods,
  qualityInspection,
  returnToSupplier,
  processSupplierInvoice,
  schedulePayment,
} from '@/lib/purchase';

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

// ---------- Suppliers ----------
export async function createSupplierAction(formData) {
  await requirePermission('purchase.suppliers');
  try {
    createSupplier({
      supplierCode: formData.get('supplierCode'),
      supplierName: formData.get('supplierName'),
      paymentTerms: formData.get('paymentTerms') || null,
      creditLimit: num(formData, 'creditLimit') || 0,
      contactPerson: formData.get('contactPerson') || null,
      email: formData.get('email') || null,
      rating: num(formData, 'rating') || 0,
    });
  } catch (err) {
    redirect(`/portal/purchase/suppliers/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/purchase/suppliers');
  redirect('/portal/purchase/suppliers');
}

export async function updateSupplierAction(formData) {
  await requirePermission('purchase.suppliers');
  const id = Number(formData.get('id'));
  try {
    updateSupplier(id, {
      supplierName: formData.get('supplierName'),
      paymentTerms: formData.get('paymentTerms') || null,
      creditLimit: num(formData, 'creditLimit'),
      contactPerson: formData.get('contactPerson') || null,
      email: formData.get('email') || null,
      rating: num(formData, 'rating'),
      isActive: formData.get('isActive') === 'on',
    });
  } catch (err) {
    redirect(`/portal/purchase/suppliers/${id}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/purchase/suppliers');
  redirect(`/portal/purchase/suppliers/${id}`);
}

// ---------- Requisitions ----------
export async function createRequisitionAction(formData) {
  const user = await requirePermission('purchase.requisitions');
  const lines = parseLines(formData, ['itemId', 'quantity', 'warehouseId'])
    .filter((l) => Number(l.quantity) > 0)
    .map((l) => ({
      itemId: Number(l.itemId),
      quantity: Number(l.quantity),
      warehouseId: l.warehouseId ? Number(l.warehouseId) : null,
    }));
  try {
    createPurchaseRequisition({
      requesterId: user.id,
      department: formData.get('department') || null,
      requiredDate: formData.get('requiredDate') || null,
      budgetCode: formData.get('budgetCode') || null,
      reason: formData.get('reason') || null,
      lines,
    });
  } catch (err) {
    redirect(`/portal/purchase/requisitions/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/purchase/requisitions');
  redirect('/portal/purchase/requisitions');
}

export async function approveRequisitionAction(formData) {
  const user = await requirePermission('purchase.requisitions');
  const id = Number(formData.get('id'));
  approvePurchaseRequisition(id, user.id);
  revalidatePath(`/portal/purchase/requisitions/${id}`);
  redirect(`/portal/purchase/requisitions/${id}`);
}

// ---------- RFQ ----------
export async function createRFQAction(formData) {
  await requirePermission('purchase.rfq');
  let id;
  try {
    id = createRFQ({
      prId: num(formData, 'prId') || null,
      quoteDueDate: formData.get('quoteDueDate') || null,
    });
  } catch (err) {
    redirect(`/portal/purchase/rfq/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/purchase/rfq');
  redirect(`/portal/purchase/rfq/${id}`);
}

export async function sendRFQAction(formData) {
  await requirePermission('purchase.rfq');
  const rfqId = Number(formData.get('rfqId'));
  const supplierIds = formData.getAll('supplierIds').map(Number);
  sendRFQ({ rfqId, supplierIds });
  revalidatePath(`/portal/purchase/rfq/${rfqId}`);
  redirect(`/portal/purchase/rfq/${rfqId}`);
}

export async function recordQuotationAction(formData) {
  await requirePermission('purchase.rfq');
  const rfqId = Number(formData.get('rfqId'));
  recordQuotation({
    rfqId,
    supplierId: num(formData, 'supplierId'),
    itemId: num(formData, 'itemId'),
    unitPrice: num(formData, 'unitPrice'),
    leadTimeDays: num(formData, 'leadTimeDays') || 0,
    paymentTerms: formData.get('paymentTerms') || null,
    warranty: formData.get('warranty') || null,
    freightCost: num(formData, 'freightCost') || 0,
  });
  revalidatePath(`/portal/purchase/rfq/${rfqId}`);
  redirect(`/portal/purchase/rfq/${rfqId}`);
}

// ---------- Purchase orders ----------
export async function createPurchaseOrderAction(formData) {
  const user = await requirePermission('purchase.orders');
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
    id = createPurchaseOrder({
      supplierId: num(formData, 'supplierId'),
      prId: num(formData, 'prId') || null,
      requiredDate: formData.get('requiredDate') || null,
      buyerId: user.id,
      paymentTerms: formData.get('paymentTerms') || null,
      shippingAddress: formData.get('shippingAddress') || null,
      lines,
    });
  } catch (err) {
    redirect(`/portal/purchase/orders/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/purchase/orders');
  redirect(`/portal/purchase/orders/${id}`);
}

async function poWorkflowAction(formData, fn, extraArg) {
  await requirePermission('purchase.orders');
  const id = Number(formData.get('id'));
  try {
    extraArg ? fn(id, extraArg) : fn(id);
  } catch (err) {
    redirect(`/portal/purchase/orders/${id}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath(`/portal/purchase/orders/${id}`);
  redirect(`/portal/purchase/orders/${id}`);
}

export async function submitPurchaseOrderAction(formData) {
  return poWorkflowAction(formData, submitPurchaseOrder);
}

export async function approvePurchaseOrderAction(formData) {
  const user = await requirePermission('purchase.orders');
  const id = Number(formData.get('id'));
  try {
    approvePurchaseOrder(id, user.id);
  } catch (err) {
    redirect(`/portal/purchase/orders/${id}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath(`/portal/purchase/orders/${id}`);
  redirect(`/portal/purchase/orders/${id}`);
}

export async function sendPurchaseOrderAction(formData) {
  return poWorkflowAction(formData, sendPurchaseOrder);
}

export async function cancelPurchaseOrderAction(formData) {
  return poWorkflowAction(formData, cancelPurchaseOrder);
}

export async function closePurchaseOrderAction(formData) {
  return poWorkflowAction(formData, closePurchaseOrder);
}

// ---------- Goods receipt / quality / returns ----------
export async function receiveGoodsAction(formData) {
  const user = await requirePermission('purchase.receipts');
  const poId = Number(formData.get('poId'));
  const lines = parseLines(formData, ['poLineId', 'receivedQty'])
    .filter((l) => Number(l.receivedQty) > 0)
    .map((l) => ({ poLineId: Number(l.poLineId), receivedQty: Number(l.receivedQty) }));

  try {
    receiveGoods({
      poId,
      warehouseId: num(formData, 'warehouseId'),
      receivedBy: user.id,
      lines,
    });
  } catch (err) {
    redirect(`/portal/purchase/receipts/new?poId=${poId}&error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/purchase/receipts');
  redirect('/portal/purchase/receipts');
}

export async function qualityInspectionAction(formData) {
  const user = await requirePermission('purchase.receipts');
  const grnId = Number(formData.get('grnId'));
  const grnLineId = Number(formData.get('grnLineId'));
  qualityInspection({ grnLineId, result: formData.get('result'), inspectedBy: user.id });
  revalidatePath(`/portal/purchase/receipts/${grnId}`);
  redirect(`/portal/purchase/receipts/${grnId}`);
}

export async function returnToSupplierAction(formData) {
  await requirePermission('purchase.receipts');
  const grnId = Number(formData.get('grnId'));
  returnToSupplier({
    grnLineId: Number(formData.get('grnLineId')),
    quantity: num(formData, 'quantity'),
    reason: formData.get('reason'),
  });
  revalidatePath(`/portal/purchase/receipts/${grnId}`);
  redirect(`/portal/purchase/receipts/${grnId}`);
}

// ---------- Invoices / payments ----------
export async function processSupplierInvoiceAction(formData) {
  await requirePermission('purchase.invoices');
  try {
    processSupplierInvoice({
      poId: num(formData, 'poId'),
      invoiceNo: formData.get('invoiceNo'),
      invoiceDate: formData.get('invoiceDate'),
      amount: num(formData, 'amount'),
      paymentTerms: formData.get('paymentTerms') || null,
    });
  } catch (err) {
    redirect(`/portal/purchase/invoices/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/purchase/invoices');
  redirect('/portal/purchase/invoices');
}

export async function schedulePaymentAction(formData) {
  await requirePermission('purchase.invoices');
  const invoiceId = Number(formData.get('invoiceId'));
  try {
    schedulePayment({ invoiceId, dueDate: formData.get('dueDate'), amount: num(formData, 'amount') });
  } catch (err) {
    redirect(`/portal/purchase/invoices?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/purchase/invoices');
  redirect('/portal/purchase/invoices');
}
