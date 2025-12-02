from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import re
import os
import shutil
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import firebase_admin
from firebase_admin import credentials, storage

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter app to access

# Configuration
FIREBASE_STORAGE_BUCKET = 'ordernpickapp.firebasestorage.app'  # Your Firebase Storage bucket
FIREBASE_CREDS_PATH = 'firebase-credentials.json'  # Service account key
STORAGE_FOLDER = 'SentimentalAnalysis'  # Your Firebase Storage folder

# Local cache directory for model files
LOCAL_MODEL_DIR = 'cached_model'

# Global variables to store loaded model and tokenizer
model = None
tokenizer = None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_CREDS_PATH)
            firebase_admin.initialize_app(cred, {
                'storageBucket': FIREBASE_STORAGE_BUCKET
            })
        print("✓ Firebase initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Firebase initialization failed: {e}")
        print("  Make sure firebase-credentials.json exists")
        return False

def download_from_firebase_storage(remote_path, local_path):
    """Download file from Firebase Storage"""
    try:
        bucket = storage.bucket()
        blob = bucket.blob(remote_path)
        
        print(f"  Downloading {remote_path}...")
        blob.download_to_filename(local_path)
        print(f"  ✓ Downloaded to {local_path}")
        return True
    except Exception as e:
        print(f"  ✗ Download failed: {e}")
        return False

def load_resources():
    """Load the model and tokenizer (from Firebase Storage if needed)"""
    global model, tokenizer
    
    try:
        print("\n=== Loading Model Resources ===")
        
        # Check if we need to download from Firebase
        need_download = not os.path.exists(LOCAL_MODEL_PATH) or not os.path.exists(LOCAL_TOKENIZER_PATH)
        
        if need_download:
            print("Model files not found locally, downloading from Firebase Storage...")
            
            # Initialize Firebase
            if not initialize_firebase():
                print("⚠ Firebase not available, using dummy predictions")
                return
            
            # Download model file
            model_remote_path = f"{STORAGE_FOLDER}/emotion_model.h5"  # UPDATE filename if different
            if not download_from_firebase_storage(model_remote_path, LOCAL_MODEL_PATH):
                print("⚠ Model download failed, using dummy predictions")
                return
            
            # Download tokenizer file
            tokenizer_remote_path = f"{STORAGE_FOLDER}/tokenizer.pkl"  # UPDATE filename if different
            if not download_from_firebase_storage(tokenizer_remote_path, LOCAL_TOKENIZER_PATH):
                print("⚠ Tokenizer download failed, using dummy predictions")
                return
        else:
            print("Using cached model files...")
        
        # Load the model
        print("Loading model...")
        model = load_model(LOCAL_MODEL_PATH)
        print("✓ Model loaded successfully")
        
        # Load tokenizer
        print("Loading tokenizer...")
        with open(LOCAL_TOKENIZER_PATH, 'rb') as f:
            tokenizer = pickle.load(f)
        print("✓ Tokenizer loaded successfully")
        
        print("=== Ready to accept requests! ===\n")
        
    except Exception as e:
        print(f"✗ Error loading resources: {e}")
        print("⚠ Using dummy predictions for testing")
        model = None
        tokenizer = None

def preprocess_text(text):
    """Clean and preprocess review text"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and extra spaces
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def predict_sentiment(text):
    """Predict sentiment from review text"""
    global model, tokenizer
    
    # If model isn't loaded, return neutral (for testing)
    if model is None or tokenizer is None:
        return {
            'sentiment': 'neutral',
            'confidence': 0.5,
            'scores': {
                'negative': 0.33,
                'neutral': 0.34,
                'positive': 0.33
            }
        }
    
    try:
        # Preprocess text
        cleaned_text = preprocess_text(text)
        
        # Tokenize and pad
        sequences = tokenizer.texts_to_sequences([cleaned_text])
        padded = pad_sequences(sequences, maxlen=max_length, padding='post')
        
        # Predict
        prediction = model.predict(padded, verbose=0)[0]
        
        # Map predictions to sentiment labels
        sentiment_labels = ['negative', 'neutral', 'positive']
        sentiment_idx = np.argmax(prediction)
        sentiment = sentiment_labels[sentiment_idx]
        confidence = float(prediction[sentiment_idx])
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': {
                'negative': float(prediction[0]),
                'neutral': float(prediction[1]),
                'positive': float(prediction[2])
            }
        }
    except Exception as e:
        print(f"Prediction error: {e}")
        return {
            'sentiment': 'neutral',
            'confidence': 0.0,
            'error': str(e)
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'tokenizer_loaded': tokenizer is not None
    })

@app.route('/api/analyze-sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment of review text"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing required field: text'
            }), 400
        
        review_text = data['text']
        
        if not review_text or len(review_text.strip()) == 0:
            return jsonify({
                'error': 'Review text cannot be empty'
            }), 400
        
        # Predict sentiment
        result = predict_sentiment(review_text)
        
        return jsonify({
            'success': True,
            'data': result,
            'original_text': review_text
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple reviews at once"""
    try:
        data = request.get_json()
        
        if not data or 'reviews' not in data:
            return jsonify({
                'error': 'Missing required field: reviews'
            }), 400
        
        reviews = data['reviews']
        
        if not isinstance(reviews, list):
            return jsonify({
                'error': 'Reviews must be a list'
            }), 400
        
        results = []
        for review in reviews:
            if 'text' in review and review['text']:
                sentiment_result = predict_sentiment(review['text'])
                results.append({
                    'id': review.get('id', None),
                    'sentiment': sentiment_result
                })
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Load model at startup
    load_resources()
    
    # Run the server
    # For development: debug=True
    # For production: use a proper WSGI server like gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)
