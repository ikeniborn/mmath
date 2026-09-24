import { useEffect, useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { api, bootstrap, clearCsrf, type Player, type Session } from './api';
import AccountPage from './features/accounts/AccountPage';
import PlayerPicker from './features/players/PlayerPicker';
import PlayerSettings from './features/players/PlayerSettings';

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [error, setError] = useState('');

  async function refresh() {
    const next = await bootstrap();
    setSession(next);
    setPlayers(next.email ? await api<Player[]>('/players') : []);
  }

  useEffect(() => { refresh().catch(() => setError('Нет соединения с сервером. Попробуйте позже.')); }, []);
  async function logout() {
    await api('/auth/logout', 'POST');
    clearCsrf();
    await refresh();
  }
  if (error) return <main><h1>Считай легко</h1><p role="alert">{error}</p><button onClick={() => refresh().catch(() => {})}>Повторить</button></main>;
  if (!session) return <main><h1>Считай легко</h1><p>Загрузка…</p></main>;
  if (!session.email) return <AccountPage onAuthenticated={refresh} />;
  return <main><header><h1>Считай легко</h1><div className="account"><span>{session.email}</span><button onClick={logout}>Выйти</button></div></header><Routes>
    <Route path="/" element={<PlayerPicker players={players} onChange={refresh} />} />
    <Route path="/children/:id/settings" element={<PlayerSettings players={players} onChange={refresh} />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes></main>;
}
