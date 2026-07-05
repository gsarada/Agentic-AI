import { type FormEvent, useEffect, useState } from 'react';
import { api } from '../api';

type Profile = {
  id: number;
  name: string;
  email: string;
  measurements: Record<string, number | string | null>;
  preferences: Record<string, unknown>;
  images: { image_type: string; file_path: string }[];
};

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [name, setName] = useState('');
  const [preferredFit, setPreferredFit] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    api.getProfile().then((data) => {
      setProfile(data as Profile);
      setName((data as Profile).name);
      setPreferredFit(String((data as Profile).preferences.preferred_fit || ''));
    });
  }, []);

  async function onSave(e: FormEvent) {
    e.preventDefault();
    const updated = await api.updateProfile({
      name,
      preferences: { preferred_fit: preferredFit },
    });
    setProfile(updated as Profile);
    setMessage('Profile updated');
  }

  if (!profile) return <p>Loading profile...</p>;

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <section className="card">
        <h1 className="mb-4 text-2xl font-semibold">Profile Dashboard</h1>
        <form onSubmit={onSave} className="space-y-3">
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} />
          <input className="input" value={preferredFit} onChange={(e) => setPreferredFit(e.target.value)} placeholder="Preferred fit" />
          <button className="btn-primary">Save changes</button>
        </form>
        {message && <p className="mt-3 text-sm text-emerald-400">{message}</p>}
      </section>

      <section className="card">
        <h2 className="mb-3 text-lg font-medium">Measurements</h2>
        <dl className="grid grid-cols-2 gap-2 text-sm">
          {Object.entries(profile.measurements).map(([key, value]) => (
            <div key={key} className="rounded-lg bg-slate-950/60 p-2">
              <dt className="text-slate-400">{key}</dt>
              <dd>{value ?? '-'}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="card lg:col-span-2">
        <h2 className="mb-3 text-lg font-medium">Uploaded Images</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {profile.images.map((img) => (
            <div key={img.image_type} className="rounded-xl border border-slate-800 p-3">
              <p className="mb-2 capitalize text-slate-400">{img.image_type}</p>
              <img src={`/images/${img.file_path}`} alt={img.image_type} className="h-48 w-full rounded-lg object-cover" />
            </div>
          ))}
          {!profile.images.length && <p className="text-slate-400">No images uploaded yet.</p>}
        </div>
      </section>
    </div>
  );
}
