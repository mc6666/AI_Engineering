import { listFunctions } from '@/lib/rbac';
import { createRoleAction } from '@/app/actions/rbac';
import FunctionCheckboxes from '@/app/components/FunctionCheckboxes';

export default async function NewRolePage({ searchParams }) {
  const { error } = await searchParams;
  const functions = listFunctions();

  return (
    <div className="py-4" style={{ maxWidth: 640 }}>
      <h2>新增角色</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={createRoleAction}>
        <div className="mb-3">
          <label className="form-label">角色名稱</label>
          <input type="text" name="name" className="form-control" required />
        </div>
        <div className="mb-3">
          <label className="form-label">說明</label>
          <input type="text" name="description" className="form-control" />
        </div>
        <label className="form-label">功能權限</label>
        <FunctionCheckboxes functions={functions} />
        <button type="submit" className="btn btn-primary">
          新增
        </button>
      </form>
    </div>
  );
}
