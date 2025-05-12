import { useState } from 'react';

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isFallback, setIsFallback] = useState(false);
  const [fallbackText, setFallbackText] = useState('');
  const [data, setData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const endpoint = '/generate10/json';
      const body = isFallback
        ? { text: fallbackText }
        : { url };
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        const json = await res.json();
        setData(json);
        setIsFallback(false);
      } else if (res.status === 422) {
        const err = await res.json();
        setError(err.detail || 'Insufficient prompts generated');
        setIsFallback(true);
      } else {
        const err = await res.json();
        throw new Error(err.detail || res.statusText);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">10-Prompt Bootstrapper</h1>
      {!data && (
        <form onSubmit={handleSubmit} className="mb-4">
          <div className="flex">
            {!isFallback ? (
              <input
                type="url"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
                className="flex-grow p-2 border border-gray-300 rounded-l"
                disabled={loading}
              />
            ) : (
              <textarea
                placeholder="Paste additional copy here..."
                value={fallbackText}
                onChange={(e) => setFallbackText(e.target.value)}
                required
                className="flex-grow p-2 border border-gray-300 rounded-l"
                rows={4}
                disabled={loading}
              />
            )}
            <button
              type="submit"
              disabled={loading}
              className="bg-indigo-600 text-white p-2 rounded-r"
            >
              {loading
                ? 'Processing...'
                : isFallback
                ? 'Retry'
                : 'Generate'}
            </button>
          </div>
          {error && <p className="text-red-500 mt-2">{error}</p>}
        </form>
      )}
      {data && (
        <div>
          {/* Brand header with logo and primary color */}
          <div className="flex items-center mb-4" style={{ color: data.palette[0] }}>
            {data.logo_url && (
              <img src={data.logo_url} alt="logo" className="h-12 mr-3" />
            )}
            <h2 className="text-2xl font-semibold">AI Prompt Pack</h2>
          </div>
          <ol className="list-decimal list-inside space-y-4 mb-4">
            {data.prompts.map((p, i) => (
              <li key={i}>
                <p className="font-medium">{p}</p>
                <p className="text-sm text-gray-600">{data.tips[i]}</p>
              </li>
            ))}
          </ol>
          <button
            onClick={async () => {
              const res = await fetch('/generate10/pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  prompts: data.prompts,
                  tips: data.tips,
                  logo_url: data.logo_url,
                  palette: data.palette,
                }),
              });
              if (res.ok) {
                const blob = await res.blob();
                const urlObj = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = urlObj;
                a.download = 'prompts10.pdf';
                document.body.appendChild(a);
                a.click();
                a.remove();
                URL.revokeObjectURL(urlObj);
              } else {
                alert('Failed to download PDF.');
              }
            }}
            className="text-white p-2 rounded"
            style={{ backgroundColor: data.palette[1] || '#10B981' }}
          >
            Download PDF
          </button>
        </div>
      )}
    </div>
  );
}

export default App;