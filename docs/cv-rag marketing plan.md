```bash
ssh root@158.220.127.4
cd /root/cv-rag
git pull origin main
docker compose restart
```

## Steps to Add Resume PDF Download

**1. Create/Export Your Resume PDF**

- Export your resume as a PDF file
- Name it: `Mike_Murphy_Resume.pdf`

**2. Place the PDF in the Correct Location**

```bash
# Copy your PDF to the docs folder
cp /path/to/your/resume.pdf /Users/mikemurphy/Code/Projects/cv-rag/docs/Mike_Murphy_Resume.pdf
```

**3. Verify the File Exists**

```bash
ls -lh /Users/mikemurphy/Code/Projects/cv-rag/docs/Mike_Murphy_Resume.pdf
```

**4. Test Locally (if running Streamlit locally)**

```bash
streamlit run streamlit/app.py
```

- The download button should now show "📄 Download Resume (PDF)" instead of "📄 PDF resume coming soon"

**5. Deploy to Production**

 

**For VPS deployment:**

```bash
# SSH to your VPS
ssh root@158.220.127.4

# Navigate to the cv-rag directory
cd /root/cv-rag

# Copy the PDF to the docs folder on the VPS
# (You can use scp from your local machine or git if you add it to the repo)
```

**Option A: Using git (if you want to version control the PDF)**

```bash
# On local machine
cd /Users/mikemurphy/Code/Projects/cv-rag
git add docs/Mike_Murphy_Resume.pdf
git commit -m "Add resume PDF for download"
git push origin main

# On VPS
cd /root/cv-rag
git pull origin main
docker compose restart
```

**Option B: Using scp (direct file transfer)**

```bash
# From your local machine
scp /Users/mikemurphy/Code/Projects/cv-rag/docs/Mike_Murphy_Resume.pdf root@158.220.127.4:/root/cv-rag/docs/

# Then restart the container
ssh root@158.220.127.4 "cd /root/cv-rag && docker compose restart"
```
## 🎯 The Two Paths

### Path A: Technical Tutorial

**"Building an AI Resume with n8n RAG + Ollama"**

- Target: Developers, n8n community, AI builders
- Goal: Education + credibility + community building
- Timeline: Longer to produce (10-15 min detailed walkthrough)

### Path B: Demo/Showcase

**"Chat With My AI Resume - Here's Why You Should Hire Me"**

- Target: Potential employers, recruiters, hiring managers
- Goal: Job opportunities + personal brand
- Timeline: Shorter, punchier (3-5 min demo)

## 💡 My Recommendation: Do BOTH, But Strategically Sequenced

Here's why and how:

### Phase 1: Launch with Demo First (Week 1)

**Create: "My Resume is an AI - Ask It Anything"** (3-5 min)

 

**Why this first:**

1. **Immediate job search impact** - Gets you in front of employers NOW
2. **Unique hook** - "I turned my resume into AI" is more viral than "tutorial #47 on RAG"
3. **Dual showcase** - Shows both the product AND your presentation/creativity skills
4. **Lower production barrier** - Faster to create, get it out there
5. **Creates demand** - Viewers will ask "how did you build this?" → natural segue to tutorial

**Structure:**

```
0:00 - Hook: "I got tired of recruiters not reading my resume..."
0:15 - Demo: Ask 3-4 strategic questions that highlight your skills
       • "What AI projects has Mike built?"
       • "Tell me about Mike's YouTube channel"
       • "What makes Mike different from other candidates?"
1:30 - Behind the scenes: Quick 30-second tech stack overview
       • "Built with n8n, Ollama, pgvector, Streamlit"
       • Show the n8n workflow visually (looks impressive!)
2:00 - More demo: Show edge cases, personality questions
       • "What's Mike's biggest accomplishment?"
       • "Tell me about his Camino journey"
2:30 - Call to action: "Want to chat with my resume? Link in description"
3:00 - Teaser: "Want to build your own? Tutorial coming next week"
```

**Distribution:**

