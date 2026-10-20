'use server';

import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import { requirePermission } from '@/lib/auth';
import {
  createUserByAdmin,
  updateUserByAdmin,
  deleteUser,
  createRole,
  updateRole,
  deleteRole,
} from '@/lib/rbac';

function parseRoleIds(formData) {
  return formData.getAll('roleIds').map(Number);
}

function parseFunctionIds(formData) {
  return formData.getAll('functionIds').map(Number);
}

export async function createUserAction(formData) {
  await requirePermission('admin.users');
  const username = String(formData.get('username') || '').trim();
  const email = String(formData.get('email') || '').trim();
  const fullName = String(formData.get('fullName') || '').trim();
  const password = String(formData.get('password') || '');
  try {
    createUserByAdmin({ username, email, fullName, password, roleIds: parseRoleIds(formData) });
  } catch (err) {
    redirect(`/admin/users/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/admin/users');
  redirect('/admin/users');
}

export async function updateUserAction(formData) {
  await requirePermission('admin.users');
  const id = Number(formData.get('id'));
  const fullName = String(formData.get('fullName') || '').trim();
  const email = String(formData.get('email') || '').trim();
  const isActive = formData.get('isActive') === 'on';
  try {
    updateUserByAdmin(id, { fullName, email, isActive, roleIds: parseRoleIds(formData) });
  } catch (err) {
    redirect(`/admin/users/${id}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/admin/users');
  redirect('/admin/users');
}

export async function deleteUserAction(formData) {
  await requirePermission('admin.users');
  const id = Number(formData.get('id'));
  deleteUser(id);
  revalidatePath('/admin/users');
  redirect('/admin/users');
}

export async function createRoleAction(formData) {
  await requirePermission('admin.roles');
  const name = String(formData.get('name') || '').trim();
  const description = String(formData.get('description') || '').trim();
  try {
    createRole({ name, description, functionIds: parseFunctionIds(formData) });
  } catch (err) {
    redirect(`/admin/roles/new?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/admin/roles');
  redirect('/admin/roles');
}

export async function updateRoleAction(formData) {
  await requirePermission('admin.roles');
  const id = Number(formData.get('id'));
  const name = String(formData.get('name') || '').trim();
  const description = String(formData.get('description') || '').trim();
  try {
    updateRole(id, { name, description, functionIds: parseFunctionIds(formData) });
  } catch (err) {
    redirect(`/admin/roles/${id}?error=${encodeURIComponent(err.message)}`);
  }
  revalidatePath('/admin/roles');
  redirect('/admin/roles');
}

export async function deleteRoleAction(formData) {
  await requirePermission('admin.roles');
  const id = Number(formData.get('id'));
  deleteRole(id);
  revalidatePath('/admin/roles');
  redirect('/admin/roles');
}
