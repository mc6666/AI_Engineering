import Link from 'next/link';
import { registerAction } from '@/app/actions/auth';

export const metadata = { title: 'Register - ERP System' };

export default async function RegisterPage({ searchParams }) {
  const { error } = await searchParams;

  return (
    <div className="login-page">
      <div className="login-box">
        <div className="login-logo">
          <b>ERP</b>System
        </div>
        <div className="card">
          <div className="card-body register-card-body">
            <p className="login-box-msg">建立新帳號</p>

            {error && <div className="alert alert-danger">{error}</div>}

            <form action={registerAction}>
              <div className="input-group mb-3">
                <input
                  type="text"
                  name="fullName"
                  className="form-control"
                  placeholder="姓名"
                  required
                />
              </div>
              <div className="input-group mb-3">
                <input
                  type="text"
                  name="username"
                  className="form-control"
                  placeholder="使用者名稱"
                  required
                />
              </div>
              <div className="input-group mb-3">
                <input
                  type="email"
                  name="email"
                  className="form-control"
                  placeholder="電子郵件"
                  required
                />
              </div>
              <div className="input-group mb-3">
                <input
                  type="password"
                  name="password"
                  className="form-control"
                  placeholder="密碼"
                  required
                  minLength={6}
                />
              </div>
              <div className="input-group mb-3">
                <input
                  type="password"
                  name="confirmPassword"
                  className="form-control"
                  placeholder="確認密碼"
                  required
                  minLength={6}
                />
              </div>
              <div className="row">
                <div className="col-12">
                  <button type="submit" className="btn btn-primary d-block w-100">
                    註冊
                  </button>
                </div>
              </div>
            </form>

            <p className="mb-0 mt-3">
              <Link href="/login">已經有帳號？登入</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
