# 📚 Teaching Resources Hub

> **The Ultimate Educational Resource Directory for Teachers Worldwide**

A comprehensive, community-driven platform connecting educators with 512+ curated educational resources across 55 categories. Features social networking, resource reviews, user submissions, and gamification to build the largest teacher resource community.

[![Flask](https://img.shields.io/badge/Flask-3.0.0-blue.svg)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](https://github.com)

## 🆕 Latest Updates

**December 2025 - Phase 3: Resource Upload & Admin System**
- 📤 **Teacher Resource Uploads** - Upload and share PDFs, documents, presentations, worksheets (50MB max, 12+ file types)
- 🗂️ **Resource Management** - Complete dashboard to manage, edit, and track your uploaded materials
- 🔍 **Advanced Browse & Search** - Filter by category, grade, difficulty, file type with full-text search
- 📊 **Download Analytics** - Track views, downloads, and engagement on your shared resources
- 🛠️ **Admin Dashboard** - Comprehensive moderation tools with user management and analytics
- 👤 **Teacher Profiles & Rooms** - Customizable profiles with bio, subjects, grades, and collaboration settings
- 🔎 **Teacher Discovery** - Find educators by subject, grade level, location, and collaboration interests
- 📈 **Reputation System** - Earn points through contributions, reviews, and community engagement

**November 2025**
- ✨ **Modern UI Redesign** - Complete color scheme overhaul with improved readability and professional gradient purple theme
- 🔧 **Duplicate Resources Removed** - Cleaned database from 996 to 512 high-quality, unique resources
- ⭐ **Favorites System Fixed** - Fully functional resource bookmarking and favorites management
- 📊 **Dynamic Resource Counts** - All resource statistics now update automatically as content changes
- 🎨 **Enhanced User Experience** - Improved navigation, better contrast, and modern card-based layouts
- 🔐 **Enterprise-Grade Security** - Comprehensive authentication, input validation, and security headers
- 👥 **Social Features** - User profiles, customizable rooms, favorites, and visit tracking
- 📱 **Responsive Design** - Fully mobile-friendly interface with smooth animations

---

## 🌟 Features

### 📖 Resource Directory
- **512 Curated Educational Resources** across 55 categories
- Advanced search and filtering with autocomplete
- Categories include Math, Science, ELA, STEM, SEL, and more
- Grade-level specific resources (Pre-K through 12th grade)
- 75% free resources for budget-conscious educators
- Detailed category pages with statistics and resource breakdowns

### 📤 Teacher Resource Uploads (NEW!)
- **Upload & Share Materials** - PDFs, DOC, PPT, XLS, images, ZIP files (50MB max)
- **Drag-and-Drop Interface** - Easy file upload with live preview
- **Comprehensive Metadata** - Tag with category, grade, difficulty, standards, duration
- **My Resources Dashboard** - Manage all your uploads in one place
- **Public/Private Control** - Choose who can access your resources
- **Download Tracking** - See views, downloads, and engagement analytics
- **Edit Anytime** - Update metadata without re-uploading files

### 🔍 Browse & Discover Resources
- **Advanced Search** - Full-text search across titles, descriptions, and tags
- **Smart Filters** - Category, grade level, difficulty, file type
- **Sorting Options** - Newest, most viewed, most downloaded, highest rated
- **Pagination** - Clean browsing experience with page navigation
- **Resource Details** - Full pages with uploader info, metadata, and stats

### 👤 Teacher Profiles & Rooms
- **Customizable Profile** - Display name, bio, profile photo, location
- **Professional Info** - Teaching subjects, grade levels, years of experience
- **Current Unit Showcase** - Share what you're teaching right now
- **Social Links** - Twitter, personal website, social media
- **Collaboration Settings** - Looking for mentorship, open to collaboration, can help with...
- **Achievements Display** - Showcase your contributions and badges
- **Visit Tracking** - See who's viewed your profile

### 🔎 Teacher Discovery
- **Find Educators** - Search by name, subject, grade level, location
- **Advanced Filters** - Subject taught, grade level, collaboration interests
- **Sorting Options** - Newest members, most active, highest reputation
- **Teacher Cards** - Quick overview with follow button and stats
- **Community Building** - Connect with like-minded educators

### 🛠️ Admin Dashboard & Moderation
- **User Management** - View, search, filter, and manage all users
- **Quick Actions** - Verify teachers, make moderators, ban users
- **Analytics Dashboard** - 30-day growth charts with Chart.js
- **Content Statistics** - Track resources, reviews, submissions, uploads
- **Pending Verification Queue** - Quick verify/reject workflow
- **Activity Monitoring** - Recent users, top contributors, trends

### ⭐ Review & Rating System
- 5-star rating system with detailed reviews
- Community-driven resource quality assessment
- Helpful vote system to surface best reviews
- Context-aware reviews (grade level, subject, time used)

### 📤 User-Submitted Resources
- Teachers can submit new external resources
- Moderation workflow with approval/rejection
- Earn reputation points for approved submissions

### 👥 Social Networking
- Follow other educators
- Activity feed with real-time updates
- Discover teachers by grade level and subject
- Reputation-based leaderboards

### 🎮 Gamification & Reputation
- Earn reputation points for all contributions
- Points for uploads, reviews, helpful votes, submissions
- Leaderboards for top contributors
- Track your stats and progress
- Verified teacher badges
- Achievement system

---

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/teaching-resources-hub.git
cd teaching-resources-hub
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize the database**
```bash
python init_db.py
python create_test_user.py
```

4. **Create admin account (optional)**
```bash
python create_admin.py
```

5. **Run the application**
```bash
python run.py
```

6. **Open your browser**
```
http://127.0.0.1:5000
```

### Test Credentials
**Regular User:**
- Username: `testteacher`
- Password: `password123`

**Admin Account:**
- Username: `admin`
- Email: `admin@teachinghub.com`
- Password: `Admin123!`

---

## 🚀 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions to Render, Railway, Heroku, or PythonAnywhere.

---

## 📈 Statistics

- **512 Curated Educational Resources**
- **55 Categories**
- **75% Free Resources**
- **18 Database Models** (User, Follow, Review, Favorite, ResourceSubmission, UploadedResource, ResourceDownload, ResourceCollection, CollectionItem, and more)
- **50+ API Endpoints**
- **20,000+ Lines of Code**
- **12+ Supported File Types** for uploads
- **Complete Admin & Moderation System**

---

## 🛠️ Tech Stack

- Flask 3.0
- SQLAlchemy 2.0
- PostgreSQL/SQLite
- Flask-Login
- Gunicorn

---

Made with ❤️ for teachers everywhere
