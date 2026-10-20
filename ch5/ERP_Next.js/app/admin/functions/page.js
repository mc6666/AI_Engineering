import { listFunctions } from '@/lib/rbac';

export default async function FunctionsPage() {
  const functions = listFunctions();

  return (
    <div className="py-4">
      <h2>功能權限管理</h2>
      <p className="text-muted">
        功能清單來自前台／後台的選單設定（JSON 檔），新增功能請調整選單設定。
      </p>
      <table className="table table-striped table-bordered">
        <thead>
          <tr>
            <th>模組</th>
            <th>代碼</th>
            <th>名稱</th>
          </tr>
        </thead>
        <tbody>
          {functions.map((fn) => (
            <tr key={fn.id}>
              <td>{fn.module}</td>
              <td>
                <code>{fn.code}</code>
              </td>
              <td>{fn.name}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
