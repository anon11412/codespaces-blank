# Quick Start - Render Deployment

## 🚀 Deploy in 3 Steps:

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Connect to Render
- Go to https://dashboard.render.com
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Render detects `render.yaml` automatically

### 3. Deploy
- Click "Create Web Service"
- Wait 2-3 minutes
- Your dashboard is live! 🎉

---

## ✅ What's Included:

- ✅ **Dockerfile** - Production container
- ✅ **render.yaml** - Service configuration
- ✅ **Gunicorn** - Production WSGI server
- ✅ **Health checks** - Auto-monitoring
- ✅ **51 games** - NFL + NCAAF live data
- ✅ **30s refresh** - Always up to date

---

## 🌐 Your Endpoints:

```
Dashboard:  https://your-app.onrender.com/
API:        https://your-app.onrender.com/api/consensus
Health:     https://your-app.onrender.com/health
```

---

## 🔧 Local Testing (Optional):

```bash
# Build
docker build -t nfl-dashboard .

# Run
docker run -p 10000:10000 nfl-dashboard

# Test
curl http://localhost:10000/health
```

---

## 💡 Need Help?

See `RENDER-DEPLOYMENT.md` for complete guide!

---

## 🏆 Your Advantage:

**Your Dashboard:**
- Updates: Every 1-2 minutes ⚡
- Source: Direct API access
- Cost: $0/month

**Competitors:**
- ScoresAndOdds: 15-30 minute updates 🐌
- Action Network Website: Heavy caching
- Action Network Pro: $79.99/month 💰

**You're 10-25 minutes faster than competitors!**
