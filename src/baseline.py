import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from src.schemas import Intent

class SimpleBaselineClassifier:
    """Baseline 2: TF-IDF + Logistic Regression for Intent Classification"""
    def __init__(self, train_csv_path: str):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        self.clf = LogisticRegression(max_iter=1000, class_weight='balanced')
        
        try:
            df = pd.read_csv(train_csv_path)
            if 'customer_text' in df.columns and 'gold_intent' in df.columns:
                X = self.vectorizer.fit_transform(df['customer_text'].fillna(""))
                y = df['gold_intent']
                self.clf.fit(X, y)
                self.is_trained = True
            else:
                self.is_trained = False
        except Exception:
            self.is_trained = False
            
    def predict(self, text: str) -> Intent:
        if not self.is_trained:
            return Intent.DELIVERY_SHIPPING_STATUS
            
        try:
            X = self.vectorizer.transform([text])
            pred = self.clf.predict(X)[0]
            # Convert string prediction to Intent enum
            for intent in Intent:
                if intent.value == pred:
                    return intent
            return Intent.DELIVERY_SHIPPING_STATUS
        except:
            return Intent.DELIVERY_SHIPPING_STATUS
