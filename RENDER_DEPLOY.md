# Quick Start: Deploy to Render in 5 Minutes

## 🚀 Fastest Way (No Git Required)

### 1. Create Account

- Go to https://render.com
- Sign up with Google/GitHub
- Verify email

### 2. Deploy

1. Click **"New +"** → **"Web Service"**
2. Select **"Build and deploy from a Git repository"** → **"Public Git"**
3. Repository URL: Leave blank for now
4. OR click **"Deploy from GitHub"** and connect your account

### 3. Configure

**Service Details:**

- Name: `ordernpick-sentiment-api`
- Region: Singapore (or closest to you)
- Branch: `main`
- Root Directory: (leave empty)

**Build Settings:**

- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

**Plan:**

- Select **Free** tier

### 4. Add Firebase Credentials

1. Click **"Advanced"** button
2. Click **"Add Environment Variable"**
3. Add this variable:
   - **Key:** `FIREBASE_CREDENTIALS`
   - **Value:** Copy-paste entire content of `firebase-credentials.json`

**Example of what to paste:**

```json
{
  "type": "service_account",
  "project_id": "ordernpickapp",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  ...
}
```

### 5. Deploy!

- Click **"Create Web Service"**
- Wait 10-15 minutes for first deployment
- You'll get a URL like: `https://ordernpick-sentiment-api.onrender.com`

---

## 📱 Update Flutter App

Once you have your Render URL:

1. Open `lib/data/services/sentiment_analysis_service.dart`
2. Change:

```dart
static const String baseUrl = 'https://YOUR-APP-NAME.onrender.com';
```

3. Hot reload or rebuild app

---

## ✅ Test Your API

```powershell
# Test health endpoint
Invoke-RestMethod -Uri "https://YOUR-APP-NAME.onrender.com/api/health" -Method Get

# Test sentiment analysis
Invoke-RestMethod -Uri "https://YOUR-APP-NAME.onrender.com/api/analyze-sentiment" -Method Post -ContentType "application/json" -Body '{"text": "The food was amazing!"}'
```

---

## 💡 Tips

- **First request takes 30 sec:** Free tier sleeps after inactivity
- **Check logs:** Render Dashboard → Your Service → Logs
- **Model downloads once:** Cached after first load (~255MB)
- **Upgrade later:** $7/month for 24/7 uptime (no sleep)

---

## 🆘 Troubleshooting

**Deployment fails?**

- Check logs in Render dashboard
- Ensure Firebase credentials are valid JSON

**Model not loading?**

- Verify `FIREBASE_CREDENTIALS` env var is set correctly
- Check Firebase Storage has model files in `SentimentAnalysis/` folder

**Timeout errors?**

- Normal on first request (model loading)
- Subsequent requests should be fast

---

## 🎯 What Happens Next

1. **Model downloads** from Firebase Storage (first time only)
2. **Model loads** into memory (~1-2 minutes)
3. **API becomes ready** for requests
4. **Flutter app** can now call API from anywhere
5. **Show friends** your AI-powered review feature! 🎉

No need to run Python on your laptop anymore!
