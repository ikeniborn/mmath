import { useState, type FormEvent } from 'react';
import { api, bootstrap } from '../../api';
import { LangToggle, useT } from '../../i18n';

export default function AccountPage({ onAuthenticated }: { onAuthenticated: () => Promise<void> }) {
  const { t } = useT();
  const [register, setRegister] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true); setError('');
    try {
      await bootstrap();
      await api(`/auth/${register ? 'register' : 'login'}`, 'POST', { email: form.get('email'), password: form.get('password') });
      await onAuthenticated();
    } catch (cause) { setError(cause instanceof Error && cause.message === 'login_throttled' ? t('auth.throttled') : t('auth.failed')); }
    finally { setBusy(false); }
  }
  return <main className="auth"><div className="auth-header"><h1>{t('app.title')}</h1><LangToggle /></div><p>{t('auth.tagline')}</p><div className="card"><h2>{register ? t('auth.register.title') : t('auth.login.title')}</h2><form onSubmit={submit}><label>{t('auth.email')}<input name="email" type="email" autoComplete="email" required /></label><label>{t('auth.password')}<input name="password" type="password" autoComplete={register ? 'new-password' : 'current-password'} minLength={12} maxLength={128} required /></label>{error && <p role="alert">{error}</p>}<button disabled={busy} type="submit">{register ? t('auth.register') : t('auth.login')}</button></form><button className="link" onClick={() => { setRegister(!register); setError(''); }}>{register ? t('auth.toLogin') : t('auth.toRegister')}</button></div><p className="help">{t('auth.help')}</p></main>;
}
