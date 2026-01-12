function App() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

  return (
    <div>
      <h1>Nuit du Basket – Frontend</h1>
      <p>API base URL : {apiBaseUrl}</p>
    </div>
  );
}

export default App;
