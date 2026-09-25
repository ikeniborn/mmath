import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './app';
import { LangProvider } from './i18n';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><LangProvider><BrowserRouter><App /></BrowserRouter></LangProvider></React.StrictMode>);
