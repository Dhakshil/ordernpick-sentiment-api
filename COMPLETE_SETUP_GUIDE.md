# Complete Guide: Using Your Model from Firebase Storage

## 🎯 What This Does

Your sentiment analysis model is stored in Firebase Storage. This guide shows you how to:

1. Create a REST API that downloads your model from Firebase
2. Deploy it (locally or cloud)
3. Connect it to your Flutter app

## 📋 Prerequisites

- ✅ Model files uploaded to Firebase Storage under `SentimentalAnalysis/`
- ✅ Python 3.8+ installed
- ✅ Firebase project with Storage enabled

## 🚀 Setup Steps

### Step 1: Get Firebase Service Account Key

1. Open Firebase Console: https://console.firebase.google.com
2. Select your project: **OrderNpick**
3. Click ⚙️ (Settings) → **Project Settings**
4. Go to **Service Accounts** tab
5. Click **Generate New Private Key**
6. Save the downloaded JSON file as `firebase-credentials.json`
7. Move it to the `emotion_api` folder

```bash
# Your folder structure should look like:
emotion_api/
├── app.py
├── requirements.txt
├── firebase-credentials.json  ← Add this
└── README.md
```

### Step 2: Update Configuration

Edit `emotion_api/app.py` lines 16-18:

```python
# Line 16: Your Firebase project ID
FIREBASE_STORAGE_BUCKET = 'ordernpick.appspot.com'  # Change 'ordernpick' to your actual project ID

# Line 18: Your Firebase Storage folder (already correct if you used 'SentimentalAnalysis')
STORAGE_FOLDER = 'SentimentalAnalysis'

# Line 26: Max sequence length from your model training
max_length = 100  # Change to match your model
```

**To find your project ID:**

- Firebase Console → Project Settings → General → Project ID

### Step 3: Verify Your Firebase Storage Files

Make sure these files exist in Firebase Storage:

1. Go to Firebase Console → Storage
2. Navigate to `SentimentalAnalysis/` folder
3. Verify these files exist:
   - `emotion_model.h5` (or your model filename)
   - `tokenizer.pkl` (or your tokenizer filename)

**If your filenames are different**, update lines 66-70 in `app.py`:

```python
# Line 66: Your model filename
model_remote_path = f"{STORAGE_FOLDER}/your_model_name.h5"

# Line 71: Your tokenizer filename
tokenizer_remote_path = f"{STORAGE_FOLDER}/your_tokenizer_name.pkl"
```

### Step 4: Install Python Dependencies

```bash
cd emotion_api
pip install -r requirements.txt
```

This will install:

- Flask (web server)
- TensorFlow (model loading)
- firebase-admin (Firebase Storage access)
- flask-cors (allow Flutter to call API)

### Step 5: Run the API Server

```bash
python app.py
```

**What happens:**

1. API starts up
2. Checks if model exists locally
3. If not, downloads from Firebase Storage
4. Caches model locally (faster next time)
5. Starts accepting requests on port 5000

**Expected output:**

```
=== Loading Model Resources ===
Model files not found locally, downloading from Firebase Storage...
✓ Firebase initialized successfully
  Downloading SentimentalAnalysis/emotion_model.h5...
  ✓ Downloaded to cached_emotion_model.h5
  Downloading SentimentalAnalysis/tokenizer.pkl...
  ✓ Downloaded to cached_tokenizer.pkl
Loading model...
✓ Model loaded successfully
Loading tokenizer...
✓ Tokenizer loaded successfully
=== Ready to accept requests! ===

 * Running on http://0.0.0.0:5000
```

### Step 6: Test the API

**Test 1: Health Check**

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "tokenizer_loaded": true
}
```

**Test 2: Analyze Sentiment**

```bash
curl -X POST http://localhost:5000/api/analyze-sentiment \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"The service was excellent and food was delicious!\"}"
```

Expected response:

```json
{
  "success": true,
  "data": {
    "sentiment": "positive",
    "confidence": 0.89,
    "scores": {
      "negative": 0.05,
      "neutral": 0.06,
      "positive": 0.89
    }
  },
  "original_text": "The service was excellent and food was delicious!"
}
```

### Step 7: Connect Flutter App

**Get your computer's IP address:**

**Windows:**

```bash
ipconfig
```

Look for "IPv4 Address" under your active network adapter.

**Mac/Linux:**

```bash
ifconfig
```

Look for "inet" address.

Example: `192.168.1.100`

**Update Flutter app:**

Edit `lib/data/services/sentiment_analysis_service.dart` line 6:

```dart
static const String baseUrl = 'http://192.168.1.100:5000';  // Your IP here
```

### Step 8: Test in Flutter

1. Make sure API is running (`python app.py`)
2. Make sure phone and computer are on **same WiFi network**
3. Hot reload Flutter app (`r` in terminal)
4. Go to "Nearest Stores" → tap any store → tap "Review"
5. Write a review → tap "Preview Sentiment"
6. You should see AI analysis appear!

## 🌐 Deployment Options

### Option A: Local Development (Current Setup)

✅ **Pros:** Free, easy, fast testing  
❌ **Cons:** Only works on your WiFi, computer must be on

**Keep using:** `http://YOUR_IP:5000`

