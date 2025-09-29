import React, { useEffect, useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Menu, X } from "lucide-react";

export default function FeedPage() {
  const [products, setProducts] = useState([]);
  const [sortBy, setSortBy] = useState("date");
  const [menuOpen, setMenuOpen] = useState(false);

  // Fetch products from Django API
  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/products/api/products/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access")}`, // JWT token stored in localStorage
        },
      })
      .then((res) => {
        setProducts(res.data);
      })
      .catch((err) => {
        console.error(err);
        alert("Error loading feed");
      });
  }, []);

  // Sorting logic
  const sortedProducts = [...products].sort((a, b) => {
    if (sortBy === "name") return a.title.localeCompare(b.title);
    if (sortBy === "price") return a.price - b.price;
    return new Date(b.created_at) - new Date(a.created_at);
  });

  return (
    <div className="relative min-h-screen bg-black text-white overflow-hidden">
      {/* Background Video */}
      <video
        autoPlay
        muted
        loop
        className="absolute top-0 left-0 w-full h-full object-cover z-0"
      >
        <source src="/background.mp4" type="video/mp4" />
      </video>
      <div className="absolute inset-0 bg-black/60 z-0"></div>

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between p-4">
        <h1 className="text-2xl font-bold">NOVA</h1>
        <button onClick={() => setMenuOpen(!menuOpen)} className="text-white">
          {menuOpen ? <X size={28} /> : <Menu size={28} />}
        </button>
        {menuOpen && (
          <div className="absolute top-16 right-4 bg-gray-900 p-4 rounded-xl shadow-lg">
            <ul className="space-y-2">
              <li className="hover:text-red-400 cursor-pointer">Profile</li>
              <li className="hover:text-red-400 cursor-pointer">Settings</li>
              <li className="hover:text-red-400 cursor-pointer">Help</li>
              <li className="hover:text-red-400 cursor-pointer">About</li>
              <li className="hover:text-red-400 cursor-pointer">Logout</li>
            </ul>
          </div>
        )}
      </header>

      {/* Sort Button */}
      <div className="relative z-10 flex justify-center mt-4">
        <select
          className="px-4 py-2 rounded-full bg-gray-800 text-white"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="date">Date</option>
          <option value="name">Name</option>
          <option value="price">Price</option>
        </select>
      </div>

      {/* Product Cards */}
      <main className="relative z-10 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 p-6">
        {sortedProducts.map((product) => (
          <motion.div
            key={product.id}
            whileHover={{ scale: 1.05 }}
            className="bg-white/10 backdrop-blur-md rounded-2xl p-4 shadow-lg overflow-hidden"
          >
            <img
              src={product.image1 || "/placeholder.png"}
              alt={product.title}
              className="rounded-xl w-full h-48 object-cover"
            />
            <h2 className="text-xl font-semibold mt-3">{product.title}</h2>
            <p className="text-gray-300">{product.description}</p>
            <p className="text-red-400 font-bold mt-2">${product.price}</p>
          </motion.div>
        ))}
      </main>

      {/* Upload Button */}
      <button
        className="fixed bottom-6 left-1/2 transform -translate-x-1/2 px-6 py-3 bg-red-500 text-white rounded-full shadow-xl hover:bg-red-600 z-10"
        onClick={() => (window.location.href = "/products/publish")}
      >
        + Upload Product
      </button>

      {/* Footer */}
      <footer className="relative z-10 text-center py-6 bg-gradient-to-r from-gray-900 via-black to-gray-900">
        <p className="text-gray-400">
          © 2025 NOVA · <span className="hover:text-red-400">About</span> ·{" "}
          <span className="hover:text-red-400">Privacy</span> ·{" "}
          <span className="hover:text-red-400">Contact</span>
        </p>
      </footer>
    </div>
  );
}