- LinkedIn (primary) - Tag n8n, Anthropic, relevant AI companies
- Twitter/X - AI/tech community
- Your YouTube channel
- Reddit (r/cscareerquestions, r/n8n, r/LocalLLaMA)
- Dev.to / Hashnode article version

### Phase 2: Technical Tutorial (Week 2-3)

**Create: "Build Your Own AI Resume with n8n (No Code RAG Tutorial)"**

 

**Why second:**

1. **You already have interest** - Demo viewers asking "how?"
2. **Portfolio proof** - Live system validates the tutorial
3. **Community contribution** - Establishes you as an educator
4. **Multiple revenue angles** - Course potential, consulting leads
5. **SEO longevity** - Tutorial content has longer shelf life

**Structure:**

```
Part 1: "Why n8n for RAG?" (2 min)
- Show the old Python approach vs n8n visual workflow
- Explain the portfolio angle (showcases n8n skills better)

Part 2: "Architecture Overview" (3 min)
- Draw out the two-workflow design
- Explain ingestion vs query separation
- Show the tech stack diagram

Part 3: "Building Workflow 1 - Ingestion" (5 min)
- Import workflow, configure nodes
- Explain chunking strategy
- Show embedding generation
- Test with curl

Part 4: "Building Workflow 2 - Query Pipeline" (5 min)
- Import workflow, configure nodes
- Explain vector search
- Show LLM integration
- Test with curl

Part 5: "Streamlit Frontend" (3 min)
- Show app.py key sections
- Explain webhook integration
- Deploy to Streamlit Cloud

Part 6: "Results & Next Steps" (2 min)
- Show it working end-to-end
- Ideas for customization
- Link to GitHub repo
```

## 🎬 The Hybrid Approach (My Top Recommendation)

**Create ONE video with TWO distinct sections:**

### **"I Built an AI Resume That Got Me Interviews - Here's How"** (8-12 min)

**Section 1: The Demo (0:00-4:00)**

- Start with the hook and showcase
- Make it punchy, personality-driven
- Show the system working
- **This section works standalone** - can be clipped for LinkedIn/Twitter

**Section 2: The Breakdown (4:00-12:00)**

- "Okay, now let me show you how I built this"
- High-level architecture walkthrough
- Show the n8n workflows visually
- Key decisions and why they matter
- Link to detailed GitHub README for full tutorial

**Why this hybrid works:**

1. **Dual audience** - Catches both employers AND learners
2. **Timestamp strategy** - Employers can watch first 4 min, devs watch all
3. **One production effort** - More efficient than two separate videos
4. **Better YouTube algorithm** - Longer watch time = more recommendations
5. **Versatile distribution** - Can clip section 1 for short-form content

## 📊 Strategic Launch Plan

### Week 1: Pre-Launch

