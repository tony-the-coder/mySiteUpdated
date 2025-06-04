// frontend/src/TestComponent.tsx
function TestComponent() {
  console.log('Rendering ultra-minimal TestComponent (for @vitejs/plugin-react)');
  return (
    <div style={{ border: '3px solid orange', padding: '25px', margin: '25px', fontFamily: 'sans-serif', backgroundColor: '#fff5e6' }}>
      <h2 style={{ color: 'darkorange', marginBottom: '10px' }}>Super Minimal React Test (Babel Plugin)</h2>
      <p>If you see this, basic React rendering via the Babel plugin is working.</p>
    </div>
  );
}
export default TestComponent;