# 🚀 Quick Start - Model from Firebase Storage

## Step-by-Step (5 minutes)

### 1️⃣ Get Firebase Credentials (2 min)

```
1. Open: https://console.firebase.google.com
2. Select project: OrderNpick
3. Settings ⚙️ → Project Settings → Service Accounts
4. Click: "Generate New Private Key"
5. Save as: firebase-credentials.json
6. Move to: emotion_api/ folder
```

### 2️⃣ Update Configuration (1 min)

Edit `emotion_api/app.py` line 16:

```python
FIREBASE_STORAGE_BUCKET = 'ordernpick.appspot.com'  # Your project ID
```

Find your project ID:

- Firebase Console → Project Settings → Project ID

### 3️⃣ Install Dependencies (1 min)

```bash
cd emotion_api
pip install -r requirements.txt
```

### 4️⃣ Test Connection (30 sec)

```bash
python test_firebase_storage.py
```

Should see:

```
✅ ALL TESTS PASSED!
```

### 5️⃣ Start API (30 sec)

```bash
python app.py
```

Should see:

```
✓ Model loaded successfully
✓ Tokenizer loaded successfully
=== Ready to accept requests! ===
```

### 6️⃣ Update Flutter App

Get your IP:

```bash
ipconfig   # Windows (look for IPv4)
ifconfig   # Mac/Linux (look for inet)
```

Edit `lib/data/services/sentiment_analysis_service.dart` line 6:

```dart
static const String baseUrl = 'http://YOUR_IP:5000';
```

Example: `http://192.168.1.100:5000`

### 7️⃣ Test!

```bash
flutter run
# Go to: Nearest Stores → Review → Preview Sentiment
```

## 🎯 Your Model Files in Firebase Storage

Make sure these exist:

```
Firebase Storage/
└── SentimentalAnalysis/
    ├── emotion_model.h5    ← Your model
    └── tokenizer.pkl       ← Your tokenizer
```

**If filenames are different**, update `app.py` lines 66-71.

## ⚠️ Troubleshooting

| Error                                 | Fix                                     |
| ------------------------------------- | --------------------------------------- |
| `firebase-credentials.json not found` | Download from Firebase Console          |
| `Module 'tensorflow' not found`       | Run `pip install tensorflow`            |
| `File does not exist in Storage`      | Check Firebase Storage folder/filenames |
| `Connection refused` in Flutter       | Check IP address, same WiFi network     |

## 📞 Quick Test Commands

**Test API is running:**

```bash
curl http://localhost:5000/health
```

**Test sentiment analysis:**

```bash
curl -X POST http://localhost:5000/api/analyze-sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "Great service!"}'
```

## 📖 Full Documentation

See `COMPLETE_SETUP_GUIDE.md` for detailed instructions and deployment options.

## ✅ Checklist

- [ ] Downloaded `firebase-credentials.json`
- [ ] Updated project ID in `app.py`
- [ ] Installed Python dependencies
- [ ] Ran `test_firebase_storage.py` successfully
- [ ] Started API server
- [ ] Updated Flutter with correct IP
- [ ] Tested review submission

Done! 🎉