- [ ]  Finalize Streamlit deployment to public URL
- [ ]  Create compelling GitHub README (you've done this! ✅)
- [ ]  Prepare 3-4 "resume questions" that showcase your best attributes
- [ ]  Write LinkedIn post draft
- [ ]  Set up analytics (Google Analytics on Streamlit? Track webhook calls?)

### Week 2: Video Production

- [ ]  Record hybrid video (demo + breakdown)
- [ ]  Edit with good pacing - B-roll of code/workflows
- [ ]  Create thumbnail: Your face + "My AI Resume" + tech stack logos
- [ ]  Write description with:
    - Live demo link
    - GitHub repo link
    - Your contact info / "Hiring? Try my AI resume first"
    - Timestamps for both sections

### Week 3: Launch

**Day 1 (Monday):**

- Upload to YouTube
- LinkedIn post (with video embed)
    - Tag: @n8n, @Anthropic, companies you want to work for
    - Text: "I spent 2 weeks building an AI version of my resume. Here's what happened..."

**Day 2-3:**

- Twitter/X thread with video clips
- Dev.to article (blog format of the tutorial)
- Post to Reddit communities

**Day 4-5:**

- Email to specific companies/recruiters: "Instead of reading my resume, chat with it"
- Engage with comments/questions
- Note any interview requests!

**Week 1-2 post-launch:**

- Monitor for feedback
- Iterate on demo questions if needed
- Track which companies/recruiters actually use it
- Follow up strategically

## 💼 The Job Search Integration

### In Your Applications:

**Resume Header:**

```
Mike Murphy
AI Engineer & Educator
🤖 Chat with my AI Resume: https://cv-rag.streamlit.app
📺 See how I built it: [YouTube link]
```

**Cover Letter Hook:**

```
"I know you're busy, so I built an AI version of my resume you can chat with. 
Ask it anything: https://cv-rag.streamlit.app

Want to see how I built it? I documented everything: [GitHub link]

TL;DR: n8n + Ollama + RAG + Streamlit. Full production system, no shortcuts."
```

**LinkedIn Headline:**

```
AI Engineer | Built an AI Resume That Actually Works | n8n + LLM Expert | Hiring? Chat with my resume 👇
```

### Strategic Targeting:

Send personalized messages to:

1. **n8n team** - "Built a production RAG system entirely in n8n, thought you'd appreciate it"
2. **Companies using n8n** - "Noticed you use n8n, here's what I built with it"
3. **AI startups** - "Built a RAG system from scratch, here's the architecture"
4. **Technical recruiters** - "Instead of a resume, try this"

## 🎯 The Unexpected $ Opportunities

Your project opens several doors:

### 1. **n8n Partnership/Sponsorship**

- They LOVE community showcases
- Could become a featured template in their library
- Potential: Speaking at n8n events, sponsored content

### 2. **Template/Course Sales**

"**Build Your Own AI Resume**" - $29-49

- Pre-configured n8n workflows
- Customization guide
- Deployment walkthrough
- Gumroad or similar

### 3. **Consulting Offers**

"I saw your AI resume video, can you build one for our company?"

- Corporate "chat with our team" systems
- Recruitment automation
- Knowledge base RAG systems

### 4. **Content Creator Path**

- This video proves you can teach complex tech clearly
- Could lead to: Udemy courses, YouTube partnership, sponsored tutorials
- Your YouTube growth goal becomes viable

### 5. **Agency/Service Model**

"**AI Resume as a Service**"

- Help other job seekers build theirs
- $500-1000 per setup
- Could scale to jobseekers, freelancers, consultants

## 🎪 My Final Recommendation

**Do the hybrid video NOW.** Here's why:

1. **Time sensitivity** - You're job searching NOW, not in 3 months
    
2. **Momentum** - You're excited about it right now, capture that energy
    
3. **Market gap** - No one else has done "AI resume demo + tutorial" well yet
    
4. **Skill showcase** - The video itself proves you can:
    
    - Build complex systems
    - Teach/present clearly
    - Think creatively about problems
    - Ship complete projects
5. **Multiple outcomes** - Even if the job search fails (it won't), you have:
    
    - A strong portfolio piece
    - A potential product/service
    - Content that builds your brand
    - Proof you can create and launch

## 🎬 The Script Opener I'd Use

> "Two months ago, I applied to 50 AI engineering jobs. You know how many actually read my full resume? Maybe 3.
> 
>  
> 
> So I did what any engineer would do - I turned my resume INTO an AI.
> 
>  
> 
> Now recruiters can just... talk to it. Watch this:
> 
>  
> 
> [DEMO: Ask it a question, get impressive answer]
> 
>  
> 
> That response pulled from my actual experience, synthesized by Ollama running on my own server, using a RAG pipeline I built entirely in n8n.
> 
>  
> 
> Let me show you how it works, and then I'll show you how I built it..."

This hits:

- ✅ Relatable problem (resume black hole)
- ✅ Creative solution (AI resume)
- ✅ Immediate proof (demo)
- ✅ Technical credibility (architecture mention)
- ✅ Leads into tutorial naturally

## The Bottom Line

**Ship the demo video this week.** It's your best shot at:

1. Landing interviews (primary goal)
2. Going viral in AI/tech circles (bonus)
3. Opening unexpected opportunities (dream scenario)

The tutorial can come after, or be part of the same video. But get something out there NOW while you have momentum and the job market is active.

 

What do you think? Want to brainstorm the script/demo questions more specifically?