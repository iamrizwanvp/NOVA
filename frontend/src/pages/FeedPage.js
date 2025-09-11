// src/pages/FeedPage.js
import React, { useEffect, useState } from "react";
import { apiFetch } from '../utils/api';
 // our API helper

const FeedPage = () => {
  const [products, setProducts] = useState([]);
  const [sortBy, setSortBy] = useState("date");
  const [menuOpen, setMenuOpen] = useState(false);

  // Fetch products from API
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const data = await apiFetch("/products/api/");
        setProducts(data);
      } catch (err) {
        console.error(err);
        alert("Error loading feed ❌");
      }
    };
    fetchProducts();
  }, []);

  // Sorting handler
  const sortedProducts = [...products].sort((a, b) => {
    if (sortBy === "price") return a.price - b.price;
    if (sortBy === "name") return a.title.localeCompare(b.title);
    return new Date(b.created_at) - new Date(a.created_at);
  });

  return (
    <div className="feed-container">

      {/* Background Video */}
      <video autoPlay loop muted className="bg-video">
        <source src="/bg.mp4" type="video/mp4" />
      </video>

      {/* Header */}
      <header className="feed-header">
        <div className="logo">NOVA</div>
        <button className="menu-btn" onClick={() => setMenuOpen(!menuOpen)}>
          ☰
        </button>
        {menuOpen && (
          <div className="menu-dropdown">
            <a href="/profile">Profile</a>
            <a href="/settings">Settings</a>
            <a href="/help">Help</a>
            <a href="/logout">Logout</a>
          </div>
        )}
      </header>

      {/* Sort Bar */}
      <div className="sort-bar">
        <label>Sort by: </label>
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="date">Date</option>
          <option value="name">Name</option>
          <option value="price">Price</option>
        </select>
      </div>

      {/* Product Cards */}
      <main className="feed-body">
        {sortedProducts.map((product) => (
          <div key={product.id} className="product-card">
            <img src={product.image1} alt={product.title} />
            <h3>{product.title}</h3>
            <p>{product.description}</p>
            <span>${product.price}</span>
          </div>
        ))}
      </main>

      {/* Upload Button */}
      <button className="upload-btn">+ Upload Your Product</button>

      {/* Footer */}
      <footer className="feed-footer">
        <p>© {new Date().getFullYear()} NOVA. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default FeedPage;
