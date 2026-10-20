import Link from 'next/link';

function SidebarGroup({ group }) {
  return (
    <li className="nav-item">
      <a href="#" className="nav-link">
        {group.icon && <i className={`nav-icon ${group.icon}`} />}
        <p>
          {group.label}
          <i className="nav-arrow bi bi-chevron-right" />
        </p>
      </a>
      <ul className="nav nav-treeview">
        {group.children.map((item) => (
          <li className="nav-item" key={item.code}>
            <Link href={item.path} className="nav-link">
              {item.icon && <i className={`nav-icon ${item.icon}`} />}
              <p>{item.label}</p>
            </Link>
          </li>
        ))}
      </ul>
    </li>
  );
}

export default function Sidebar({ brand, tree }) {
  return (
    <aside className="app-sidebar bg-body-secondary shadow" data-bs-theme="dark">
      <div className="sidebar-brand">
        <Link href="/portal" className="brand-link">
          <span className="brand-text fw-light">{brand}</span>
        </Link>
      </div>
      <div className="sidebar-wrapper">
        <nav className="mt-2">
          <ul
            className="nav sidebar-menu flex-column"
            data-lte-toggle="treeview"
            role="menu"
          >
            {tree.map((group) => (
              <SidebarGroup group={group} key={group.label} />
            ))}
          </ul>
        </nav>
      </div>
    </aside>
  );
}
