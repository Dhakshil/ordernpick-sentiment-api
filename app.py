from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import firebase_admin
from firebase_admin import credentials, storage

app = Flask(__name__)
CORS(app)

# Configuration
FIREBASE_STORAGE_BUCKET = 'ordernpickapp.firebasestorage.app'
FIREBASE_CREDS_PATH = 'firebase-credentials.json'
STORAGE_FOLDER = 'SentimentAnalysis'
LOCAL_MODEL_DIR = 'cached_model'

# Required model files
REQUIRED_FILES = ['config.json', 'model.safetensors', 'tokenizer.json', 
                  'tokenizer_config.json', 'special_tokens_map.json', 'vocab.txt']

# Global variables
model = None
tokenizer = None
sentiment_pipeline = None

def get_firebase_credentials():
    """Get Firebase credentials from file or environment variable"""
    # Try environment variable first (for production)
    creds_json = os.environ.get('FIREBASE_CREDENTIALS')
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            return credentials.Certificate(creds_dict)
        except Exception as e:
            print(f"✗ Error parsing FIREBASE_CREDENTIALS env var: {e}")
    
    # Fall back to local file (for development)
    if os.path.exists(FIREBASE_CREDS_PATH):
        return credentials.Certificate(FIREBASE_CREDS_PATH)
    
    raise Exception("No Firebase credentials found. Set FIREBASE_CREDENTIALS env var or provide firebase-credentials.json")

def initialize_firebase():
    """Initialize Firebase"""
    try:
        if not firebase_admin._apps:
            cred = get_firebase_credentials()
            firebase_admin.initialize_app(cred, {'storageBucket': FIREBASE_STORAGE_BUCKET})
        print("✓ Firebase initialized")
        return True
    except Exception as e:
        print(f"✗ Firebase error: {e}")
        return False

def download_model_from_firebase():
    """Download model files from Firebase Storage"""
    try:
        print("\n=== Downloading Model ===")
        os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
        
        if not initialize_firebase():
            return False
        
        bucket = storage.bucket()
        
        for filename in REQUIRED_FILES:
            remote_path = f"{STORAGE_FOLDER}/{filename}"
            local_path = os.path.join(LOCAL_MODEL_DIR, filename)
            print(f"  Downloading {filename}...")
            blob = bucket.blob(remote_path)
            blob.download_to_filename(local_path)
            print(f"  ✓ {filename}")
        
        print("✓ All files downloaded\n")
        return True
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return False

def load_resources():
    """Load model and tokenizer"""
    global model, tokenizer, sentiment_pipeline
    
    try:
        print("\n=== Loading Model ===")
        
        # Download if needed
        if not os.path.exists(LOCAL_MODEL_DIR) or len(os.listdir(LOCAL_MODEL_DIR)) < len(REQUIRED_FILES):
            print("Downloading from Firebase...")
            if not download_model_from_firebase():
                print("⚠ Using dummy predictions")
                return
        else:
            print("Using cached model...")
        
        # Load model
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_DIR)
        print("✓ Tokenizer loaded")
        
        print("Loading model...")
        model = AutoModelForSequenceClassification.from_pretrained(LOCAL_MODEL_DIR)
        print("✓ Model loaded")
        
        print("Creating pipeline...")
        sentiment_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, device=-1)
        print("✓ Pipeline ready")
        
        print("=== Ready! ===\n")
    except Exception as e:
        print(f"✗ Loading error: {e}")
        sentiment_pipeline = None

def predict_sentiment(text):
    """Predict sentiment"""
    if sentiment_pipeline is None:
        return {'sentiment': 'neutral', 'confidence': 0.5, 'scores': {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33}}
    
    try:
        result = sentiment_pipeline(text)[0]
        label = result['label'].lower()
        confidence = result['score']
        
        # Map labels
        sentiment_map = {
            'positive': 'positive', 'pos': 'positive', 'label_2': 'positive', '2': 'positive',
            'negative': 'negative', 'neg': 'negative', 'label_0': 'negative', '0': 'negative',
            'neutral': 'neutral', 'neu': 'neutral', 'label_1': 'neutral', '1': 'neutral'
        }
        
        sentiment = sentiment_map.get(label, 'neutral')
        
        scores = {'negative': 0.0, 'neutral': 0.0, 'positive': 0.0}
        scores[sentiment] = confidence
        remaining = (1.0 - confidence) / 2
        for s in scores:
            if s != sentiment:
                scores[s] = remaining
        
        return {'sentiment': sentiment, 'confidence': float(confidence), 'scores': scores}
    except Exception as e:
        return {'sentiment': 'neutral', 'confidence': 0.0, 'error': str(e)}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'pipeline_ready': sentiment_pipeline is not None
    })

@app.route('/api/analyze-sentiment', methods=['POST'])
def analyze_sentiment():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required field: text'}), 400
        
        review_text = data['text']
        if not review_text or len(review_text.strip()) == 0:
            return jsonify({'error': 'Review text cannot be empty'}), 400
        
        result = predict_sentiment(review_text)
        return jsonify({'success': True, 'data': result, 'original_text': review_text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    try:
        data = request.get_json()
        if not data or 'reviews' not in data:
            return jsonify({'error': 'Missing required field: reviews'}), 400
        
        reviews = data['reviews']
        if not isinstance(reviews, list):
            return jsonify({'error': 'Reviews must be a list'}), 400
        
        results = []
        for review in reviews:
            if 'text' in review and review['text']:
                sentiment_result = predict_sentiment(review['text'])
                results.append({'id': review.get('id', None), 'sentiment': sentiment_result})
        
        return jsonify({'success': True, 'count': len(results), 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Load model when app starts (for production)
load_resources()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
