# Streamlit Deployment Guide

This guide shows you how to deploy your CV-RAG Streamlit app so employers can interact with your AI resume!

## 🎯 **What This Gives You**

A public URL like: `https://cv-rag-mikemurphy.streamlit.app`

**Perfect for:**
- ✅ Job applications (link in resume/cover letter)
- ✅ LinkedIn "Featured" section
- ✅ Tutorial demonstrations
- ✅ Portfolio showcase
- ✅ "WOW factor" in interviews

---

## 📋 **Quick Overview**

```
User visits Streamlit app
    ↓
Clicks "What AI tutorials has Mike created?"
    ↓
Streamlit sends to: https://flow.imurph.com/webhook/cv-rag-query
    ↓
n8n Workflow 2 processes query
    ↓
Answer appears in Streamlit UI
    ↓
Employer thinks: "This is awesome, let's interview this person!"
```

---

## 🚀 **Option 1: Streamlit Community Cloud (Recommended - FREE)**

Perfect for demos and portfolio projects. Takes 5 minutes.

### Prerequisites

- ✅ GitHub account
- ✅ Your cv-rag repo pushed to GitHub
- ✅ n8n Workflow 2 deployed and active

### Step-by-Step Deployment

**1. Push your code to GitHub**

```bash
cd /Users/mikemurphy/Code/Projects/cv-rag

# If not already a git repo:
git init
git add .
git commit -m "Add CV-RAG Streamlit app"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/cv-rag.git
git branch -M main
git push -u origin main
```

**2. Sign up for Streamlit Community Cloud**

- Go to: https://share.streamlit.io/
- Click "Sign up with GitHub"
- Authorize Streamlit to access your GitHub

**3. Deploy Your App**

- Click "New app"
- Select your repository: `YOUR_USERNAME/cv-rag`
- Branch: `main`
- Main file path: `streamlit/app.py`
- Click "Deploy!"

**4. Configure Secrets**

Streamlit needs your n8n webhook URL, but you don't want it public in GitHub!

- In your deployed app, click "Settings" → "Secrets"
- Add this (in TOML format):

```toml
N8N_WEBHOOK_URL = "https://flow.imurph.com/webhook/cv-rag-query"
```

- Click "Save"

**5. Update Your Code for Streamlit Cloud**

Streamlit Cloud uses a different secrets format. Update `streamlit/app.py`:

```python
# Change this line (around line 93):
webhook_url = os.getenv("N8N_WEBHOOK_URL")

# To this:
try:
    webhook_url = st.secrets.get("N8N_WEBHOOK_URL") or os.getenv("N8N_WEBHOOK_URL")
except:
    webhook_url = os.getenv("N8N_WEBHOOK_URL")
```

Push the change:
```bash
git add streamlit/app.py
git commit -m "Add Streamlit Cloud secrets support"
git push
```

The app will auto-redeploy!

**6. Get Your Public URL**

Your app will be live at:
```
https://cv-rag-YOUR_USERNAME.streamlit.app
```

Copy this URL - this is what you share with employers!

---

## 🏠 **Option 2: Self-Host on Your VPS**

If you want more control or a custom domain.

### Install Streamlit on VPS

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Create a directory for the app
mkdir -p /opt/cv-rag
cd /opt/cv-rag

# Clone your repo
git clone https://github.com/YOUR_USERNAME/cv-rag.git .

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
N8N_WEBHOOK_URL=http://localhost:5678/webhook/cv-rag-query
EOF
```

### Run with systemd (Auto-start on boot)

Create a service file:

```bash
sudo nano /etc/systemd/system/cv-rag-streamlit.service
```

Add this content:

```ini
[Unit]
Description=CV-RAG Streamlit App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/cv-rag
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/streamlit run streamlit/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable cv-rag-streamlit
sudo systemctl start cv-rag-streamlit

# Check status
sudo systemctl status cv-rag-streamlit
```

### Configure Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/cv-rag
```

Add:

```nginx
server {
    listen 80;
    server_name cv.yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/cv-rag /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Add SSL with Let's Encrypt:

```bash
sudo certbot --nginx -d cv.yourdomain.com
```

Your app is now live at: `https://cv.yourdomain.com`

---

## 📝 **Local Testing (Before Deployment)**

Always test locally first!

```bash
cd /Users/mikemurphy/Code/Projects/cv-rag

# Make sure .env has your webhook URL
echo "N8N_WEBHOOK_URL=https://flow.imurph.com/webhook/cv-rag-query" >> .env

# Activate virtual environment
source .venv/bin/activate

# Install Streamlit if needed
pip install streamlit

# Run locally
streamlit run streamlit/app.py
```

Opens at: `http://localhost:8501`

