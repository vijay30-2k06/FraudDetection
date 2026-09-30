import axios from 'axios';

const SESSION_EVENT = 'frauddesk:session-expired';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('frauddesk-token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && localStorage.getItem('frauddesk-token')) {
      localStorage.removeItem('frauddesk-token');
      localStorage.removeItem('frauddesk-user');
      window.dispatchEvent(new Event(SESSION_EVENT));
    }
    return Promise.reject(error);
  },
);

export async function signIn(credentials) {
  const { data } = await api.post('/login', credentials);
  localStorage.setItem('frauddesk-token', data.access_token);
  localStorage.setItem('frauddesk-user', JSON.stringify(data.user));
  return data.user;
}

export function signOut() {
  localStorage.removeItem('frauddesk-token');
  localStorage.removeItem('frauddesk-user');
}

export { SESSION_EVENT };
export default api;