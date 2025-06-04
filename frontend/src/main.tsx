import { createRoot } from 'react-dom/client';
import TestComponent from './TestComponent';

const rootElement = document.getElementById('root');
if (rootElement) {
  const root = createRoot(rootElement);
  root.render(<TestComponent />);
} else {
  console.error("Root element (#root) not found.");
}