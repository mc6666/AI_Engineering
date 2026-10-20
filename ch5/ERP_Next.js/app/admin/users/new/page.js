import { listRoles } from '@/lib/rbac';
import { createUserAction } from '@/app/actions/rbac';

export default async function NewUserPage({ searchParams }) {
  const { error } = await searchParams;
  const roles = listRoles();

  return (
    <div className="py-4" style={{ maxWidth: 560 }}>
      <h2>新增使用者</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={createUserAction}>
        <div className="mb-3">
          <label className="form-label">姓名</label>
          <input type="text" name="fullName" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">使用者名稱</label>
          <input type="text" name="username" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">電子郵件</label>
          <input type="email" name="email" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">初始密碼</label>
          <input type="password" name="password" className="form-control" required minLength={6} />
        </div>
        <div className="mb-3">
          <label className="form-label">角色</label>
          {roles.map((role) => (
            <div className="form-check" key={role.id}>
              <input
                type="checkbox"
                name="roleIds"
                value={role.id}
                className="form-check-input"
                id={`role-${role.id}`}
              />
              <label className="form-check-label" htmlFor={`role-${role.id}`}>
                {role.name}
              </label>
            </div>
          ))}
        </div>
        <button type="submit" className="btn btn-primary">
          新增
        </button>
      </form>
    </div>
  );
}