---

### Option B: Deploy to Railway (Recommended for Production)

Railway provides free hosting with easy deployment.

**Steps:**

1. Create account: https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variables in Railway dashboard
5. Railway will auto-deploy your API
6. Get your public URL: `https://your-app.railway.app`

**Update Flutter:**

```dart
static const String baseUrl = 'https://your-app.railway.app';
```

**Cost:** Free tier includes 500 hours/month ($5/month after)

---

### Option C: Google Cloud Run (Best for Scale)

Serverless, auto-scales, only pay when used.

**Steps:**

1. Install Google Cloud SDK
2. Create Dockerfile:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

3. Deploy:

```bash
gcloud run deploy sentiment-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

4. Get your URL: `https://sentiment-api-xxxxx.run.app`

**Cost:** Free tier: 2 million requests/month

---

### Option D: Render (Easy Alternative)

Similar to Railway, very easy deployment.

**Steps:**

1. Create account: https://render.com
2. New → Web Service → Connect repository
3. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`
5. Add environment variables
6. Deploy

**Cost:** Free tier available

## 🔒 Security Best Practices

### 1. Secure Your Firebase Credentials

**DO NOT commit `firebase-credentials.json` to Git!**

Add to `.gitignore`:

```
emotion_api/firebase-credentials.json
emotion_api/cached_*.h5
emotion_api/cached_*.pkl
```

### 2. Add API Authentication

For production, add API key authentication:

```python
# In app.py
API_KEY = os.getenv('API_KEY', 'your-secret-key')

@app.before_request
def check_auth():
    if request.endpoint != 'health':
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
```

Update Flutter:

```dart
final response = await http.post(
  Uri.parse('$baseUrl/api/analyze-sentiment'),
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-secret-key',
  },
  body: jsonEncode({'text': reviewText}),
);
```

### 3. Rate Limiting

Install Flask-Limiter:

```bash
pip install Flask-Limiter
```

Add to app.py:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/analyze-sentiment', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_sentiment():
    # ... existing code
```

## 🐛 Troubleshooting

### Error: "firebase-credentials.json not found"

**Solution:** Download service account key from Firebase Console

### Error: "Module 'tensorflow' not found"

**Solution:**

```bash
pip install tensorflow==2.15.0
```

### Error: "Model download failed"

**Solution:**

1. Check Firebase Storage rules allow read access
2. Verify file paths match exactly (case-sensitive!)
3. Check Firebase credentials are valid

### Error: "Connection refused" from Flutter

**Solution:**

1. Check API is running: `curl http://localhost:5000/health`
2. Phone and computer on same WiFi?
3. Use correct IP address (not localhost!)
4. Windows Firewall blocking port 5000?
   - Control Panel → Windows Defender Firewall
   - Allow port 5000 for Python

### Model predicts poorly

**Solution:**

1. Verify `max_length` in app.py matches training
2. Check text preprocessing matches your training code
3. Test your model separately with sample texts

## 📊 Monitoring

### View API Logs

```bash
# The Flask server prints all requests
# Look for lines like:
"Analyzed: 'Great service!' → positive (0.92)"
```

### View Firebase Storage Usage

- Firebase Console → Storage → Usage tab
- Check download counts and bandwidth

### Track Predictions in Firebase

Add logging to app.py:

```python
from firebase_admin import firestore

db = firestore.client()

def log_prediction(text, sentiment, confidence):
    db.collection('SentimentLogs').add({
        'text': text,
        'sentiment': sentiment,
        'confidence': confidence,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
```

## ✅ Verification Checklist

Before marking this as complete:

- [ ] `firebase-credentials.json` downloaded and in `emotion_api/` folder
- [ ] Firebase Storage bucket name updated in app.py
- [ ] Model and tokenizer filenames verified
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] API server starts without errors
- [ ] Health check returns `"model_loaded": true`
- [ ] Test sentiment analysis returns valid predictions
- [ ] Flutter app updated with correct API URL
- [ ] Phone and computer on same WiFi
- [ ] Review submission works end-to-end
- [ ] Sentiment preview shows correct emotion

## 🎉 Next Steps

Once this is working:

1. **Test thoroughly** with various review texts
2. **Deploy to Railway/Cloud Run** for 24/7 availability
3. **Add authentication** for production security
4. **Monitor predictions** to improve model
5. **Collect user feedback** to retrain model

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Check API logs for specific error messages
4. Ensure Firebase Storage permissions are correct

Your AI sentiment analysis system is now powered by Firebase Storage! 🚀
