// frontend/src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App'; // Your main React App component

// For the portfolio showcase page
const portfolioRootElement = document.getElementById('react-portfolio-root');
if (portfolioRootElement) {
  ReactDOM.createRoot(portfolioRootElement).render(
    <React.StrictMode>
      <App /> {/* Or your specific Portfolio App component */}
    </React.StrictMode>
  );
}

// For the contact page (if you have a separate React app/component for it)
const contactRootElement = document.getElementById('react-contact-form-root');
if (contactRootElement) {
    // Assuming App or a different root component is used for the contact form
    ReactDOM.createRoot(contactRootElement).render(
        <React.StrictMode>
            <App /> {/* Or your specific Contact Form App component */}
        </React.StrictMode>
    );
}