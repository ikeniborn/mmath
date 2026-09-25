import { useEffect, useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { api, bootstrap, clearCsrf, type Player, type Session } from './api';
import AccountPage from './features/accounts/AccountPage';
import ChildHome from './features/game/ChildHome';
import GamePage from './features/game/GamePage';
import { clearPending } from './features/game/pendingSubmission';
import PlayerPicker from './features/players/PlayerPicker';
import PlayerSettings from './features/players/PlayerSettings';
import ProgressPage from './features/progress/ProgressPage';
import { LangToggle, useT } from './i18n';

export default function App() {
  const { t } = useT();
  const [session, setSession] = useState<Session | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [error, setError] = useState(false);

  async function refresh() {
    const next = await bootstrap();
    setSession(next);
    setPlayers(next.email ? await api<Player[]>('/players') : []);
  }

  useEffect(() => { refresh().catch(() => setError(true)); }, []);
  async function logout() {
    await api('/auth/logout', 'POST');
    clearCsrf();
    clearPending();
    await refresh();
  }
  if (error) return <main><h1>{t('app.title')}</h1><p role="alert">{t('app.offline')}</p><button onClick={() => refresh().catch(() => {})}>{t('app.retry')}</button></main>;
  if (!session) return <main><h1>{t('app.title')}</h1><p>{t('app.loading')}</p></main>;
  if (!session.email) return <AccountPage onAuthenticated={refresh} />;
  return <main><header><h1>{t('app.title')}</h1><div className="account"><span>{session.email}</span><LangToggle /><button onClick={logout}>{t('app.logout')}</button></div></header><Routes>
    <Route path="/" element={<PlayerPicker players={players} onChange={refresh} />} />
    <Route path="/children/:id/settings" element={<PlayerSettings players={players} onChange={refresh} />} />
    <Route path="/children/:id" element={<ChildHome players={players} />} />
    <Route path="/children/:id/play" element={<GamePage players={players} />} />
    <Route path="/children/:id/progress" element={<ProgressPage players={players} />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes></main>;
}
