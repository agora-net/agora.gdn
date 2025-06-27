import React from 'react';
import ReactDOM from 'react-dom/client';
import { NewsletterForm } from './components/NewsletterForm';

const root = ReactDOM.createRoot(
  document.getElementById('newsletter-form-root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <NewsletterForm />
  </React.StrictMode>
);
