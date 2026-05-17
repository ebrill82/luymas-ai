import React, { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';

function App() {
  const [greeting, setGreeting] = useState('');
  const [name, setName] = useState('');

  const handleGreet = async () => {
    const result = await invoke('greet', { name: name || 'World' });
    setGreeting(result as string);
  };

  const handleHealthCheck = async () => {
    const result = await invoke('health_check');
    alert(`Health: ${result}`);
  };

  return (
    <div className="container">
      <h1>Welcome to Luymas App</h1>
      <p>Built with Luymas AI — Tauri + React</p>
      
      <div className="row">
        <input
          type="text"
          placeholder="Enter your name..."
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button onClick={handleGreet}>Greet</button>
      </div>
      
      {greeting && <p className="greeting">{greeting}</p>}
      
      <button onClick={handleHealthCheck} className="secondary">
        Health Check
      </button>
    </div>
  );
}

export default App;
