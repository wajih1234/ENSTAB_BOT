document.getElementById("loginForm").addEventListener("submit", async function (event) {
  event.preventDefault(); // Prevent default form submission

  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const response = await fetch("https://enstab-bot.onrender.com/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    
      
      if (data.token) {
        
        
        
        
        alert("Connexion réussie !");
        
        window.location.replace(`https://enstab-bot.onrender.com/chatbot?token=${encodeURIComponent(data.token)}`);
      }
      
      
     else {
      alert("Email ou mot de passe incorrect.");
    }
  } catch (error) {
    console.error("❌ Erreur de connexion:", error);
    alert(error.message || "Une erreur est survenue");
  }
});
