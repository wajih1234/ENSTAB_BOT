var express = require("express");
var bodyParser = require("body-parser");
var mongoose = require("mongoose");
var bcrypt = require("bcryptjs");
var jwt = require("jsonwebtoken");
const cors = require('cors');
const path = require('path')

const app = express();
app.use('/chatbot', express.static(path.join(__dirname, 'ENSTA_BOT1/templates'))); // For chatbot files
const corsOptions = {
  origin: [
    'https://enstab-bot.vercel.app', 
    'http://localhost:3000'          
  ],
  methods: ['GET', 'POST', 'OPTIONS'],
  credentials: true,
  allowedHeaders: ['Content-Type', 'Authorization']
};
app.use(cors(corsOptions));

app.use(bodyParser.json());
app.use(express.static('public'));
app.use(bodyParser.urlencoded({ extended: true }));

// MongoDB Connection
mongoose.connect('mongodb+srv://cherniwajih4:wajihmadrid1@cluster0.dx1apxy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0');

var db = mongoose.connection;
db.on('error', () => console.log("Error in Connecting to Database"));
db.once('open', () => console.log("Connected to Database"));


const userSchema = new mongoose.Schema({
  name: String,
  prenom: String,
  email: String,
  password: String
});

const User = mongoose.model("User", userSchema);
// Message Schema
const messageSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User" },
  sender: String, // 'user' or 'bot'
  message: String,
  timestamp: { type: Date, default: Date.now }
});

const Message = mongoose.model("Message", messageSchema);


app.post("/sign-up", async (req, res) => {
  const { name, prenom, email, password } = req.body;

  try {
    
     const hashedPassword = await bcrypt.hash(String(password), 10);
    const newUser = new User({
      name,
      prenom,
      email,
      password: hashedPassword
    });

    await newUser.save();
    console.log("Registration Inserted Successfully");

    return res.redirect('signup_successful.html');
  } catch (error) {
    console.error(error);
    res.status(500).send("Error registering user");
  }
});


app.post("/login", async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await User.findOne({ email });

    if (!user) {
      return res.status(400).json({ error: "Adresse e-mail introuvable" });

    }
    
    const isMatch = await bcrypt.compare(password, user.password);
      
    if (!isMatch) {
      return res.status(400).json({ error: "Mot de passe incorrect" });
    }

    
    const token = jwt.sign({ userId: user._id }, 'your_jwt_secret', { expiresIn: '1h' });

    
    // Return both success status and redirect URL with token
    return res.json({ 
      success: true,
      message: "Login successful", 
      token,
      redirectUrl: `https://enstab-bot.vercel.app/chatbot?token=${token}`
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Erreur lors de la connexion" });
  }
});
app.post("/save-message", async (req, res) => {
  const { userId, sender, message } = req.body;

  try {
    const newMessage = new Message({ userId, sender, message });
    await newMessage.save();

    res.status(201).json({ success: true, message: "Message saved" });
  } catch (error) {
    console.error("Error saving message:", error);
    res.status(500).json({ error: "Error saving message" });
  }
});

app.get("/messages/:userId", async (req, res) => {
  const { userId } = req.params;

  try {
    const messages = await Message.find({ userId }).sort({ timestamp: 1 });
    res.json(messages);
  } catch (error) {
    console.error("Error fetching messages:", error);
    res.status(500).json({ error: "Error fetching messages" });
  }
});
// Add these new routes to your existing server.js:

// Chatbot page route
app.get("/chatbot", (req, res) => {
  const token = req.cookies.authToken || req.query.token;
  
  if (!token) {
    return res.redirect("/login");
  }

  try {
    jwt.verify(token, "your_jwt_secret");
    // Serve from templates directory
    res.sendFile(path.join(__dirname, "ENSTA_BOT1/templates/base.html"));
  } catch (err) {
    res.redirect("/login?error=invalid_token");
  }
});

// Predict route (from Flask)
app.post("/predict", async (req, res) => {
  const token = req.cookies.authToken || req.headers.authorization?.split(' ')[1];
  
  if (!token) return res.status(401).json({ error: "Unauthorized" });

  try {
    const decoded = jwt.verify(token, "your_jwt_secret");
    // Add your prediction logic here
    res.json({ answer: "Bot response" });
  } catch (err) {
    res.status(401).json({ error: "Invalid token" });
  }
});




app.get("/", (req, res) => {
  res.set({ "Allow-access-Allow-Origin": '*' });
  return res.redirect('index.html');
});

app.listen(8901, () => {
  console.log("Listening on port 8901");
});
