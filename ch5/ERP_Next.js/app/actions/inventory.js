'use server';

import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import { requirePermission } from '@/lib/auth';
import {
  createItem,
  updateItem,
  createWarehouse,
  updateWarehouse,
  receiveInventory,
  issueInventory,
  transferInventory,
  adjustInventory,
  performCycleCount,
  approveCycleCount,
  performPhysicalCount,
  completePhysicalCount,
  generateBarcode,
} from '@/lib/inventory';

function num(formData, key) {
  const v = formData.get(key);
  return v === null || v === '' ? undefined : Number(v);
}

export async function createItemAction(formData) {
  await requirePermission('inventory.items');
  try {
    createItem({
      itemCode: formData.get('itemCode'),
      itemName: formData.get('itemName'),
      category: formData.get('category') || null,
      uom: formData.get('uom') || 'EA',
      costingMethod: formData.get('costingMethod'),
      lotManaged: formData.get('lotManaged') === 'on',
      serialManaged: formData.get('serialManaged') === 'on',
      standardCost: num(formData, 'standardCost') || 0,
      reorderPoint: num(formData, 'reorderPoint') || 0,
      safetyStock: num(formData, 'safetyStock') || 0,
      leadTimeDays: num(formData, 'leadTimeDays') || 0,
    });
  } catch (err) {
    redirect(`/portal/inventory/items/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/inventory/items');
  redirect('/portal/inventory/items');
}

export async function updateItemAction(formData) {
  await requirePermission('inventory.items');
  const id = Number(formData.get('id'));
  try {
    updateItem(id, {
      itemName: formData.get('itemName'),
      category: formData.get('category') || null,
      uom: formData.get('uom'),
      costingMethod: formData.get('costingMethod'),
      lotManaged: formData.get('lotManaged') === 'on',
      serialManaged: formData.get('serialManaged') === 'on',
      standardCost: num(formData, 'standardCost'),
      reorderPoint: num(formData, 'reorderPoint'),
      safetyStock: num(formData, 'safetyStock'),
      leadTimeDays: num(formData, 'leadTimeDays'),
      isActive: formData.get('isActive') === 'on',
    });
  } catch (err) {
    redirect(`/portal/inventory/items/${id}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/inventory/items');
  redirect(`/portal/inventory/items/${id}`);
}

export async function generateBarcodeAction(formData) {
  await requirePermission('inventory.items');
  const id = Number(formData.get('id'));
  generateBarcode(id);
  revalidatePath(`/portal/inventory/items/${id}`);
  redirect(`/portal/inventory/items/${id}`);
}

export async function createWarehouseAction(formData) {
  await requirePermission('inventory.warehouses');
  try {
    createWarehouse({
      warehouseCode: formData.get('warehouseCode'),
      warehouseName: formData.get('warehouseName'),
      location: formData.get('location') || null,
    });
  } catch (err) {
    redirect(`/portal/inventory/warehouses/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/inventory/warehouses');
  redirect('/portal/inventory/warehouses');
}

export async function updateWarehouseAction(formData) {
  await requirePermission('inventory.warehouses');
  const id = Number(formData.get('id'));
  try {
    updateWarehouse(id, {
      warehouseName: formData.get('warehouseName'),
      location: formData.get('location') || null,
      isActive: formData.get('isActive') === 'on',
    });
  } catch (err) {
    redirect(`/portal/inventory/warehouses/${id}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/inventory/warehouses');
  redirect('/portal/inventory/warehouses');
}

export async function receiveInventoryAction(formData) {
  const user = await requirePermission('inventory.receipts');
  try {
    receiveInventory({
      itemId: num(formData, 'itemId'),
      warehouseId: num(formData, 'warehouseId'),
      lotNumber: formData.get('lotNumber') || null,
      serialNumber: formData.get('serialNumber') || null,
      expirationDate: formData.get('expirationDate') || null,
      quantity: num(formData, 'quantity'),
      unitCost: num(formData, 'unitCost') || 0,
      referenceDoc: formData.get('referenceDoc') || null,
      userId: user.id,
    });
  } catch (err) {
    redirect(`/portal/inventory/receipts/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/inventory/receipts');
  redirect('/portal/inventory/receipts');
}

export async function issueInventoryAction(formData) {
  const user = await requirePermission('inventory.issues');
  try {
    issueInventory({
      itemId: num(formData, 'itemId'),
      warehouseId: num(formData, 'warehouseId'),
      quantity: num(formData, 'quantity'),
      referenceDoc: formData.get('referenceDoc') || null,
      notes: formData.get('notes') || null,
      userId: user.id,
    });
  } catch (err) {
    redirect(`/portal/inventory/issues/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/inventory/issues');
  redirect('/portal/inventory/issues');
}

export async function transferInventoryAction(formData) {
  const user = await requirePermission('inventory.transfers');
  try {
    transferInventory({
      itemId: num(formData, 'itemId'),
      fromWarehouseId: num(formData, 'fromWarehouseId'),
      toWarehouseId: num(formData, 'toWarehouseId'),
      quantity: num(formData, 'quantity'),
      referenceDoc: formData.get('referenceDoc') || null,
      userId: user.id,
    });
  } catch (err) {
    redirect(`/portal/inventory/transfers/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/inventory/transfers');
  redirect('/portal/inventory/transfers');
}

export async function adjustInventoryAction(formData) {
  const user = await requirePermission('inventory.adjustments');
  try {
    adjustInventory({
      itemId: num(formData, 'itemId'),
      warehouseId: num(formData, 'warehouseId'),
      quantityDelta: num(formData, 'quantityDelta'),
      reason: formData.get('reason'),
      approvedBy: user.id,
      userId: user.id,
    });
  } catch (err) {
    redirect(`/portal/inventory/adjustments/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/inventory/adjustments');
  redirect('/portal/inventory/adjustments');
}

export async function performCycleCountAction(formData) {
  const user = await requirePermission('inventory.cycle_counts');
  const warehouseId = num(formData, 'warehouseId');
  const stockIds = formData.getAll('stockId').map(Number);
  const countedQtys = formData.getAll('countedQty').map(Number);
  const lines = stockIds.map((stockId, i) => ({ stockId, countedQty: countedQtys[i] }));

  let id;
  try {
    id = performCycleCount({ warehouseId, method: formData.get('method'), countedBy: user.id, lines });
  } catch (err) {
    redirect(`/portal/inventory/cycle-counts/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/inventory/cycle-counts');
  redirect(`/portal/inventory/cycle-counts/${id}`);
}

export async function approveCycleCountAction(formData) {
  const user = await requirePermission('inventory.cycle_counts');
  const id = Number(formData.get('id'));
  approveCycleCount(id, user.id);
  revalidatePath(`/portal/inventory/cycle-counts/${id}`);
  redirect(`/portal/inventory/cycle-counts/${id}`);
}

export async function performPhysicalCountAction(formData) {
  await requirePermission('inventory.physical_counts');
  const warehouseId = num(formData, 'warehouseId');
  const stockIds = formData.getAll('stockId').map(Number);
  const countedQtys = formData.getAll('countedQty').map(Number);
  const lines = stockIds.map((stockId, i) => ({ stockId, countedQty: countedQtys[i] }));

  let id;
  try {
    id = performPhysicalCount({ warehouseId, lines });
  } catch (err) {
    redirect(`/portal/inventory/physical-counts/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/portal/inventory/physical-counts');
  redirect(`/portal/inventory/physical-counts/${id}`);
}

export async function completePhysicalCountAction(formData) {
  const user = await requirePermission('inventory.physical_counts');
  const id = Number(formData.get('id'));
  completePhysicalCount(id, user.id);
  revalidatePath(`/portal/inventory/physical-counts/${id}`);
  redirect(`/portal/inventory/physical-counts/${id}`);
}