**Test checklist:**
- [ ] Sample questions work
- [ ] Custom questions work
- [ ] Answers are relevant
- [ ] No timeout errors
- [ ] UI looks good
- [ ] Download buttons work (if you have PDFs)

---

## 🎬 **Making Your Tutorial/Demo Video**

Now that you have a deployed app, you can create a killer tutorial!

### Video Structure

**1. Introduction (30 seconds)**
- "Today I'm showing you my AI-powered resume that you can chat with"
- Show the live Streamlit URL

**2. Live Demo (2 minutes)**
- Ask sample questions
- Show real-time answers
- Highlight the tech stack in sidebar

**3. Behind the Scenes (5 minutes)**
- Open n8n at flow.imurph.com
- Show Workflow 1 (document ingestion)
- Show Workflow 2 (query pipeline)
- Explain each node briefly

**4. Architecture Overview (2 minutes)**
- Draw diagram: Streamlit → n8n → Ollama → Postgres
- Explain why you chose each technology

**5. Code Walkthrough (3 minutes)**
- Show Streamlit app.py (briefly)
- Show n8n workflow configurations
- Highlight the AI nodes

**6. Deployment (2 minutes)**
- Show Streamlit Cloud dashboard
- Show n8n running on VPS
- Show Neon Postgres database

**7. Conclusion (30 seconds)**
- "This demonstrates RAG, LangChain, vector databases, self-hosted LLMs"
- "Link to GitHub repo in description"
- Call to action

### Screen Recording Tips

- **Tool**: OBS Studio (free) or Loom
- **Resolution**: 1920x1080
- **Show**: Browser + n8n UI side-by-side
- **Cursor**: Enable cursor highlighting
- **Audio**: Clear microphone, no background noise

---

## 📊 **Analytics & Tracking (Optional)**

Want to know if employers are using your app?

### Add Google Analytics

1. Get tracking ID from Google Analytics
2. Add to `streamlit/app.py`:

```python
# In the <head> section custom CSS
st.markdown("""
    <script async src="https://www.googletagmanager.com/gtag/js?id=YOUR-GA-ID"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'YOUR-GA-ID');
    </script>
""", unsafe_allow_html=True)
```

Track:
- Total visitors
- Questions asked
- Time spent on page

---

## 🔗 **Where to Share Your App**

Once deployed, add the link to:

1. **Resume** - "Interactive AI Resume: [link]"
2. **LinkedIn** - Featured section or About
3. **Cover Letters** - "Try my AI resume at [link]"
4. **GitHub Profile** - Pin the repo
5. **Portfolio Website** - Big CTA button
6. **Email Signature** - "Chat with my AI resume"
7. **Job Applications** - In the "Additional Info" field

---

## 🎯 **Marketing Copy Examples**

**For your resume:**
```
Interactive AI Resume: https://cv-rag.streamlit.app
Try asking: "What's Mike's experience with n8n and RAG systems?"
```

**For LinkedIn:**
```
🤖 I built an AI-powered resume you can chat with!

Ask it anything about my experience with:
• n8n workflow automation
• RAG systems & vector databases
• Self-hosted LLMs (Ollama)
• AI education & tutorials

Try it live: [link]

Built with n8n AI nodes, PostgreSQL+pgvector, Ollama, and Streamlit.
```

**For cover letters:**
```
I've built an interactive AI resume that demonstrates my skills with
RAG systems, n8n automation, and self-hosted LLMs. You can try it at
[link] - ask it anything about my experience!
```

---

## 🐛 **Troubleshooting**

### "N8N_WEBHOOK_URL not set"

**Fix**: Add secrets in Streamlit Cloud settings or .env locally

### "Connection refused"

**Fix**: Make sure n8n Workflow 2 is ACTIVE (not paused)

### "Timeout error"

**Fix**: Check Ollama is running on VPS:
```bash
ssh root@your-vps-ip
systemctl status ollama
```

### "App won't deploy on Streamlit Cloud"

**Fix**: Check requirements.txt includes:
```
streamlit==1.40.2
requests==2.32.3
python-dotenv==1.0.1
```

---

## ✅ **Final Checklist**

Before sharing with employers:

- [ ] n8n Workflow 2 is active and tested
- [ ] Streamlit app deployed and accessible
- [ ] All sample questions return good answers
- [ ] No timeout errors
- [ ] UI looks professional
- [ ] Your contact links work
- [ ] Tested on mobile (Streamlit is responsive!)
- [ ] Analytics set up (optional)
- [ ] Tutorial video recorded (optional)
- [ ] Link added to resume/LinkedIn

---

**You're ready to impress employers with your interactive AI resume!** 🚀

The combination of:
- Deployed Streamlit app (easy to use)
- n8n workflows (shows technical skill)
- Tutorial video (demonstrates communication)
- Open source code (proves competence)

...is a **killer portfolio piece** that will set you apart from other candidates.
