import random
import json
import torch
import os
from ENSTA_BOT1.model import NeuralNet
from ENSTA_BOT1.nltk_utils import bag_of_words, tokenize

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
intents_path = os.path.join(BASE_DIR, 'intents.json')

with open(intents_path, 'r', encoding='utf-8') as f:

        intents=json.load(f)




BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # goes up one level from ENSTA_BOT1
FILE = os.path.join(BASE_DIR, "data.pth")

data = torch.load(FILE)
input_size=data["input_size"] 
hidden_size=data["hidden_size"]
output_size=data["output_size"]
allwords=data["allwords"]
tags=data["tags"]
model_state=data["model_state"]





model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Enstabot"


def get_response(sentence): 

    sentence = tokenize(sentence)
    X = bag_of_words(sentence, allwords)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                  return random.choice(intent['responses'])
    else:
           return "Je ne comprends pas..."

if __name__ == "__main__":
     print("tu veux des informations sur l 'enstab! (type 'quit' to exit)")
     while True:
    # sentence = "do you use credit cards?"
        sentence = input("You: ")
        if sentence == "quit":
             break
        
        resp = get_response(sentence)
        print(resp)
    
