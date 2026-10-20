import { redirect } from 'next/navigation';
import { getCurrentUser, hasAnyPermissionPrefix } from '@/lib/auth';
import { getPortalSidebar } from '@/lib/sidebar';
import BodyClass from '@/app/components/BodyClass';
import Sidebar from '@/app/components/Sidebar';
import Topbar from '@/app/components/Topbar';

export default async function PortalLayout({ children }) {
  const user = await getCurrentUser();
  if (!user) redirect('/login');

  const tree = getPortalSidebar(user);
  const canSeeAdmin = hasAnyPermissionPrefix(user, 'admin.');

  return (
    <>
      <BodyClass className="layout-fixed sidebar-expand-lg bg-body-tertiary" />
      <div className="app-wrapper">
        <Topbar
          user={user}
          otherAreaHref={canSeeAdmin ? '/admin' : null}
          otherAreaLabel="後台管理"
        />
        <Sidebar brand="ERP 前台" tree={tree} />
        <main className="app-main">
          <div className="app-content">
            <div className="container-fluid">{children}</div>
          </div>
        </main>
      </div>
    </>
  );
}
