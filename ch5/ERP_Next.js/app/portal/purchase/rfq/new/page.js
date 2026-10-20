import { createRFQAction } from '@/app/actions/purchase';

export default async function NewRFQPage({ searchParams }) {
  const { error, prId } = await searchParams;

  return (
    <div className="py-4" style={{ maxWidth: 480 }}>
      <h2>新增詢價單</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      <form action={createRFQAction}>
        {prId && <input type="hidden" name="prId" value={prId} />}
        <div className="mb-3">
          <label className="form-label">報價截止日</label>
          <input type="date" name="quoteDueDate" className="form-control" />
        </div>
        <button type="submit" className="btn btn-primary">
          建立
        </button>
      </form>
    </div>
  );
}
