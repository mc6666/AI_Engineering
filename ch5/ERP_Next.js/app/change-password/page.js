import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';
import { changePasswordAction } from '@/app/actions/auth';
import BodyClass from '@/app/components/BodyClass';
import Topbar from '@/app/components/Topbar';

export const metadata = { title: 'Change Password - ERP System' };

export default async function ChangePasswordPage({ searchParams }) {
  const user = await getCurrentUser();
  if (!user) redirect('/login');
  const { error } = await searchParams;

  return (
    <>
      <BodyClass className="layout-fixed bg-body-tertiary" />
      <div className="app-wrapper">
        <Topbar user={user} />
        <main className="app-main">
          <div className="app-content">
            <div className="container-fluid" style={{ maxWidth: 480 }}>
              <div className="card mt-4">
                <div className="card-header">
                  <h3 className="card-title">變更密碼</h3>
                </div>
                <div className="card-body">
                  {error && <div className="alert alert-danger">{error}</div>}
                  <form action={changePasswordAction}>
                    <div className="mb-3">
                      <label className="form-label">目前密碼</label>
                      <input
                        type="password"
                        name="currentPassword"
                        className="form-control"
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">新密碼</label>
                      <input
                        type="password"
                        name="newPassword"
                        className="form-control"
                        required
                        minLength={6}
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">確認新密碼</label>
                      <input
                        type="password"
                        name="confirmPassword"
                        className="form-control"
                        required
                        minLength={6}
                      />
                    </div>
                    <button type="submit" className="btn btn-primary">
                      更新密碼
                    </button>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
