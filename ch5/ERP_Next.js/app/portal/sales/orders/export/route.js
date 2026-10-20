import { requirePermission } from '@/lib/auth';
import { exportSalesOrders } from '@/lib/sales';

export async function GET() {
  try {
    await requirePermission('sales.orders');
  } catch {
    return new Response('Forbidden', { status: 403 });
  }

  const csv = exportSalesOrders();
  return new Response(csv, {
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'attachment; filename="sales_orders.csv"',
    },
  });
}
