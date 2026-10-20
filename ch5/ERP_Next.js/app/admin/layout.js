import { redirect } from 'next/navigation';
import { getCurrentUser, hasAnyPermissionPrefix } from '@/lib/auth';
import { getAdminSidebar } from '@/lib/sidebar';
import BodyClass from '@/app/components/BodyClass';
import Sidebar from '@/app/components/Sidebar';
import Topbar from '@/app/components/Topbar';

export default async function AdminLayout({ children }) {
  const user = await getCurrentUser();
  if (!user) redirect('/login');
  if (!hasAnyPermissionPrefix(user, 'admin.')) redirect('/portal');

  const tree = getAdminSidebar(user);

  return (
    <>
      <BodyClass className="layout-fixed sidebar-expand-lg bg-body-tertiary" />
      <div className="app-wrapper">
        <Topbar user={user} otherAreaHref="/portal" otherAreaLabel="前台應用" />
        <Sidebar brand="ERP 後台" tree={tree} />
        <main className="app-main">
          <div className="app-content">
            <div className="container-fluid">{children}</div>
          </div>
        </main>
      </div>
    </>
  );
}
