function groupByModule(functions) {
  const groups = new Map();
  for (const fn of functions) {
    if (!groups.has(fn.module)) groups.set(fn.module, []);
    groups.get(fn.module).push(fn);
  }
  return [...groups.entries()];
}

export default function FunctionCheckboxes({ functions, selectedIds = [] }) {
  const groups = groupByModule(functions);
  return (
    <>
      {groups.map(([module, fns]) => (
        <div className="mb-3" key={module}>
          <div className="fw-bold text-uppercase text-muted mb-1">{module}</div>
          {fns.map((fn) => (
            <div className="form-check" key={fn.id}>
              <input
                type="checkbox"
                name="functionIds"
                value={fn.id}
                className="form-check-input"
                id={`fn-${fn.id}`}
                defaultChecked={selectedIds.includes(fn.id)}
              />
              <label className="form-check-label" htmlFor={`fn-${fn.id}`}>
                {fn.name} <code>{fn.code}</code>
              </label>
            </div>
          ))}
        </div>
      ))}
    </>
  );
}
