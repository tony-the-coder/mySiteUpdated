// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Your main React App component

// --- Mount for Portfolio Showcase Page ---
const portfolioRootElement = document.getElementById('react-portfolio-root');
if (portfolioRootElement) {
  console.log("Found 'react-portfolio-root', mounting Portfolio App...");
  ReactDOM.createRoot(portfolioRootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}

// --- Mount for Contact Us Page ---
const contactRootElement = document.getElementById('react-contact-form-root');
if (contactRootElement) {
  console.log("Found 'react-contact-form-root', mounting Contact Form App...");
  ReactDOM.createRoot(contactRootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}

// --- Mount for Minimal Test Page ---
const minimalTestRootElement = document.getElementById('react-app-minimal-root');
if (minimalTestRootElement) {
  console.log("Found 'react-app-minimal-root', mounting Minimal Test App...");
  ReactDOM.createRoot(minimalTestRootElement).render(
    <React.StrictMode>
      <App /> {/* Or a specific minimal test component */}
    </React.StrictMode>
  );
}

// Fallback for Vite's own index.html if no specific ID is found
const genericRootElement = document.getElementById('root');
if (genericRootElement && !portfolioRootElement && !contactRootElement && !minimalTestRootElement) {
  console.log("Found generic 'root', mounting App (this might be for Vite's index.html)...");
  ReactDOM.createRoot(genericRootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
