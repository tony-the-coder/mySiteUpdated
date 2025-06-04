import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import ContactUs from './pages/contact_us/ContactUs'
import App from './App'

document.addEventListener('DOMContentLoaded', () => {
  const contactRoot = document.getElementById('react-contact-form-root')
  if (contactRoot) {
    createRoot(contactRoot).render(
      <StrictMode>
        <ContactUs />
      </StrictMode>
    )
  } else {
    const appRoot = document.getElementById('root')
    if (appRoot) {
      createRoot(appRoot).render(
        <StrictMode>
          <App />
        </StrictMode>
      )
    }
  }
})