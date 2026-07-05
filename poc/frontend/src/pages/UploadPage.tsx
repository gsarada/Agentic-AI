import { type FormEvent, useState } from 'react';
import { api } from '../api';

export default function UploadPage() {
  const [front, setFront] = useState<File | null>(null);
  const [side, setSide] = useState<File | null>(null);
  const [back, setBack] = useState<File | null>(null);
  const [message, setMessage] = useState('');

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const formData = new FormData();
    if (front) formData.append('front', front);
    if (side) formData.append('side', side);
    if (back) formData.append('back', back);
    await api.uploadImages(formData);
    setMessage('Images uploaded successfully');
  }

  return (
    <div className="card max-w-2xl">
      <h1 className="mb-4 text-2xl font-semibold">Upload Body Images</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <label className="block text-sm text-slate-300">
          Front image
          <input type="file" accept="image/*" className="mt-2 block w-full" onChange={(e) => setFront(e.target.files?.[0] || null)} />
        </label>
        <label className="block text-sm text-slate-300">
          Side image
          <input type="file" accept="image/*" className="mt-2 block w-full" onChange={(e) => setSide(e.target.files?.[0] || null)} />
        </label>
        <label className="block text-sm text-slate-300">
          Back image (optional)
          <input type="file" accept="image/*" className="mt-2 block w-full" onChange={(e) => setBack(e.target.files?.[0] || null)} />
        </label>
        <button className="btn-primary">Upload</button>
      </form>
      {message && <p className="mt-4 text-emerald-400">{message}</p>}
    </div>
  );
}
