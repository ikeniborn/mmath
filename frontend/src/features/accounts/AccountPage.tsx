import { useState, type FormEvent } from 'react';
import { api, bootstrap } from '../../api';

export default function AccountPage({ onAuthenticated }: { onAuthenticated: () => Promise<void> }) {
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
    } catch (cause) { setError(cause instanceof Error && cause.message === 'login_throttled' ? 'Слишком много попыток. Повторите через 15 минут.' : 'Не удалось войти. Проверьте адрес и пароль.'); }
    finally { setBusy(false); }
  }
  return <main className="auth"><h1>Считай легко</h1><p>Математика, в которой каждый ребёнок идёт своим путём.</p><div className="card"><h2>{register ? 'Создать аккаунт родителя' : 'Вход для родителя'}</h2><form onSubmit={submit}><label>Электронная почта<input name="email" type="email" autoComplete="email" required /></label><label>Пароль<input name="password" type="password" autoComplete={register ? 'new-password' : 'current-password'} minLength={12} maxLength={128} required /></label>{error && <p role="alert">{error}</p>}<button disabled={busy} type="submit">{register ? 'Зарегистрироваться' : 'Войти'}</button></form><button className="link" onClick={() => { setRegister(!register); setError(''); }}>{register ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Зарегистрироваться'}</button></div><p className="help">Почта пока не подтверждается. Если забудете пароль, обратитесь к оператору сервиса.</p></main>;
}
