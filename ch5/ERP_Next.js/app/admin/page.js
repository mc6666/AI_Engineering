import Link from 'next/link';

export default function AdminHome() {
  return (
    <div className="py-4">
      <h2>後台管理</h2>
      <p className="text-muted">管理使用者、角色與功能權限。</p>
      <div className="row mt-4">
        <div className="col-md-4">
          <Link href="/admin/users" className="card text-decoration-none mb-3">
            <div className="card-body">
              <h5 className="card-title">使用者管理</h5>
            </div>
          </Link>
        </div>
        <div className="col-md-4">
          <Link href="/admin/roles" className="card text-decoration-none mb-3">
            <div className="card-body">
              <h5 className="card-title">角色管理</h5>
            </div>
          </Link>
        </div>
        <div className="col-md-4">
          <Link href="/admin/functions" className="card text-decoration-none mb-3">
            <div className="card-body">
              <h5 className="card-title">功能權限管理</h5>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
