// Lehman-Django/tailwind.config.js (V4 - Content Scanning Only)
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './LehmanCustomConstruction/templates/**/*.html',
      './**/templates/**/*.html',
    './LehmanCustomConstruction/forms.py'
  ],
  // NO theme object, NO plugins object for this approach as per the docs you want to follow
  // for theme variables.
};