import { LangToggle, useT } from '../../i18n';

/** Shown when the app cannot reach the API: the game is connected-only and nothing is served from a personal cache. */
export default function ConnectionRequired({ onRetry }: { onRetry: () => void }) {
  const { t } = useT();
  return <main className="auth"><div className="auth-header"><h1>{t('app.title')}</h1><LangToggle /></div><div className="card"><h2>{t('offline.title')}</h2><p role="alert">{t('offline.text')}</p><button type="button" onClick={onRetry}>{t('app.retry')}</button></div></main>;
}
