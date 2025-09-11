// src/App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import FeedPage from "./pages/FeedPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<FeedPage />} />
      </Routes>
    </Router>
  );
}

export default App;
