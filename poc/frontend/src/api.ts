const API_BASE = '/api';

export function getToken(): string | null {
  return localStorage.getItem('token');
}

export function setToken(token: string) {
  localStorage.setItem('token', token);
}

export function clearToken() {
  localStorage.removeItem('token');
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  const token = getToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (!(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || response.statusText);
  }
  return response.json();
}

export const api = {
  register: (body: Record<string, unknown>) =>
    request<{ access_token: string }>('/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body: { email: string; password: string }) =>
    request<{ access_token: string }>('/login', { method: 'POST', body: JSON.stringify(body) }),
  getProfile: () => request('/profile'),
  updateProfile: (body: Record<string, unknown>) =>
    request('/profile', { method: 'PUT', body: JSON.stringify(body) }),
  uploadImages: (formData: FormData) =>
    request('/upload-images', { method: 'POST', body: formData }),
  analyzeProduct: (url: string) =>
    request('/analyze-product', { method: 'POST', body: JSON.stringify({ url }) }),
  recommendSize: (product_id: number) =>
    request('/recommend-size', { method: 'POST', body: JSON.stringify({ product_id }) }),
  generateTryOn: (product_id?: number) =>
    request('/generate-tryon', {
      method: 'POST',
      body: JSON.stringify({ product_id: product_id ?? null }),
    }),
  chat: (message: string, product_id?: number) =>
    request('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, product_id: product_id ?? null }),
    }),
  history: () => request('/history'),
};
