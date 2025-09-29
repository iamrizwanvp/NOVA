const PUBLIC_API_BASE = "http://127.0.0.1:8000/products/api/products/";
const AUTH_API_BASE = "http://127.0.0.1:8000/products/api/products/"; // same endpoint but POST requires auth

// Fetch public products (non-authenticated)
async function fetchPublicProducts() {
    try {
        const response = await fetch(PUBLIC_API_BASE);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        renderProducts(data);
    } catch (err) {
        console.error("Error fetching public products:", err);
        alert("Failed to fetch public products.");
    }
}

// Render products as cards
function renderProducts(products) {
    const container = document.getElementById("productsContainer");
    container.innerHTML = "";

    if (!products || products.length === 0) {
        container.innerHTML = '<div class="col-12 text-center"><p>No products found.</p></div>';
        return;
    }

    products.forEach(product => {
        const imgUrl = product.image1 || "http://via.placeholder.com/300x200";
        const ownerEmail = product.owner?.email || "Unknown";

        container.innerHTML += `
        <div class="col-md-4">
          <div class="card shadow-sm h-100">
            <img src="${imgUrl}" class="card-img-top" alt="${product.title}" onerror="this.src='http://via.placeholder.com/300x200'">
            <div class="card-body">
              <h5 class="card-title">${product.title}</h5>
              <p class="card-text">${product.description}</p>
              <p><strong>Category:</strong> ${product.category}</p>
              <p><strong>Price:</strong> ₹${product.price}</p>
              <p><strong>Owner:</strong> ${ownerEmail}</p>
            </div>
          </div>
        </div>
        `;
    });
}

// Get JWT token from localStorage
function getAuthToken() {
    return localStorage.getItem('access_token'); 
}

// Show/hide create product form
document.getElementById("btnShowCreateForm").addEventListener("click", () => {
    const formContainer = document.getElementById("createProductFormContainer");
    formContainer.style.display = formContainer.style.display === "none" ? "block" : "none";
});

// Handle create product form submission
document.getElementById("createProductForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = getAuthToken();
    if (!token) {
        alert("You must be logged in to create a product!");
        return;
    }

    const form = e.target;
    const formData = new FormData(form);

    try {
        const response = await fetch(AUTH_API_BASE, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}` // JWT token
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || "Failed to create product");
        }

        const data = await response.json();
        alert("Product created successfully!");
        console.log("Created product:", data);
        form.reset();
        fetchPublicProducts(); // Refresh product list
    } catch (err) {
        console.error("Error creating product:", err);
        alert("Failed to create product. Check console for details.");
    }
});

// Bind public products button
document.getElementById("btnViewProducts").addEventListener("click", fetchPublicProducts);


// Track currently editing product
let currentEditProductId = null;


document.getElementById("btnEditProduct").addEventListener("click", async () => {
    const productId = prompt("Enter Product ID to edit:");
    if (!productId) return;

    const token = getAuthToken();
    if (!token) {
        alert("You must be logged in to edit a product!");
        return;
    }

    try {
        const response = await fetch(`${AUTH_API_BASE}${productId}/`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || "Failed to fetch product");
        }

        const product = await response.json();

        // Prefill form fields
        document.getElementById("title").value = product.title;
        document.getElementById("description").value = product.description;
        document.getElementById("category").value = product.category;
        document.getElementById("price").value = product.price;

        // Show form
        const formContainer = document.getElementById("createProductFormContainer");
        formContainer.style.display = "block";

        // Set current edit ID
        currentEditProductId = productId;

    } catch (err) {
        console.error("Error fetching product for edit:", err);
        alert("Failed to fetch product. Check console for details.");
    }
});

// Handle create/edit product form submission
document.getElementById("createProductForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = getAuthToken();
    if (!token) {
        alert("You must be logged in to create or edit a product!");
        return;
    }

    const form = e.target;
    const formData = new FormData(form);

    try {
        const method = currentEditProductId ? "PUT" : "POST";
        const url = currentEditProductId ? `${AUTH_API_BASE}${currentEditProductId}/` : AUTH_API_BASE;

        const response = await fetch(url, {
            method: method,
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || "Failed to submit product");
        }

        const data = await response.json();
        alert(currentEditProductId ? "Product updated successfully!" : "Product created successfully!");
        console.log("Product data:", data);

        form.reset();
        currentEditProductId = null;
        fetchPublicProducts(); // Refresh product list
    } catch (err) {
        console.error("Error submitting product:", err);
        alert("Failed to submit product. Check console for details.");
    }
});





// Delete Product
document.getElementById("btnDeleteProduct").addEventListener("click", async () => {
    const productId = prompt("Enter Product ID to delete:");
    if (!productId) return;

    const token = getAuthToken();
    if (!token) {
        alert("You must be logged in to delete a product!");
        return;
    }

    if (!confirm(`Are you sure you want to delete product ID ${productId}?`)) return;

    try {
        const response = await fetch(`${AUTH_API_BASE}${productId}/`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.status === 204 || response.ok) {
            alert("Product deleted successfully!");
            fetchPublicProducts(); // Refresh product list
        } else {
            const error = await response.text();
            throw new Error(error || "Failed to delete product");
        }
    } catch (err) {
        console.error("Error deleting product:", err);
        alert("Failed to delete product. Check console for details.");
    }
});





// Logout function
document.getElementById("btnLogout").addEventListener("click", () => {
    // Remove JWT tokens
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    // Optionally remove any other auth keys you might have
    localStorage.removeItem("authToken");
    
    // Redirect to login page
    window.location.href = "/users/login/";  // adjust this path to your login URL
});




// Utility: decode JWT to get payload
function parseJwt(token) {
    try {
        const base64Payload = token.split('.')[1];
        const payload = atob(base64Payload);
        return JSON.parse(payload);
    } catch (e) {
        console.error("Failed to parse token:", e);
        return null;
    }
}

// Show logged-in user info
function displayUserInfo() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    const payload = parseJwt(token);
    if (!payload) return;

    const username = payload.username || "Unknown";
    const email = payload.email || "";

    document.getElementById("userInfo").innerText = `${username} (${email})`;
}

// Call on page load
window.addEventListener("DOMContentLoaded", displayUserInfo);



// Fetch only current user products
async function loadMyProducts() {
    const token = localStorage.getItem("access_token");
    const res = await fetch("http://127.0.0.1:8000/products/api/products/?my=true", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await res.json();
    renderProducts(data); // reuse your existing render function
}
