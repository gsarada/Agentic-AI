import { type FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, setToken } from '../api';

const listField = (value: string) => value.split(',').map((v) => v.trim()).filter(Boolean);

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    height: '',
    weight: '',
    preferred_fit: 'Relaxed',
    preferred_colors: 'Blue, Black',
    preferred_fabrics: 'Cotton, Linen',
    chest: '',
    waist: '',
    hip: '',
  });
  const [error, setError] = useState('');

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const payload = {
        ...form,
        height: form.height ? Number(form.height) : null,
        weight: form.weight ? Number(form.weight) : null,
        chest: form.chest ? Number(form.chest) : null,
        waist: form.waist ? Number(form.waist) : null,
        hip: form.hip ? Number(form.hip) : null,
        preferred_colors: listField(form.preferred_colors),
        preferred_fabrics: listField(form.preferred_fabrics),
      };
      const { access_token } = await api.register(payload);
      setToken(access_token);
      navigate('/profile');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    }
  }

  return (
    <div className="mx-auto max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <h1 className="mb-4 text-2xl font-semibold">Create your stylist profile</h1>
      <form onSubmit={onSubmit} className="grid gap-4 md:grid-cols-2">
        <input className="input md:col-span-2" placeholder="Name" value={form.name} onChange={(e) => update('name', e.target.value)} />
        <input className="input" placeholder="Email" value={form.email} onChange={(e) => update('email', e.target.value)} />
        <input className="input" type="password" placeholder="Password" value={form.password} onChange={(e) => update('password', e.target.value)} />
        <input className="input" placeholder="Height (cm)" value={form.height} onChange={(e) => update('height', e.target.value)} />
        <input className="input" placeholder="Weight (kg)" value={form.weight} onChange={(e) => update('weight', e.target.value)} />
        <input className="input" placeholder="Chest (cm)" value={form.chest} onChange={(e) => update('chest', e.target.value)} />
        <input className="input" placeholder="Waist (cm)" value={form.waist} onChange={(e) => update('waist', e.target.value)} />
        <input className="input" placeholder="Hip (cm)" value={form.hip} onChange={(e) => update('hip', e.target.value)} />
        <input className="input md:col-span-2" placeholder="Preferred fit" value={form.preferred_fit} onChange={(e) => update('preferred_fit', e.target.value)} />
        <input className="input md:col-span-2" placeholder="Preferred colors (comma separated)" value={form.preferred_colors} onChange={(e) => update('preferred_colors', e.target.value)} />
        <input className="input md:col-span-2" placeholder="Preferred fabrics (comma separated)" value={form.preferred_fabrics} onChange={(e) => update('preferred_fabrics', e.target.value)} />
        {error && <p className="text-sm text-rose-400 md:col-span-2">{error}</p>}
        <button className="btn-primary md:col-span-2">Register</button>
      </form>
      <p className="mt-4 text-sm text-slate-400">
        Already registered? <Link className="text-violet-300" to="/login">Login</Link>
      </p>
    </div>
  );
}
