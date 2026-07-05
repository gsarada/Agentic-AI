import { type FormEvent, useState } from 'react';
import { api } from '../api';

export default function ChatPage() {
  const [message, setMessage] = useState('');
  const [productId, setProductId] = useState('');
  const [reply, setReply] = useState('');

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const result = await api.chat(message, productId ? Number(productId) : undefined) as { reply: string };
    setReply(result.reply);
  }

  return (
    <div className="card max-w-3xl">
      <h1 className="mb-4 text-2xl font-semibold">Stylist Chat</h1>
      <form onSubmit={onSubmit} className="space-y-3">
        <input className="input" placeholder="Optional product ID for context" value={productId} onChange={(e) => setProductId(e.target.value)} />
        <textarea className="input min-h-28" placeholder="Will this fit me? Should I size up?" value={message} onChange={(e) => setMessage(e.target.value)} />
        <button className="btn-primary">Ask stylist</button>
      </form>
      {reply && (
        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950 p-4">
          <h2 className="mb-2 font-medium text-violet-300">Assistant</h2>
          <p className="whitespace-pre-wrap">{reply}</p>
        </div>
      )}
    </div>
  );
}
