import { notFound } from 'next/navigation';
import { getRole, listFunctions } from '@/lib/rbac';
import { updateRoleAction } from '@/app/actions/rbac';
import FunctionCheckboxes from '@/app/components/FunctionCheckboxes';

export default async function EditRolePage({ params, searchParams }) {
  const { id } = await params;
  const { error } = await searchParams;
  const role = getRole(Number(id));
  if (!role) notFound();
  const functions = listFunctions();

  return (
    <div className="py-4" style={{ maxWidth: 640 }}>
      <h2>編輯角色：{role.name}</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={updateRoleAction}>
        <input type="hidden" name="id" value={role.id} />
        <div className="mb-3">
          <label className="form-label">角色名稱</label>
          <input
            type="text"
            name="name"
            className="form-control"
            defaultValue={role.name}
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">說明</label>
          <input
            type="text"
            name="description"
            className="form-control"
            defaultValue={role.description || ''}
          />
        </div>
        <label className="form-label">功能權限</label>
        <FunctionCheckboxes functions={functions} selectedIds={role.functionIds} />
        <button type="submit" className="btn btn-primary">
          儲存
        </button>
      </form>
    </div>
  );
}
