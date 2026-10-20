import { notFound } from 'next/navigation';
import { getUser, listRoles } from '@/lib/rbac';
import { updateUserAction } from '@/app/actions/rbac';

export default async function EditUserPage({ params, searchParams }) {
  const { id } = await params;
  const { error } = await searchParams;
  const user = getUser(Number(id));
  if (!user) notFound();
  const roles = listRoles();

  return (
    <div className="py-4" style={{ maxWidth: 560 }}>
      <h2>編輯使用者：{user.username}</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={updateUserAction}>
        <input type="hidden" name="id" value={user.id} />
        <div className="mb-3">
          <label className="form-label">姓名</label>
          <input
            type="text"
            name="fullName"
            className="form-control"
            defaultValue={user.full_name}
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">電子郵件</label>
          <input
            type="email"
            name="email"
            className="form-control"
            defaultValue={user.email}
            required
          />
        </div>
        <div className="form-check mb-3">
          <input
            type="checkbox"
            name="isActive"
            className="form-check-input"
            id="isActive"
            defaultChecked={Boolean(user.is_active)}
          />
          <label className="form-check-label" htmlFor="isActive">
            啟用
          </label>
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
                defaultChecked={user.roleIds.includes(role.id)}
              />
              <label className="form-check-label" htmlFor={`role-${role.id}`}>
                {role.name}
              </label>
            </div>
          ))}
        </div>
        <button type="submit" className="btn btn-primary">
          儲存
        </button>
      </form>
    </div>
  );
}
