import Link from 'next/link';
import { logoutAction } from '@/app/actions/auth';

export default function Topbar({ user, otherAreaHref, otherAreaLabel }) {
  return (
    <nav className="app-header navbar navbar-expand bg-body">
      <div className="container-fluid">
        <ul className="navbar-nav">
          <li className="nav-item">
            <a className="nav-link" data-lte-toggle="sidebar" href="#" role="button">
              <i className="bi bi-list" />
            </a>
          </li>
        </ul>
        <ul className="navbar-nav ms-auto align-items-center">
          {otherAreaHref && (
            <li className="nav-item">
              <Link href={otherAreaHref} className="nav-link">
                {otherAreaLabel}
              </Link>
            </li>
          )}
          <li className="nav-item">
            <span className="nav-link disabled">{user.full_name}</span>
          </li>
          <li className="nav-item">
            <Link href="/change-password" className="nav-link">
              變更密碼
            </Link>
          </li>
          <li className="nav-item">
            <form action={logoutAction}>
              <button type="submit" className="btn btn-link nav-link border-0">
                登出
              </button>
            </form>
          </li>
        </ul>
      </div>
    </nav>
  );
}
