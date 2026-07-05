import { useEffect, useState } from 'react';
import { api } from '../api';

type HistoryItem = {
  id: number;
  role: string;
  content: string;
  product_id: number | null;
  created_at: string;
};

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);

  useEffect(() => {
    api.history().then((data) => setItems(data as HistoryItem[]));
  }, []);

  return (
    <div className="card">
      <h1 className="mb-4 text-2xl font-semibold">Chat History</h1>
      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.id} className="rounded-xl border border-slate-800 bg-slate-950 p-4">
            <div className="mb-2 flex items-center justify-between text-xs text-slate-400">
              <span className="uppercase">{item.role}</span>
              <span>{new Date(item.created_at).toLocaleString()}</span>
            </div>
            <p className="whitespace-pre-wrap">{item.content}</p>
          </div>
        ))}
        {!items.length && <p className="text-slate-400">No chat history yet.</p>}
      </div>
    </div>
  );
}
