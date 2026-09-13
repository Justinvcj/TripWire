import json
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def run():
    train_path = "data/baseline2_train_labels.json"
    if not os.path.exists(train_path):
        raise FileNotFoundError(f"Missing hand-labelled training data for Baseline 2 at {train_path}")

    with open(train_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    if len(data) < 10:
        print("Warning: Training set is very small. You should hand-label ~200-300 examples.")

    texts = [item['customer_text'] for item in data]
    labels = [item['gold_intent'] for item in data]
    
    print("Training TF-IDF + LogReg baseline...")
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    X = vectorizer.fit_transform(texts)
    
    model = LogisticRegression(max_iter=1000)
    model.fit(X, labels)
    
    os.makedirs("models", exist_ok=True)
    with open("models/baseline2_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open("models/baseline2_model.pkl", "wb") as f:
        pickle.dump(model, f)
        
    print("Baseline 2 model saved.")

if __name__ == "__main__":
    run()
