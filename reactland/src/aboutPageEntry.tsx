// C:\Users\tonyt\Desktop\mySiteUpdated\reactland\src\aboutPageEntry.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { LampDemo } from './components/ui/lamp'; // Ensure this path is correct based on your folder structure
import './index.css'; // This imports your main Tailwind CSS

const rootElement = document.getElementById('about-page-lamp-hero-root');

if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <LampDemo />
    </React.StrictMode>,
  );
  console.log("React LampDemo component mounted on #about-page-lamp-hero-root.");
} else {
  console.warn('React root element #about-page-lamp-hero-root not found. LampDemo will not render.');
}