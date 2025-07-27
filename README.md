# 💬 ENSTAB Chatbot

A university-oriented chatbot that helps students access essential information and services quickly. This app combines a custom-built deep learning model with a full-stack web interface using both **Node.js** and **Flask** backends.

---

## 🧠 Features

- 🔐 User Authentication (Login/Signup)
- 💬 Real-time chatbot conversation
- 🧾 Each user's conversation history stored in MongoDB
- 🤖 Custom AI model built with **PyTorch** (2 hidden layers)
- 🧠 NLP preprocessing: **tokenization**, **stemming**, and **bag of words**
- 🌍 Fullstack architecture: frontend + dual backend (auth & chatbot logic)

---

## 🛠️ Tech Stack

| Layer         | Technology                     |
|--------------|----------------------------------|
| Frontend     | HTML, CSS, JavaScript           |
| Backend #1   | Node.js + Express.js (auth/API) |
| Backend #2   | Flask + PyTorch (chatbot logic) |
| AI/ML        | PyTorch (feedforward neural net)|
| NLP          | Tokenization, Stemming, Bag of Words |
| Database     | MongoDB (Atlas)                 |
| Auth         | JWT                             |
| Hosting      | Vercel (Frontend), Render (Backends) |

---




---

## 🧠 AI & NLP

The chatbot is powered by a **feedforward neural network** trained with **PyTorch**, featuring:

- 🧠 **Two hidden layers**
- 🧠 **Softmax output for classification**
- ✂️ **Tokenization** and **stemming** using NLTK
- 📊 **Bag-of-words** vectorization
- 🗂️ Trained on custom `intents.json` file

### 📦 Training the Model

cd ENSTA_BOT1
python train.py

## Set Up Node.js Backend 


cd logpfa2
node server.js or nodemon start
## run the flask backend
cd ENSTA_BOT1
python app.py
