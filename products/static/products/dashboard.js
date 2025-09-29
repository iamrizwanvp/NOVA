// =====================
// Helpers
// =====================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
  function getAuthHeaders(extra = {}) {
    const token = localStorage.getItem("access_token");
    return {
      "Authorization": token ? `Bearer ${token}` : "",
      "X-CSRFToken": getCookie("csrftoken"),
      ...extra,
    };
  }
  
  // =====================
  // Profile Handling
  // =====================
  function renderProfile(data) {
    // Debug in console
    console.log("Profile data:", data);
  
    // Update raw JSON
    document.getElementById("myProfileResult").innerText = JSON.stringify(data, null, 2);
  
    // Update preview UI
    document.getElementById("profileNickname").innerText = data.nickname || "(no nickname)";
    document.getElementById("profilePicPreview").src = data.profile_picture || "/static/images/avatar_fallback.png";
  }
  
  function getMyProfile() {
    fetch("/users/api/profile/", {
      method: "GET",
      headers: getAuthHeaders()
    })
    .then(res => res.json())
    .then(data => renderProfile(data))
    .catch(err => console.error("Profile fetch error:", err));
  }
  
  function updateProfile() {
    const formData = new FormData();
    formData.append("nickname", document.getElementById("nickname").value);
    const pic = document.getElementById("profilePicture").files[0];
    if (pic) formData.append("profile_picture", pic);
  
    fetch("/users/api/profile/update/", {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById("updateProfileResult").innerText = JSON.stringify(data, null, 2);
      renderProfile(data);
    })
    .catch(err => console.error("Profile update error:", err));
  }
  
  function changePassword() {
    const payload = {
      old_password: document.getElementById("oldPassword").value,
      new_password: document.getElementById("newPassword").value
    };
  
    fetch("/users/api/profile/change-password/", {
      method: "PUT",
      headers: getAuthHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById("changePasswordResult").innerText = JSON.stringify(data, null, 2);
    })
    .catch(err => console.error("Password change error:", err));
  }
  
  // =====================
  // Public User Profile (by ID)
  // =====================
  function findUser() {
    const userId = document.getElementById("findUserId").value;
    fetch(`/users/api/profile/${userId}/`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById("findUserResult").innerText = JSON.stringify(data, null, 2);
    })
    .catch(err => console.error("Find user error:", err));
  }
  