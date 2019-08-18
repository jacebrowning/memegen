import React from "react";
import "./App.css";

function App() {
  let backend = process.env.REACT_APP_BACKEND_URL || "";
  return (
    <div className="App">
      <header className="App-header">
        <a className="App-link" href={backend + "/api/"}>
          API
        </a>
        <a className="App-link" href={backend + "/swagger/"}>
          Documentation
        </a>
        <img src={backend + "/api/images/iw/tests_code/in_production.jpg"} />
      </header>
    </div>
  );
}

export default App;
