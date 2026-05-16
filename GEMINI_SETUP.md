# Gemini AI Setup Guide for NYC Trail Planner

## ✅ 100% FREE - No Payment Required

This app uses only **FREE-TIER Gemini models**. No credit card, no paid plans!

- **Limits:** Up to 15 requests/minute, 1,500 requests/day
- **Cost:** $0 (completely free)
- **Perfect for:** Personal projects, testing, light usage

## Quick Setup

### Option 1: Using Environment Variables (.env file) - Easiest

1. **Get your FREE Gemini API Key**
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Click "Create API Key" 
   - **No credit card needed** - completely free
   - Copy the key

2. **Create a .env file**
   - Copy `.env.example` to `.env`
   - Replace `your_api_key_here` with your actual key
   ```
   GEMINI_API_KEY=sk-xxxxxxxxxxxxx
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

### Option 2: Using Streamlit Secrets (For Deployment)

1. Create `.streamlit/secrets.toml` in your project:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```

2. Run the app normally:
   ```bash
   streamlit run app.py
   ```

## What Gemini Does

When enabled, Gemini AI:

- 🎯 **Enhances missions** with geographically accurate descriptions for NYC neighborhoods
- 🤖 **Maintains tone** - keeps the cyberpunk/tactical terminal aesthetic
- 📍 **Geographic constraints** - ensures missions are possible for the selected neighborhood
- 🍽️ **Dietary compliance** - maintains pescatarian (no avocado) requirements for EAT missions
- 📸 **Action focus** - ensures WALK missions are about movement/photography, EAT is about dining, CHILL is about resting

## Free-Tier Models Used

The app uses these **FREE-TIER models** in order of preference:

1. **gemini-2.0-flash** (newest, recommended)
2. **gemini-1.5-flash** (fast, reliable fallback)
3. **gemini-pro** (stable older model)

All are completely **FREE** with the tier limits above.

## Troubleshooting

### "Gemini API not configured"
- Check your `.env` file has `GEMINI_API_KEY`
- Verify the API key is valid at [Google AI Studio](https://aistudio.google.com/app/apikey)
- Restart the Streamlit app

### "Gemini initialization failed"
- Check the Streamlit sidebar for error details
- Verify `google-generativeai` is installed: `pip install google-generativeai`
- Try updating: `pip install --upgrade google-generativeai`

### Missions not getting enhanced
- Check sidebar status indicator
- Gemini enhancement might fail due to rate limits - the app falls back to local generation
- Wait a moment and try again (free tier: 15 requests/minute max)

### Rate Limited (Too Many Requests)
- Free tier limits: 15 requests/minute, 1,500/day
- The app automatically falls back to local generation when rate-limited
- No cost - just use local generation for a while

## Cost

### Free Tier (Recommended for this app)
- **Cost:** $0
- **Limits:** 15 req/min, 1,500 req/day
- **Models:** All models supported

### Paid Tiers (Optional, not needed)
- **Cost:** $0.075 per 1M input tokens, $0.30 per 1M output tokens
- **For comparison:** This app uses ~200-300 tokens per enhancement
- **Rough cost:** ~$0.00002 per enhancement (less than a fraction of a penny)

**Bottom line:** Stick with the free tier! No payment needed.

## Features

✅ **Mission Enhancement** - AI-powered descriptive mission generation
✅ **Geographic Awareness** - Contextual missions for each NYC neighborhood  
✅ **Fallback Logic** - Works without API key (uses local generation)
✅ **Error Handling** - Gracefully degrades if API is unavailable or rate-limited
✅ **Caching** - Reduces API calls with smart caching (1 hour TTL)

---

For more info: [Google AI Studio Docs](https://ai.google.dev/docs)
