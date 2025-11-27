# 🚀 Deployment Guide - AI Travel Planner

## ⚠️ Important: Deployment Architecture

Your app has **2 parts**:
1. **Streamlit UI** (travel_ui.py) - The frontend
2. **4 FastAPI Agents** (flight, stay, activities, host) - The backend

**Streamlit Cloud can only host the Streamlit UI**, not the FastAPI agents.

---

## 🎯 Deployment Options

### **Option 1: Full Deployment (Recommended for Production)**

Deploy the **entire multi-agent system** with UI + Backend:

**Frontend (Streamlit UI):**
- Deploy to **Streamlit Cloud** (free)

**Backend (4 Agents):**
- Deploy to **Railway**, **Render**, or **Google Cloud Run**
- Each agent runs as a separate service
- Update UI to point to deployed agent URLs

**Cost:** ~$5-20/month for backend hosting

---

### **Option 2: Streamlit Cloud Only (Demo/Simplified)**

Create a **standalone version** that runs everything in Streamlit:
- Combines all agents into the Streamlit app
- No separate backend needed
- Simpler but less scalable

**Cost:** Free on Streamlit Cloud

---

### **Option 3: Local Development Only**

Keep running locally with `./start_agents.sh`
- Best for development and testing
- No deployment needed

---

## 📋 **Which Option Do You Want?**

I recommend **Option 1** for a professional deployment, but **Option 2** is easier if you just want a quick demo online.

Let me know which option you prefer, and I'll guide you through the deployment! 🚀

---

## 🔧 Option 1: Full Deployment Steps

### Step 1: Deploy Backend Agents (Railway Example)

1. **Sign up for Railway**: https://railway.app
2. **Create a new project**
3. **Deploy each agent**:
   ```bash
   # Host Agent
   railway up --service host-agent
   
   # Flight Agent  
   railway up --service flight-agent
   
   # Stay Agent
   railway up --service stay-agent
   
   # Activities Agent
   railway up --service activities-agent
   ```

4. **Set environment variables**:
   - `GOOGLE_API_KEY` = your Google API key
   - `PORT` = 8000 (host), 8001 (flight), etc.

5. **Get the deployed URLs**:
   - Each service will get a URL like: `https://host-agent-production.up.railway.app`

### Step 2: Update Streamlit UI

Update `travel_ui.py` to use deployed agent URLs:

```python
# Instead of localhost
AGENT_URL = "https://host-agent-production.up.railway.app/run"

response = requests.post(AGENT_URL, json=payload, timeout=120)
```

### Step 3: Deploy Streamlit UI

1. **Push code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/travel-planner.git
   git push -u origin main
   ```

2. **Go to Streamlit Cloud**: https://share.streamlit.io
3. **Click "New app"**
4. **Connect your GitHub repo**
5. **Set secrets** (Settings → Secrets):
   ```toml
   GOOGLE_API_KEY = "your-google-api-key"
   ```
6. **Deploy!**

---

## 🎨 Option 2: Streamlit-Only Deployment

I can create a simplified version (`travel_ui_standalone.py`) that:
- Runs all AI logic directly in Streamlit
- No separate backend needed
- Works on Streamlit Cloud's free tier

Would you like me to create this standalone version?

---

## 📊 Cost Comparison

| Option | Frontend | Backend | Total/Month |
|--------|----------|---------|-------------|
| **Option 1** | Free (Streamlit Cloud) | $5-20 (Railway/Render) | $5-20 |
| **Option 2** | Free (Streamlit Cloud) | N/A | $0 |
| **Option 3** | Local | Local | $0 |

---

## 🤔 My Recommendation

For a **portfolio/demo**: Use Option 2 (Streamlit-only)
For **production**: Use Option 1 (Full deployment)
For **development**: Use Option 3 (Local)

**What would you like to do?** 😊
