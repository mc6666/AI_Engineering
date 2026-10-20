'use server';

import { redirect } from 'next/navigation';
import {
  registerUser,
  verifyLogin,
  createSession,
  destroySession,
  changePassword,
  requireUser,
} from '@/lib/auth';

export async function loginAction(formData) {
  const username = String(formData.get('username') || '').trim();
  const password = String(formData.get('password') || '');

  let user;
  try {
    user = verifyLogin({ username, password });
  } catch (err) {
    redirect(`/login?error=${encodeURIComponent(err.message)}`);
  }
  await createSession(user);
  redirect('/portal');
}

export async function registerAction(formData) {
  const username = String(formData.get('username') || '').trim();
  const email = String(formData.get('email') || '').trim();
  const fullName = String(formData.get('fullName') || '').trim();
  const password = String(formData.get('password') || '');
  const confirmPassword = String(formData.get('confirmPassword') || '');

  if (password !== confirmPassword) {
    redirect(`/register?error=${encodeURIComponent('Passwords do not match')}`);
  }

  try {
    registerUser({ username, email, password, fullName });
  } catch (err) {
    redirect(`/register?error=${encodeURIComponent(err.message)}`);
  }
  redirect('/login?registered=1');
}

export async function logoutAction() {
  await destroySession();
  redirect('/login');
}

export async function changePasswordAction(formData) {
  const user = await requireUser();
  const currentPassword = String(formData.get('currentPassword') || '');
  const newPassword = String(formData.get('newPassword') || '');
  const confirmPassword = String(formData.get('confirmPassword') || '');

  if (newPassword !== confirmPassword) {
    redirect(`/change-password?error=${encodeURIComponent('Passwords do not match')}`);
  }

  try {
    changePassword({ userId: user.id, currentPassword, newPassword });
  } catch (err) {
    redirect(`/change-password?error=${encodeURIComponent(err.message)}`);
  }
  redirect('/portal?message=Password+changed');
}
