# 🚀 Deployment Guide - Teaching Resources Hub

## Quick Deploy to Render (Recommended - Free Tier Available)

### Prerequisites
- GitHub account
- Render account (free at https://render.com)
- Your code pushed to GitHub

---

## Option 1: Deploy to Render (Easiest - Free Tier)

### Step 1: Push to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/teaching-resources-hub.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### Step 3: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Name: `teaching-resources-db`
3. Database: `teaching_resources`
4. User: Leave default
5. Region: Choose closest to you
6. Plan: **Free** (expires after 90 days, but you can create a new one)
7. Click "Create Database"
8. **Save the Internal Database URL** - you'll need this

### Step 4: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** `teaching-resources-hub`
   - **Region:** Same as database
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
   - **Plan:** Free

### Step 5: Add Environment Variables
In the "Environment" section, add:

```
SECRET_KEY=your-random-secret-key-here-make-it-long-and-random
DATABASE_URL=<paste your PostgreSQL Internal Database URL>
DEBUG=False
FLASK_ENV=production
```

**Generate a SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### Step 6: Deploy!
1. Click "Create Web Service"
2. Wait for deployment (3-5 minutes)
3. Your app will be live at: `https://teaching-resources-hub.onrender.com`

### Step 7: Initialize Database
Once deployed, you need to create database tables:

1. Go to your Render dashboard
2. Click on your web service
3. Go to "Shell" tab
4. Run:
```bash
python init_db.py
python create_test_user.py
```

✅ **Your app is now live!**

---

## Option 2: Deploy to Railway (Also Free Tier)

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub

### Step 2: Deploy
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway will auto-detect it's a Python app

### Step 3: Add PostgreSQL
1. Click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set DATABASE_URL

### Step 4: Add Environment Variables
```
SECRET_KEY=your-random-secret-key
DEBUG=False
FLASK_ENV=production
```

### Step 5: Deploy
Railway will automatically deploy. Your app will be at:
`https://your-app.up.railway.app`

---

## Option 3: Deploy to Heroku (Paid)

**Note:** Heroku removed free tier in November 2022. Minimum $7/month.

### Step 1: Install Heroku CLI
```bash
# Download from: https://devcli.heroku.com/
```

### Step 2: Create Heroku App
```bash
heroku login
heroku create teaching-resources-hub
```

### Step 3: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:mini
```

### Step 4: Set Environment Variables
```bash
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set DEBUG=False
```

### Step 5: Deploy
```bash
git push heroku main
```

### Step 6: Initialize Database
```bash
heroku run python init_db.py
heroku run python create_test_user.py
```

---

## Option 4: Deploy to PythonAnywhere (Free Tier)

### Step 1: Create Account
1. Go to https://www.pythonanywhere.com
2. Create free account

### Step 2: Upload Code
1. Use Git or upload files via Web interface
2. Clone your repository:
```bash
git clone https://github.com/YOUR_USERNAME/teaching-resources-hub.git
```

### Step 3: Create Virtual Environment
```bash
cd teaching-resources-hub
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Python version: 3.10
5. Set working directory to your project folder

### Step 5: Configure WSGI file
Edit `/var/www/YOUR_USERNAME_pythonanywhere_com_wsgi.py`:

```python
import sys
import os

project_folder = '/home/YOUR_USERNAME/teaching-resources-hub'
sys.path.insert(0, project_folder)

os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['DEBUG'] = 'False'

from run import app as application
```

### Step 6: Initialize Database
In PythonAnywhere console:
```bash
cd teaching-resources-hub
python init_db.py
python create_test_user.py
```

### Step 7: Reload
Click "Reload" button in Web tab.

Your app will be at: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Post-Deployment Checklist

### ✅ Essential
- [ ] Database tables created (`python init_db.py`)
- [ ] Test users created (optional - `python create_test_user.py`)
- [ ] SECRET_KEY is set to a random value
- [ ] DEBUG is set to False
- [ ] App is accessible via URL
- [ ] Login/signup works
- [ ] Resources page loads (512 resources)

### ✅ Recommended
- [ ] Set up custom domain
- [ ] Configure HTTPS (usually automatic)
- [ ] Set up monitoring/error tracking
- [ ] Configure automated backups
- [ ] Test all features in production
- [ ] Create production admin account

### ✅ Optional Enhancements
- [ ] Set up Redis for caching
- [ ] Configure email service (SendGrid, Mailgun)
- [ ] Set up Google Analytics
- [ ] Add error tracking (Sentry)
- [ ] Set up automated testing (GitHub Actions)
- [ ] Configure CDN for static files

---

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | Flask secret key | Random 64-char string |
| `DATABASE_URL` | Production | PostgreSQL connection | Auto-set by host |
| `DEBUG` | No | Debug mode (False in production) | `False` |
| `FLASK_ENV` | No | Environment | `production` |
| `GOOGLE_CLIENT_ID` | Optional | Google OAuth | From Google Console |
| `GOOGLE_CLIENT_SECRET` | Optional | Google OAuth | From Google Console |

---

## Database Migration

If you need to migrate data from SQLite to PostgreSQL:

```python
# Export from SQLite
import sqlite3
import json

conn = sqlite3.connect('data/users.db')
cursor = conn.cursor()

# Export users
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

# Save to JSON
with open('users_export.json', 'w') as f:
    json.dump(users, f)

# Then import to PostgreSQL using similar logic
```

---

## Troubleshooting

### App Won't Start
- Check logs in platform dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` is up to date
- Check Python version compatibility

### Database Errors
- Ensure DATABASE_URL is correctly set
- Run `python init_db.py` to create tables
- Check database connection permissions

### Static Files Not Loading
- Check static file configuration in platform
- Ensure files are in correct directory structure
- May need to configure static file serving

### 500 Errors
- Check application logs
- Verify all dependencies installed
- Ensure database is accessible
- Check environment variables

---

## Scaling & Performance

### Free Tier Limitations
- **Render Free:** Sleeps after 15 min inactivity, 750 hours/month
- **Railway Free:** $5 credit/month
- **PythonAnywhere Free:** Limited CPU, always on

### When to Upgrade
- **Users:** > 100 daily active users
- **Traffic:** > 10,000 requests/day
- **Database:** > 1GB data
- **Need:** 24/7 uptime, custom domain

### Performance Tips
1. **Enable caching** - Redis for session storage
2. **Optimize queries** - Add database indexes
3. **Use CDN** - Cloudflare for static files
4. **Compress assets** - Minify CSS/JS
5. **Monitor performance** - Use APM tools

---

## Backup Strategy

### Render/Railway PostgreSQL
```bash
# Backup command (run locally)
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20250101.sql
```

### Automated Backups
Most platforms offer automated database backups:
- **Render:** Daily backups on paid plans
- **Railway:** Point-in-time recovery
- **Heroku:** Continuous protection on paid plans

---

## Production Best Practices

1. **Security**
   - Use strong SECRET_KEY
   - Enable HTTPS only
   - Set secure cookie flags
   - Regular security updates

2. **Monitoring**
   - Set up error tracking (Sentry)
   - Monitor uptime (UptimeRobot)
   - Track analytics (Google Analytics)
   - Log aggregation (Papertrail)

3. **Performance**
   - Use production WSGI server (gunicorn)
   - Enable gzip compression
   - Implement caching headers
   - Optimize database queries

4. **Maintenance**
   - Regular dependency updates
   - Database backups
   - Monitor disk space
   - Review error logs

---

## Cost Estimates

### Free Tiers
- **Render:** Free web service + Free PostgreSQL (90 days)
- **Railway:** $5 credit/month (good for small apps)
- **PythonAnywhere:** Free (limited resources)

### Paid Options (when you outgrow free)
- **Render:** $7/month (Starter)
- **Railway:** $5-20/month (usage-based)
- **Heroku:** $7/month (Eco dyno)
- **DigitalOcean:** $6/month (Droplet)

---

## Support & Resources

### Documentation
- Flask: https://flask.palletsprojects.com/
- Render: https://render.com/docs
- Railway: https://docs.railway.app/
- Heroku: https://devcenter.heroku.com/

### Community
- Flask Discord: https://discord.gg/pallets
- GitHub Issues: Your repository
- Stack Overflow: Tag with `flask`

---

## Next Steps After Deployment

1. **Test Everything**
   - Sign up as new user
   - Test all features
   - Try on mobile devices
   - Check different browsers

2. **Customize**
   - Add your branding
   - Customize colors/logo
   - Update about page
   - Add contact information

3. **Promote**
   - Share with teacher communities
   - Post on social media
   - Submit to education directories
   - Gather feedback

4. **Improve**
   - Monitor user feedback
   - Fix bugs
   - Add requested features
   - Optimize performance

---

## 🎉 Congratulations!

Your Teaching Resources Hub is now live and accessible to teachers worldwide!

**Share your deployment:**
- URL: `https://your-app.onrender.com`
- GitHub: `https://github.com/YOUR_USERNAME/teaching-resources-hub`
- Twitter: "Just deployed my Teaching Resources Hub! 🎓"

---

**Need Help?** Check the troubleshooting section or open an issue on GitHub.
