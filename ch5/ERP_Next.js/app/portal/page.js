import Link from 'next/link';
import { getCurrentUser } from '@/lib/auth';

export default async function PortalHome() {
  const user = await getCurrentUser();

  return (
    <div className="py-4">
      <h2>歡迎，{user.full_name}</h2>
      <p className="text-muted">請由左側選單選擇欲使用的功能。</p>
      <div className="row mt-4">
        <div className="col-md-4">
          <Link href="/portal/inventory/dashboard" className="card text-decoration-none mb-3">
            <div className="card-body">
              <h5 className="card-title">庫存管理</h5>
              <p className="card-text text-muted">商品、倉庫、入出庫與盤點</p>
            </div>
          </Link>
        </div>
        <div className="col-md-4">
          <Link href="/portal/purchase/dashboard" className="card text-decoration-none mb-3">
            <div className="card-body">
              <h5 className="card-title">採購管理</h5>
              <p className="card-text text-muted">請購、詢價、採購訂單與收貨</p>
            </div>
          </Link>
        </div>
        <div className="col-md-4">
          <Link href="/portal/sales/dashboard" className="card text-decoration-none mb-3">
            <div className="card-body">
              <h5 className="card-title">銷售管理</h5>
              <p className="card-text text-muted">客戶、銷售訂單、出貨與發票</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
