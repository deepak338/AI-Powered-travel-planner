# 🚀 Deploy to Streamlit Cloud - Quick Guide

## ✅ Prerequisites

1. **GitHub Account** - Create one at https://github.com
2. **Streamlit Cloud Account** - Sign up at https://share.streamlit.io (use your GitHub account)
3. **Google API Key** - Get it from https://makersuite.google.com/app/apikey

---

## 📤 Step 1: Push to GitHub

```bash
# Make sure you're in the project directory
cd "/Users/deepakkumar/Desktop/deepak_folder/AI-Powered Travel Planner"

# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-travel-planner.git
git branch -M main
git push -u origin main
```

**Important:** The `.env` file with your real API key will NOT be pushed (it's in `.gitignore`)

---

## 🌐 Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud:** https://share.streamlit.io

2. **Click "New app"**

3. **Fill in the details:**
   - Repository: `YOUR_USERNAME/ai-travel-planner`
   - Branch: `main`
   - Main file path: `app.py`

4. **Click "Advanced settings"** 

5. **Add your secrets** in the Secrets section:
   ```toml
   GOOGLE_API_KEY = "your-actual-google-api-key-here"
   ```
   
   ⚠️ **Important:** Replace with your REAL Google API key!

6. **Click "Deploy"**

7. **Wait 2-3 minutes** for deployment to complete

8. **Your app will be live at:** `https://YOUR_USERNAME-ai-travel-planner.streamlit.app`

---

## 🎉 That's It!

Your AI Travel Planner is now live and accessible to anyone with the link!

---

## 🔧 Updating Your App

To update your deployed app:

```bash
# Make changes to your code
git add .
git commit -m "Update: description of changes"
git push origin main
```

Streamlit will automatically redeploy your app! 🚀

---

## 📊 What Got Deployed?

✅ Beautiful purple gradient UI
✅ AI-powered travel recommendations
✅ Flights, hotels, and activities search
✅ Working "Book Now" buttons
✅ Fully responsive design

---

## 💰 Cost

**$0** - Completely FREE on Streamlit Cloud!

---

## 🆘 Troubleshooting

### "Module not found" error
- Check that `requirements.txt` is in your repo
- Make sure all packages are listed correctly

### "API Key not found" error
- Go to your app settings on Streamlit Cloud
- Click "Secrets" and add your `GOOGLE_API_KEY`
- Reboot the app

### App is slow
- First load takes 10-20 seconds (normal)
- After first load, agents are cached and it's faster

---

## 📱 Share Your App!

Once deployed, share your link:
- `https://YOUR_USERNAME-ai-travel-planner.streamlit.app`

Add it to your:
- Portfolio
- Resume
- LinkedIn
- GitHub README

---

**Need help?** Check the official guide: https://docs.streamlit.io/streamlit-community-cloud/get-started
