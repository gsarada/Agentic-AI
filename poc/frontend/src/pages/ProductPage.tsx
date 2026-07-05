import { type FormEvent, useState } from 'react';
import { api } from '../api';

export default function ProductPage() {
  const [url, setUrl] = useState('');
  const [analysis, setAnalysis] = useState<any>(null);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [tryOn, setTryOn] = useState<any>(null);
  const [error, setError] = useState('');

  async function analyze(e: FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const result = await api.analyzeProduct(url);
      setAnalysis(result);
      setRecommendation(null);
      setTryOn(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    }
  }

  async function recommend() {
    if (!analysis?.product_id) return;
    const result = await api.recommendSize(analysis.product_id);
    setRecommendation(result);
  }

  async function tryOnGenerate() {
    if (!analysis?.product_id) return;
    const result = await api.generateTryOn(analysis.product_id);
    setTryOn(result);
  }

  return (
    <div className="space-y-6">
      <section className="card">
        <h1 className="mb-4 text-2xl font-semibold">Analyze Product URL</h1>
        <form onSubmit={analyze} className="flex flex-col gap-3 md:flex-row">
          <input className="input flex-1" placeholder="Paste Amazon, Nike, Zara, Myntra URL..." value={url} onChange={(e) => setUrl(e.target.value)} />
          <button className="btn-primary">Analyze</button>
        </form>
        {error && <p className="mt-3 text-rose-400">{error}</p>}
      </section>

      {analysis && (
        <>
          <section className="card">
            <h2 className="mb-3 text-xl font-medium">Product Analysis</h2>
            <pre className="overflow-auto rounded-xl bg-slate-950 p-4 text-sm">{JSON.stringify(analysis.product_profile, null, 2)}</pre>
            <div className="mt-4 flex flex-wrap gap-3">
              <button className="btn-primary" onClick={recommend}>Recommend Size</button>
              <button className="btn-secondary" onClick={tryOnGenerate}>Generate Try-On</button>
            </div>
          </section>

          {recommendation && (
            <section className="card">
              <h2 className="mb-3 text-xl font-medium">Size Recommendation</h2>
              <p className="text-3xl font-bold text-violet-300">{recommendation.recommendation.recommended_size}</p>
              <p className="mt-2 text-slate-300">Confidence: {(recommendation.recommendation.confidence_score * 100).toFixed(0)}%</p>
              <p className="mt-4">{recommendation.recommendation.explanation}</p>
              <h3 className="mt-6 font-medium">Review Intelligence</h3>
              <pre className="mt-2 overflow-auto rounded-xl bg-slate-950 p-4 text-sm">{JSON.stringify(recommendation.review_intelligence, null, 2)}</pre>
            </section>
          )}

          {tryOn && (
            <section className="card">
              <h2 className="mb-3 text-xl font-medium">Generated Try-On</h2>
              <img src={`/images/${tryOn.file_path}`} alt="Try-on preview" className="max-h-[32rem] rounded-xl border border-slate-800" />
              <p className="mt-2 text-sm text-slate-400">Provider: {tryOn.provider}</p>
            </section>
          )}
        </>
      )}
    </div>
  );
}
