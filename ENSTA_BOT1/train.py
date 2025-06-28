import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split  # Import for splitting data
from model import NeuralNet
from nltk_utils import tokenize, stem, bag_of_words

# Load intents.json
with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

allwords = []
tags = []
xy = []

# Process intents data
for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        allwords.extend(w)
        xy.append((w, tag))

# Ignore common punctuation
ignore_words = ['?', '!', '.', ',']
allwords = [stem(w) for w in allwords if w not in ignore_words]
allwords = sorted(set(allwords))
tags = sorted(set(tags))

# Create training data
x_data = []
y_data = []
for (pattern, tag) in xy:
    bag = bag_of_words(pattern, allwords)
    x_data.append(bag)
    label = tags.index(tag)
    y_data.append(label)

x_data = np.array(x_data)
y_data = np.array(y_data)

# **Step 1: Split the Data (Train: 80%, Validation: 15%, Test: 5%)**
x_train, x_temp, y_train, y_temp = train_test_split(x_data, y_data, test_size=0.2, random_state=42)
x_valid, x_test, y_valid, y_test = train_test_split(x_temp, y_temp, test_size=0.25, random_state=42)

# **Step 2: Create a Dataset Class**
class ChatDataset(Dataset):
    def __init__(self, x, y):
        self.x_data = x
        self.y_data = y
        self.n_samples = len(x)

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples

# **Step 3: Create DataLoaders**
batch_size = 8
train_dataset = ChatDataset(x_train, y_train)
valid_dataset = ChatDataset(x_valid, y_valid)
test_dataset = ChatDataset(x_test, y_test)

train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
valid_loader = DataLoader(dataset=valid_dataset, batch_size=batch_size, shuffle=False)
test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)

# **Step 4: Define Model Parameters**
input_size = len(x_train[0])
hidden_size = 16
output_size = len(tags)
learning_rate = 0.001
num_epochs = 1000

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = NeuralNet(input_size, hidden_size, output_size).to(device)

# **Loss and Optimizer**
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# **Step 5: Training Loop**
for epoch in range(num_epochs):
    model.train()
    for words, labels in train_loader:
        words = words.to(device)
        labels = labels.to(device)

        outputs = model(words)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # **Validation Step Every 100 Epochs**
    if (epoch + 1) % 100 == 0:
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for words, labels in valid_loader:
                words = words.to(device)
                labels = labels.to(device)
                outputs = model(words)
                val_loss += criterion(outputs, labels).item()

        val_loss /= len(valid_loader)
        print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {loss.item():.4f}, Validation Loss: {val_loss:.4f}")

# **Step 6: Final Test Accuracy**
model.eval()
correct = 0
total = 0
with torch.no_grad():
    for words, labels in test_loader:
        words = words.to(device)
        labels = labels.to(device)
        outputs = model(words)
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

accuracy = 100 * correct / total
print(f"Final Test Accuracy: {accuracy:.2f}%")

# **Save the trained model**
data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "output_size": output_size,
    "hidden_size": hidden_size,
    "allwords": allwords,
    "tags": tags
}
FILE = "data.pth"
torch.save(data, FILE)
print(f"Training complete, file saved to {FILE}")
