export async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
  
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    };
  
    const response = await fetch(url, {
      ...options,
      headers: { ...headers, ...(options.headers || {}) },
    });
  
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.message || 'API Error');
    }
  
    return response.json();
  }
  