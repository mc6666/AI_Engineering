import Link from 'next/link';
import { listUsers } from '@/lib/rbac';
import { deleteUserAction } from '@/app/actions/rbac';

export default async function UsersPage() {
  const users = listUsers();

  return (
    <div className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2>使用者管理</h2>
        <Link href="/admin/users/new" className="btn btn-primary">
          新增使用者
        </Link>
      </div>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>使用者名稱</th>
            <th>姓名</th>
            <th>電子郵件</th>
            <th>角色</th>
            <th>狀態</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>
                <Link href={`/admin/users/${u.id}`}>{u.username}</Link>
              </td>
              <td>{u.full_name}</td>
              <td>{u.email}</td>
              <td>{u.role_names || '-'}</td>
              <td>{u.is_active ? '啟用' : '停用'}</td>
              <td>
                <form action={deleteUserAction}>
                  <input type="hidden" name="id" value={u.id} />
                  <button type="submit" className="btn btn-sm btn-danger">
                    刪除
                  </button>
                </form>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
