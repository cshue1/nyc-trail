# Gemini AI Setup Guide for NYC Trail Planner

## Quick Setup

### Option 1: Using Environment Variables (.env file) - Easiest

1. **Get your Gemini API Key**
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Click "Create API Key"
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

## API Models

The app uses:
- **Primary**: `gemini-1.5-flash` (via Google Generative AI SDK)
- **Fallback**: `gemini-2.5-flash` (via REST API if SDK unavailable)

Both models are optimized for cost and speed.

## Troubleshooting

### "Gemini API not configured"
- Check your `.env` file has `GEMINI_API_KEY`
- Verify the API key is valid at [Google AI Studio](https://aistudio.google.com/app/apikey)
- Restart the Streamlit app

### "Gemini initialization failed"
- Check the Streamlit sidebar for error details
- Verify `google-generativeai` is installed: `pip install google-generativeai`
- Try using REST API instead by removing the SDK

### Missions not getting enhanced
- Check sidebar status indicator
- Gemini enhancement might fail due to rate limits - the app falls back to local generation
- Wait a moment and try again

## API Cost

Google Generative AI has a **free tier**:
- Up to 15 requests per minute
- Up to 1,500 requests per day
- Perfect for testing and personal use

Paid plans available for higher usage.

## Features

✅ **Mission Enhancement** - AI-powered descriptive mission generation
✅ **Geographic Awareness** - Contextual missions for each NYC neighborhood  
✅ **Fallback Logic** - Works without API key (uses local generation)
✅ **Error Handling** - Gracefully degrades if API is unavailable
✅ **Caching** - Reduces API calls with smart caching

---

For more info: [Google AI Studio Docs](https://ai.google.dev/docs)
