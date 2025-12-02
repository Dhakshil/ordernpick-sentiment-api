# Emotion Detection API

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd emotion_api
pip install -r requirements.txt
```

### 2. Add Your Model Files

Place your trained model files in this directory:

- `emotion_model.h5` - Your Keras/TensorFlow model
- `tokenizer.pkl` - Your trained tokenizer

If you're using a different format (PyTorch, scikit-learn), update the `load_resources()` function in `app.py`.

### 3. Configure Model Path

Edit `app.py` and update these paths:

```python
MODEL_PATH = 'emotion_model.h5'  # Your model file
TOKENIZER_PATH = 'tokenizer.pkl'  # Your tokenizer file
max_length = 100  # Max sequence length used during training
```

### 4. Run the API Server

**Development:**

```bash
python app.py
```

**Production (using gunicorn):**

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 5. Test the API

**Health Check:**

```bash
curl http://localhost:5000/health
```

**Single Review Analysis:**

```bash
curl -X POST http://localhost:5000/api/analyze-sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "The food was amazing and service was excellent!"}'
```

**Batch Analysis:**

```bash
curl -X POST http://localhost:5000/api/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "reviews": [
      {"id": "1", "text": "Great experience!"},
      {"id": "2", "text": "Terrible service"}
    ]
  }'
```

## API Endpoints

### POST `/api/analyze-sentiment`

Analyze single review text

**Request:**

```json
{
  "text": "Review text here"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "sentiment": "positive",
    "confidence": 0.92,
    "scores": {
      "negative": 0.02,
      "neutral": 0.06,
      "positive": 0.92
    }
  },
  "original_text": "Review text here"
}
```

### POST `/api/batch-analyze`

Analyze multiple reviews

**Request:**

```json
{
  "reviews": [
    { "id": "review1", "text": "Great!" },
    { "id": "review2", "text": "Bad experience" }
  ]
}
```

### GET `/health`

Check API health status

## Deployment

### Local Network Access

- Find your machine's IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Access from Flutter: `http://YOUR_IP:5000/api/analyze-sentiment`

### Cloud Deployment Options

- **Railway**: Easy deployment, free tier available
- **Render**: Free tier for APIs
- **AWS EC2**: Full control
- **Google Cloud Run**: Serverless option
- **Heroku**: Simple deployment

## Notes

- The API includes CORS support for Flutter apps
- Default port is 5000 (change in `app.py` if needed)
- For production, use a proper WSGI server (gunicorn, uWSGI)
- Consider adding authentication for production use
