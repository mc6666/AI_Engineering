import Link from 'next/link';
import { loginAction } from '@/app/actions/auth';

export const metadata = { title: 'Login - ERP System' };

export default async function LoginPage({ searchParams }) {
  const { error, registered } = await searchParams;

  return (
    <div className="login-page">
      <div className="login-box">
        <div className="login-logo">
          <b>ERP</b>System
        </div>
        <div className="card">
          <div className="card-body login-card-body">
            <p className="login-box-msg">請登入以繼續</p>

            {registered && (
              <div className="alert alert-success">註冊成功，請登入。</div>
            )}
            {error && <div className="alert alert-danger">{error}</div>}

            <form action={loginAction}>
              <div className="input-group mb-3">
                <input
                  type="text"
                  name="username"
                  className="form-control"
                  placeholder="使用者名稱"
                  required
                  autoFocus
                />
                <div className="input-group-text">
                  <span className="bi bi-person" />
                </div>
              </div>
              <div className="input-group mb-3">
                <input
                  type="password"
                  name="password"
                  className="form-control"
                  placeholder="密碼"
                  required
                />
                <div className="input-group-text">
                  <span className="bi bi-lock-fill" />
                </div>
              </div>
              <div className="row">
                <div className="col-12">
                  <button type="submit" className="btn btn-primary d-block w-100">
                    登入
                  </button>
                </div>
              </div>
            </form>

            <p className="mb-0 mt-3">
              <Link href="/register">建立新帳號</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
