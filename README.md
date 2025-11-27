# ✈️ AI-Powered Travel Planner

<div align="center">

![Travel Planner](https://img.shields.io/badge/AI-Travel%20Planner-purple?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.51+-red?style=for-the-badge&logo=streamlit)
![Google ADK](https://img.shields.io/badge/Google-ADK-green?style=for-the-badge&logo=google)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A beautiful AI-powered multi-agent travel planning system built with Google's Agent Development Kit (ADK) and Gemini 2.0**

[Live Demo](https://deepak338-ai-powered-travel-planner.streamlit.app) • [Documentation](#documentation) • [Quick Start](#quick-start)

</div>

---

## 🌟 Features

- 🤖 **Multi-Agent AI System** - Specialized agents for flights, hotels, and activities
- 🎨 **Beautiful UI** - Modern gradient design with smooth animations
- ⚡ **Fast & Efficient** - Parallel agent execution for quick results
- 🔗 **Functional Booking Links** - Direct links to Google Flights, Booking.com, and search results
- 🌐 **100% Free Deployment** - Runs on Streamlit Cloud at zero cost
- 🔐 **Secure** - API keys stored in secrets, never committed to git

---

## 🎯 Demo

### Live Application
👉 **[Try it now!](https://deepak338-ai-powered-travel-planner.streamlit.app)**


---

## 🚀 Quick Start

### Option 1: Try Online (Instant)

Visit the live demo: **[AI Travel Planner](https://deepak338-ai-powered-travel-planner.streamlit.app)**

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://github.com/deepak338/AI-Powered-travel-planner.git
cd AI-Powered-travel-planner

# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp .example_env .env
# Edit .env and add your Google API key

# Run the app
streamlit run app.py
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│          Streamlit UI (app.py)              │
│      Beautiful Purple Gradient Interface    │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         Multi-Agent Orchestrator             │
│     (Parallel Execution with asyncio)        │
└─┬──────────────┬──────────────┬─────────────┘
  │              │              │
  ▼              ▼              ▼
┌─────────┐  ┌─────────┐  ┌──────────┐
│ Flight  │  │  Stay   │  │Activities│
│  Agent  │  │  Agent  │  │  Agent   │
└────┬────┘  └────┬────┘  └────┬─────┘
     │            │            │
     ▼            ▼            ▼
┌─────────────────────────────────────┐
│      Google Gemini 2.0 Flash        │
│    (AI-Powered Recommendations)     │
└─────────────────────────────────────┘
```

### How It Works

1. **User Input** - Enter travel details (origin, destination, dates, budget)
2. **Multi-Agent Processing** - 3 AI agents work in parallel:
   - 🛫 **Flight Agent** - Finds best flight options
   - 🏨 **Stay Agent** - Recommends hotels within budget
   - 🗺️ **Activities Agent** - Suggests tourist activities
3. **AI-Powered Results** - Gemini 2.0 generates personalized recommendations
4. **Beautiful Display** - Results shown in elegant cards with booking links

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| **Google ADK** | Agent Development Kit for building AI agents |
| **Gemini 2.0 Flash** | Fast, cost-effective AI model |
| **Streamlit** | Web UI framework |
| **Python 3.11+** | Programming language |
| **asyncio** | Parallel agent execution |

---

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Deployment Guide](STREAMLIT_DEPLOY.md)** - Deploy to Streamlit Cloud
- **[Next Steps](NEXT_STEPS.md)** - What to do after setup
- **[Test Report](TEST_REPORT.md)** - Comprehensive testing results

---

## 🎨 UI Features

- ✨ **Modern Design** - Purple gradient background inspired by Instagram
- 🎯 **Responsive Layout** - Works on desktop, tablet, and mobile
- 💫 **Smooth Animations** - Cards lift and scale on hover
- 🔗 **Working Buttons** - All "Search" buttons link to real booking sites
- 📱 **Clean Typography** - Poppins font for modern look

---

## 💰 Cost

**Development & Deployment: $0**

- Streamlit Cloud hosting: FREE
- Google API usage: ~$0.003 per trip plan
- No credit card required for basic usage

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
GOOGLE_API_KEY=your-google-api-key-here
```

Get your API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

### Streamlit Secrets

For deployment, add to Streamlit Cloud secrets:

```toml
GOOGLE_API_KEY = "your-google-api-key-here"
```

---

## 📊 Project Structure

```
AI-Powered-travel-planner/
├── app.py                   # Main Streamlit app (standalone)
├── requirements.txt         # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── .gitignore              # Git ignore rules
├── .example_env            # Environment template
├── README.md               # This file
├── QUICKSTART.md           # Quick start guide
├── STREAMLIT_DEPLOY.md     # Deployment instructions
├── NEXT_STEPS.md           # Post-setup guide
└── TEST_REPORT.md          # Test results

# Optional (for local multi-agent setup):
├── agents/                 # Individual agent modules
├── common/                 # Shared utilities
├── shared/                 # Shared schemas
└── travel_ui.py           # UI for multi-agent setup
```

---

## 🚀 Deployment

### Deploy to Streamlit Cloud (Free)

1. **Push to GitHub** (you're here!)
2. **Go to** [Streamlit Cloud](https://share.streamlit.io)
3. **Click** "New app"
4. **Select** your repository
5. **Set** main file to `app.py`
6. **Add** Google API key to secrets
7. **Deploy!** 🎉

Full instructions: [STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)

---

## 🧪 Testing

All agents tested and working! ✅

- ✅ Flight recommendations
- ✅ Hotel suggestions  
- ✅ Activity recommendations
- ✅ Parallel execution
- ✅ UI rendering
- ✅ Booking links

See full test report: [TEST_REPORT.md](TEST_REPORT.md)

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🐛 Known Issues & Roadmap

### Known Issues
- First load may take 10-20 seconds (cold start)
- JSON responses sometimes wrapped in code fences (handled automatically)

### Roadmap
- [ ] Add real-time flight price tracking
- [ ] Integrate actual booking APIs (Amadeus, Booking.com)
- [ ] Add user authentication
- [ ] Save and share trip plans
- [ ] Add weather forecasts
- [ ] Multi-language support
- [ ] Mobile app version

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Deepak Kumar**

- GitHub: [@deepak338](https://github.com/deepak338)
- Project: [AI-Powered Travel Planner](https://github.com/deepak338/AI-Powered-travel-planner)

---

## 🙏 Acknowledgments

- [Google ADK](https://github.com/google/adk) - Agent Development Kit
- [Streamlit](https://streamlit.io) - Amazing UI framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) - Powerful AI model
- Inspired by modern travel planning apps

---

## 📞 Support

- 📧 Email: deepakthedev@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/deepak338/AI-Powered-travel-planner/issues)


---

