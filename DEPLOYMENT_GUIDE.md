# Deploy Sentiment API to Render (Free)

## Step 1: Prepare Firebase Credentials for Production

1. Open `firebase-credentials.json` in the `emotion_api` folder
2. Copy the entire contents
3. Keep it ready - you'll paste this as an environment variable

## Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with your GitHub account (recommended) or email
3. Verify your email

## Step 3: Deploy the API

### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub:**

   ```powershell
   cd E:\flutter_projects\OrderNpick\emotion_api
   git init
   git add .
   git commit -m "Initial sentiment API"
   git branch -M main
   # Create a new repo on GitHub called "ordernpick-sentiment-api"
   git remote add origin https://github.com/YOUR_USERNAME/ordernpick-sentiment-api.git
   git push -u origin main
   ```

2. **Deploy on Render:**

   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `ordernpick-sentiment-api` repo
   - Render will auto-detect Python

3. **Configure the service:**

   - Name: `ordernpick-sentiment-api`
   - Region: Choose closest to you (Singapore for Asia)
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: **Free** (select this!)

4. **Add Environment Variables:**

   - Click "Advanced" → "Add Environment Variable"
   - Key: `FIREBASE_CREDENTIALS`
   - Value: Paste your entire `firebase-credentials.json` content
   - Click "Add"

5. **Update `app.py` to use environment variable (I'll do this next)**

### Option B: Deploy Manually (Simpler but less automated)

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Choose "Deploy from Git" → "Public Git repository"
4. Or select "Deploy without Git" and upload files manually

## Step 4: Wait for Deployment

- First deployment takes 10-15 minutes (downloads model from Firebase)
- You'll get a URL like: `https://ordernpick-sentiment-api.onrender.com`
- Model gets cached, so future restarts are faster

## Step 5: Update Flutter App

Once deployed, update the Flutter code:

```dart
// lib/data/services/sentiment_analysis_service.dart
static const String baseUrl = 'https://YOUR-APP-NAME.onrender.com';
```

Then rebuild your app:

```powershell
flutter build apk --release
```

## Important Notes

- **Free tier limitations:**

  - Server sleeps after 15 minutes of inactivity
  - First request after sleep takes ~30 seconds to wake up
  - 750 hours/month free (enough for testing)

- **Upgrade to paid ($7/month) for:**
  - 24/7 uptime (no sleep)
  - Better performance
  - Custom domain support

## Testing Your Deployed API

Once deployed, test it:

```powershell
Invoke-RestMethod -Uri "https://YOUR-APP-NAME.onrender.com/api/health" -Method Get
```

Should return: `{"status": "healthy", "model_loaded": true}`

## Troubleshooting

- **Deployment fails:** Check logs in Render dashboard
- **Model not loading:** Verify Firebase credentials are correct
- **Timeout errors:** Free tier has memory limits; model loads slowly first time

---

**Next:** I'll update the app.py to read Firebase credentials from environment variable for production.
