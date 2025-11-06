# 🏫 Teacher Room Enhancement Roadmap

**Vision:** Transform teacher profiles into vibrant, personalized "rooms" that showcase personality, expertise, and resources - inspired by MySpace customization but built for modern educators.

---

## 📊 Current State

### Implemented Features ✅
- **Basic Customization**
  - 6 theme presets (Light, Dark, Ocean, Sunset, Forest, Lavender)
  - Custom colors (background, text, accent)
  - Live preview during editing

- **Profile Information**
  - Display name, username, bio
  - Teaching philosophy
  - School, grade levels, subjects
  - Website and Twitter links

- **Social Features**
  - Favorite resources (up to 12 displayed)
  - Visit tracking
  - Recent visitors (last 5)
  - Visit counter

### Underutilized Database Fields ⚠️
The User model already has these fields but they're not being used:
- `profile_picture` - Profile image upload
- `years_teaching` - Teaching experience
- `location` - City, State
- `favorite_quote` - Personal quote
- `favorite_lesson` - Best lesson description
- `classroom_setup` - Classroom description
- `about_me` - Separate from bio
- `profile_public` - Privacy toggle
- `show_favorites_public` - Favorites visibility

---

## 🚀 PHASE 1: Quick Wins
**Timeline:** 2-3 hours | **Difficulty:** Easy | **Impact:** HIGH

### 1.1 Profile Picture Upload 📸
**Why:** Letter-based avatars are boring. Real photos build connection.

**Implementation:**
- File upload field in edit profile
- Store in `/static/uploads/profiles/`
- Image validation (size, format)
- Default fallback to letter avatar
- Circular crop preview

**Technical Details:**
```python
# File upload handling
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Profile picture route
@bp.route('/profile/upload-picture', methods=['POST'])
def upload_picture():
    file = request.files['profile_picture']
    # Validate, save, update database
```

**UI Changes:**
- Add image upload input to edit_profile.html
- Show current image with "Change Photo" button
- Display uploaded image in profile.html

---

### 1.2 Favorite Quote Banner 💬
**Why:** Adds personality and inspiration. Nostalgic MySpace feature.

**Implementation:**
- Text input field (max 200 chars)
- Display prominently at top of profile
- Stylized quote box with quotation marks
- Optional empty state

**UI Design:**
```html
<div class="quote-banner">
  <span class="quote-mark">"</span>
  <p class="quote-text">{{ profile_user.favorite_quote }}</p>
  <span class="quote-mark">"</span>
</div>
```

---

### 1.3 Years Teaching Badge 🎓
**Why:** Shows experience level at a glance. Builds credibility.

**Implementation:**
- Integer field (years_teaching)
- Display as badge/medal icon
- Auto-calculate from start year (alternative approach)
- Color-coded by experience level:
  - 0-3 years: Green (New Teacher)
  - 4-10 years: Blue (Experienced)
  - 11-20 years: Purple (Veteran)
  - 20+ years: Gold (Master Educator)

**Display:**
```html
<div class="experience-badge veteran">
  <span class="badge-icon">🏆</span>
  <span class="badge-text">15 Years Teaching</span>
</div>
```

---

### 1.4 Location Display 📍
**Why:** Helps teachers connect with nearby colleagues. Community building.

**Implementation:**
- Text field for location (City, State format)
- Display with emoji: "📍 Austin, TX"
- Optional - can be left blank
- Privacy-conscious (only city/state, not address)

---

### 1.5 Privacy Controls 🔒
**Why:** Essential for teacher safety and comfort. MUST HAVE.

**Implementation:**
- Toggle switches in edit profile:
  - `profile_public`: Make profile visible to everyone vs. logged-in only
  - `show_favorites_public`: Show favorites to everyone vs. hidden
  - Future: `show_email`, `show_school`, etc.

**Route Protection:**
```python
@bp.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()

    # Check privacy settings
    if not user.profile_public and not current_user.is_authenticated:
        flash('This profile is private.', 'error')
        return redirect(url_for('main.index'))
```

**UI:**
```html
<div class="privacy-section">
  <h3>🔒 Privacy Settings</h3>
  <label class="toggle-switch">
    <input type="checkbox" name="profile_public" {% if current_user.profile_public %}checked{% endif %}>
    <span>Make profile public</span>
  </label>
  <label class="toggle-switch">
    <input type="checkbox" name="show_favorites_public" {% if current_user.show_favorites_public %}checked{% endif %}>
    <span>Show favorites publicly</span>
  </label>
</div>
```

---

### 1.6 Visitor Counter Widget 📊
**Why:** Fun nostalgia factor. Shows engagement.

**Implementation:**
- Display total visit count prominently
- "You are visitor #1,234" style
- Animated counter (optional)
- Retro styling

**Display:**
```html
<div class="visitor-counter retro">
  <span class="counter-label">Profile Views</span>
  <span class="counter-digits">{{ total_visits }}</span>
</div>
```

**CSS Styling:**
```css
.visitor-counter.retro {
  background: linear-gradient(to bottom, #333, #000);
  color: #0f0;
  font-family: 'Courier New', monospace;
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid #0f0;
  text-align: center;
}
```

---

### 1.7 Enhanced Favorites Organization 📚
**Why:** Current implementation is limited. Teachers need better organization.

**Current Limitations:**
- Only shows 12 favorites
- No organization/folders
- No personal notes on favorites
- No categories

**Enhancements:**

**A. Favorites Collections**
```sql
-- New table
CREATE TABLE favorite_collections (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP
);

-- Add to Favorite model
collection_id INTEGER FOREIGN KEY
```

**B. Personal Notes (Already in model!)**
- Use `personal_note` field that's already in Favorite model
- Add note editing UI to favorites page
- Display notes on hover/click

**C. Better Favorites Display**
- Show ALL favorites (not just 12)
- Group by collection or category
- Search/filter favorites
- Sort by: Date added, Name, Category
- Grid view vs. List view toggle

**Implementation:**
```python
# In profile route
user_favorites = Favorite.query.filter_by(user_id=user.id)\
    .order_by(Favorite.created_at.desc())\
    .all()  # No limit

# Group by collection
favorites_by_collection = {}
for fav in user_favorites:
    collection = fav.collection_id or 'Uncategorized'
    if collection not in favorites_by_collection:
        favorites_by_collection[collection] = []
    favorites_by_collection[collection].append(fav)
```

---

## 🎨 PHASE 2: Rich Content Sections
**Timeline:** 4-6 hours | **Difficulty:** Medium | **Impact:** HIGH

### 2.1 Classroom Showcase Gallery 🖼️
**Why:** Visual storytelling. Show your classroom personality.

**Features:**
- Upload multiple photos (classroom, bulletin boards, student work)
- Gallery grid layout
- Lightbox view
- Captions for each photo
- Max 20 photos

**New Model:**
```python
class ClassroomPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_url = db.Column(db.String(500))
    caption = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**UI:**
```html
<div class="classroom-gallery">
  <h2>My Classroom</h2>
  <div class="photo-grid">
    {% for photo in classroom_photos %}
    <div class="photo-card" onclick="openLightbox({{ loop.index0 }})">
      <img src="{{ photo.image_url }}" alt="{{ photo.caption }}">
      <p class="photo-caption">{{ photo.caption }}</p>
    </div>
    {% endfor %}
  </div>
</div>
```

---

### 2.2 Teaching Journey Timeline ⏳
**Why:** Tell your story. Show career progression.

**Features:**
- Add milestones (year, event, description)
- Visual timeline
- Icons for different event types (🎓 degree, 📚 new job, 🏆 award)
- Sortable by date

**New Model:**
```python
class TeachingMilestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    year = db.Column(db.Integer)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    milestone_type = db.Column(db.String(50))  # education, job, award, certification
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**UI Design:**
```html
<div class="teaching-timeline">
  <h2>My Teaching Journey</h2>
  {% for milestone in milestones|sort(attribute='year') %}
  <div class="timeline-item">
    <div class="timeline-year">{{ milestone.year }}</div>
    <div class="timeline-content">
      <h3>{{ milestone.title }}</h3>
      <p>{{ milestone.description }}</p>
    </div>
  </div>
  {% endfor %}
</div>
```

---

### 2.3 Favorite Lessons Showcase 📝
**Why:** Share successful lessons. Build your reputation.

**Features:**
- Use existing `favorite_lesson` field (currently unused)
- Expand to multiple lessons
- Include: Title, Grade Level, Subject, Description, Materials needed
- Optional link to full lesson plan
- Tags for easy discovery

**Enhanced Model:**
```python
class FavoriteLesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200))
    grade_level = db.Column(db.String(50))
    subject = db.Column(db.String(100))
    description = db.Column(db.Text)
    materials_needed = db.Column(db.Text)
    duration = db.Column(db.String(50))  # "1 hour", "3 days"
    tags = db.Column(db.String(500))  # Comma-separated
    lesson_plan_url = db.Column(db.String(500))  # External link
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### 2.4 What I'm Teaching Now 📅
**Why:** Shows current work. Easy icebreaker for connections.

**Features:**
- Current unit/topic
- Start and end dates
- Subject and grade level
- Brief description
- Updates regularly

**New Model:**
```python
class CurrentUnit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200))
    subject = db.Column(db.String(100))
    grade_level = db.Column(db.String(50))
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20))  # planning, active, completed
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Display:**
```html
<div class="current-teaching">
  <h2>📚 Currently Teaching</h2>
  <div class="unit-card active">
    <h3>{{ unit.title }}</h3>
    <div class="unit-meta">
      <span>{{ unit.subject }}</span> •
      <span>{{ unit.grade_level }}</span> •
      <span>{{ unit.start_date.strftime('%b %d') }} - {{ unit.end_date.strftime('%b %d') }}</span>
    </div>
    <p>{{ unit.description }}</p>
  </div>
</div>
```

---

### 2.5 Professional Achievements 🏆
**Why:** Showcase credentials. Build authority.

**Features:**
- Certifications (National Board, ESL, etc.)
- Awards and recognitions
- Professional development
- Conference presentations
- Publications

**New Model:**
```python
class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200))
    achievement_type = db.Column(db.String(50))  # certification, award, conference, publication
    organization = db.Column(db.String(200))
    year = db.Column(db.Integer)
    description = db.Column(db.Text)
    credential_url = db.Column(db.String(500))  # Link to certificate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### 2.6 Collaboration Board 🤝
**Why:** Connect teachers. Foster collaboration.

**Features:**
- "Looking for..." section (collaboration opportunities)
- "Can help with..." section (expertise to share)
- Subject/grade level tags
- Collaboration requests

**Implementation:**
```python
# Add to User model
looking_for = db.Column(db.Text)  # What they need help with
can_help_with = db.Column(db.Text)  # What they can offer
open_to_collaboration = db.Column(db.Boolean, default=True)
```

**Display:**
```html
<div class="collaboration-board">
  <div class="looking-for">
    <h3>🔍 Looking For</h3>
    <p>{{ profile_user.looking_for }}</p>
  </div>
  <div class="can-help">
    <h3>💡 Can Help With</h3>
    <p>{{ profile_user.can_help_with }}</p>
  </div>
</div>
```

---

## 👥 PHASE 3: Social & Interactive
**Timeline:** 6-8 hours | **Difficulty:** Medium-Hard | **Impact:** VERY HIGH

### 3.1 Guestbook/Comments 📖
**Why:** Classic MySpace feature. Builds community.

**Features:**
- Visitors leave public messages
- Threading/replies
- Moderation (approve/delete)
- Rich text formatting
- Emoji support

**New Model:**
```python
class GuestbookEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('guestbook_entries.id'))  # For replies
    approved = db.Column(db.Boolean, default=True)  # Owner can moderate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    profile_user = db.relationship('User', foreign_keys=[profile_user_id])
    author = db.relationship('User', foreign_keys=[author_id])
    replies = db.relationship('GuestbookEntry', backref=db.backref('parent', remote_side=[id]))
```

**Routes:**
```python
@bp.route('/profile/<username>/guestbook/post', methods=['POST'])
@login_required
def post_guestbook_message(username):
    # Create guestbook entry
    # Send notification to profile owner

@bp.route('/profile/guestbook/<int:entry_id>/approve', methods=['POST'])
@login_required
def approve_guestbook_entry(entry_id):
    # Only profile owner can approve
```

---

### 3.2 Top Friends Feature 👯
**Why:** MySpace nostalgia. Highlight key connections.

**Features:**
- Select up to 8 "top friends"
- Display with photos
- Drag-and-drop ordering
- Link to their profiles

**Implementation:**
```python
# Add to User model
top_friends = db.Column(db.Text)  # JSON array of user IDs in order

# Example: "[123, 456, 789]"
```

**Display:**
```html
<div class="top-friends">
  <h2>Top Friends</h2>
  <div class="friends-grid">
    {% for friend_id in profile_user.get_top_friends() %}
    <a href="/profile/{{ friend.username }}" class="friend-card">
      <img src="{{ friend.get_avatar() }}" alt="{{ friend.display_name }}">
      <span>{{ friend.display_name }}</span>
    </a>
    {% endfor %}
  </div>
</div>
```

---

### 3.3 Follow/Follower Display 🔔
**Why:** Show social proof. Encourage connections.

**Features:**
- Follower count badge
- Following count badge
- Follower list (modal/separate page)
- Follow button (for non-owner)
- Mutual friends indicator

**Already have Follow model, just need UI:**
```html
<div class="social-stats">
  <div class="stat-item" onclick="showFollowers()">
    <strong>{{ follower_count }}</strong>
    <span>Followers</span>
  </div>
  <div class="stat-item" onclick="showFollowing()">
    <strong>{{ following_count }}</strong>
    <span>Following</span>
  </div>
  {% if not is_own_profile %}
  <button class="btn-follow" onclick="toggleFollow()">
    {% if current_user.is_following(profile_user) %}
    Unfollow
    {% else %}
    Follow
    {% endif %}
  </button>
  {% endif %}
</div>
```

---

### 3.4 Activity Feed 📰
**Why:** Show recent contributions. Keep profile dynamic.

**Features:**
- Recent reviews posted
- Resources submitted
- Favorites added
- Achievements earned
- Limit to last 10 activities

**Already have Activity model, just need display:**
```html
<div class="activity-feed">
  <h2>Recent Activity</h2>
  {% for activity in recent_activities %}
  <div class="activity-item">
    <span class="activity-icon">{{ activity.get_icon() }}</span>
    <p>{{ activity.get_description() }}</p>
    <span class="activity-time">{{ activity.created_at|timeago }}</span>
  </div>
  {% endfor %}
</div>
```

---

### 3.5 Skill Endorsements 🌟
**Why:** LinkedIn-style validation. Build credibility.

**Features:**
- Add skills (max 20)
- Other teachers can endorse skills
- Show endorsement count per skill
- Display top endorsed skills

**New Models:**
```python
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    skill_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SkillEndorsement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'))
    endorser_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Display:**
```html
<div class="skills-section">
  <h2>Skills & Expertise</h2>
  {% for skill in profile_user.get_skills() %}
  <div class="skill-badge">
    <span class="skill-name">{{ skill.skill_name }}</span>
    <span class="endorsement-count">{{ skill.get_endorsement_count() }}</span>
    {% if not is_own_profile %}
    <button class="btn-endorse" onclick="endorseSkill({{ skill.id }})">+</button>
    {% endif %}
  </div>
  {% endfor %}
</div>
```

---

### 3.6 Teaching Badges 🎖️
**Why:** Gamification. Visual achievement display.

**Features:**
- Automatic badges:
  - Early Adopter (joined in first month)
  - Review Master (50+ reviews)
  - Resource Contributor (10+ submissions)
  - Helper (100+ helpful votes)
  - Veteran Teacher (20+ years)
- Display on profile
- Hover for badge description
- Badge collection page

**Implementation:**
```python
class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))  # Emoji or icon class
    criteria = db.Column(db.Text)  # JSON criteria

class UserBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'))
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Auto-award logic:**
```python
def check_and_award_badges(user):
    """Check if user qualifies for new badges."""
    # Review Master badge
    if user.total_reviews >= 50:
        award_badge(user, 'review_master')

    # Resource Contributor
    if user.total_submissions >= 10:
        award_badge(user, 'resource_contributor')
```

---

### 3.7 Profile Background Music 🎵
**Why:** Ultimate MySpace nostalgia. Optional feature.

**Features:**
- Upload audio file or link to Spotify/SoundCloud
- Auto-play toggle (off by default for sanity)
- Volume control
- Mute button
- Educational podcasts or classroom playlists

**Implementation:**
```python
# Add to User model
profile_music_url = db.Column(db.String(500))
auto_play_music = db.Column(db.Boolean, default=False)
```

**UI:**
```html
{% if profile_user.profile_music_url %}
<div class="music-player">
  <audio id="profileMusic" {% if profile_user.auto_play_music %}autoplay{% endif %} loop>
    <source src="{{ profile_user.profile_music_url }}" type="audio/mpeg">
  </audio>
  <button onclick="toggleMusic()" class="music-toggle">🔊</button>
</div>
{% endif %}
```

---

## 🎨 PHASE 4: Advanced Features
**Timeline:** 8-12 hours | **Difficulty:** Hard | **Impact:** MEDIUM-HIGH

### 4.1 Custom Profile Layouts 🖼️
**Why:** Ultimate customization. Different teaching styles.

**Features:**
- Multiple layout templates:
  - Classic (current layout)
  - Modern Grid
  - Sidebar Left/Right
  - Minimalist
  - Showcase (photo-heavy)
- Drag-and-drop section ordering
- Show/hide sections

**Implementation:**
```python
# Add to User model
profile_layout = db.Column(db.String(50), default='classic')
section_order = db.Column(db.Text)  # JSON array

# Example section_order:
# ["about", "favorites", "gallery", "teaching_philosophy", "achievements"]
```

**Template Structure:**
```html
{% if profile_user.profile_layout == 'modern_grid' %}
  {% include 'profile/layouts/modern_grid.html' %}
{% elif profile_user.profile_layout == 'sidebar' %}
  {% include 'profile/layouts/sidebar.html' %}
{% else %}
  {% include 'profile/layouts/classic.html' %}
{% endif %}
```

---

### 4.2 Widget/Section Management 🧩
**Why:** Modular profiles. Show what matters to you.

**Features:**
- Toggle sections on/off
- Reorder sections (drag-and-drop)
- Collapse/expand sections
- Visitor sees only enabled sections

**Implementation:**
```python
class ProfileSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    section_type = db.Column(db.String(50))  # favorites, gallery, achievements, etc.
    enabled = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    collapsed = db.Column(db.Boolean, default=False)
```

**UI (Edit Mode):**
```html
<div class="section-manager">
  <h2>Manage Profile Sections</h2>
  <div id="sortableSections" class="section-list">
    {% for section in profile_sections %}
    <div class="section-item" data-id="{{ section.id }}">
      <span class="drag-handle">⋮⋮</span>
      <span class="section-name">{{ section.get_display_name() }}</span>
      <label class="toggle-switch">
        <input type="checkbox" {% if section.enabled %}checked{% endif %}>
      </label>
    </div>
    {% endfor %}
  </div>
</div>
```

---

### 4.3 Embedded Content 📺
**Why:** Rich multimedia profiles. Showcase external content.

**Features:**
- Embed YouTube videos (classroom tours, lesson demos)
- Pinterest boards (teaching resources)
- Twitter feed
- Instagram photos
- TikTok classroom tips
- Padlet walls

**Implementation:**
```python
class EmbeddedContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content_type = db.Column(db.String(50))  # youtube, pinterest, twitter
    embed_code = db.Column(db.Text)  # Iframe or embed code
    title = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Display:**
```html
<div class="embedded-content-section">
  <h2>Featured Content</h2>
  {% for content in embedded_content %}
  <div class="embed-container">
    <h3>{{ content.title }}</h3>
    {{ content.embed_code|safe }}
  </div>
  {% endfor %}
</div>
```

---

### 4.4 Profile Analytics Dashboard 📊
**Why:** Understand engagement. Data-driven profile optimization.

**Features (Owner Only):**
- Total profile views (by day/week/month)
- Visitor demographics (grade level, subjects)
- Most viewed sections
- Referral sources
- Follower growth chart
- Resource click-through rates
- Guestbook engagement

**New Model:**
```python
class ProfileAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(db.Date)
    total_views = db.Column(db.Integer, default=0)
    unique_visitors = db.Column(db.Integer, default=0)
    new_followers = db.Column(db.Integer, default=0)
    section_views = db.Column(db.Text)  # JSON: {"favorites": 50, "gallery": 30}
    referral_sources = db.Column(db.Text)  # JSON
```

**Dashboard Route:**
```python
@bp.route('/profile/analytics')
@login_required
def profile_analytics():
    # Last 30 days
    analytics = ProfileAnalytics.query.filter_by(
        user_id=current_user.id
    ).filter(
        ProfileAnalytics.date >= datetime.now() - timedelta(days=30)
    ).all()

    return render_template('profile/analytics.html', analytics=analytics)
```

---

### 4.5 Direct Messaging System 💬
**Why:** Teacher-to-teacher communication. Collaboration.

**Features:**
- Send/receive private messages
- Message threads
- Unread count badge
- Email notifications (optional)
- Block/report users
- Message search

**New Models:**
```python
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subject = db.Column(db.String(200))
    body = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)
    thread_id = db.Column(db.Integer)  # Group related messages
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])

class MessageThread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

### 4.6 Virtual Office Hours 📅
**Why:** Structured availability. Professional networking.

**Features:**
- Set weekly availability (Google Calendar style)
- "Available for collaboration" status
- Booking/request system
- Time zone support
- Video call integration (Zoom/Meet link)

**Implementation:**
```python
class OfficeHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    day_of_week = db.Column(db.Integer)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    timezone = db.Column(db.String(50))
    meeting_link = db.Column(db.String(500))  # Zoom/Meet URL
    enabled = db.Column(db.Boolean, default=True)
```

**Display:**
```html
<div class="office-hours">
  <h2>📅 Virtual Office Hours</h2>
  <p>{{ profile_user.display_name }} is available for collaboration:</p>
  <div class="availability-grid">
    {% for slot in office_hours %}
    <div class="time-slot">
      <span class="day">{{ slot.get_day_name() }}</span>
      <span class="time">{{ slot.start_time }} - {{ slot.end_time }}</span>
      <span class="timezone">{{ slot.timezone }}</span>
    </div>
    {% endfor %}
  </div>
  {% if not is_own_profile %}
  <a href="{{ profile_user.get_meeting_link() }}" class="btn-join-meeting" target="_blank">
    Request Collaboration Time
  </a>
  {% endif %}
</div>
```

---

### 4.7 Resource Collections (Playlists) 🎵
**Why:** Curated resource lists. Share expertise.

**Features:**
- Create named collections ("Best Math Games", "My Go-To Science Tools")
- Public/private toggle
- Add resources from main directory
- Add external links
- Share collection URL
- Browse other teachers' collections

**New Model:**
```python
class ResourceCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(200))
    description = db.Column(db.Text)
    public = db.Column(db.Boolean, default=True)
    cover_image = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('CollectionItem', backref='collection', lazy='dynamic')

class CollectionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('resource_collections.id'))
    resource_name = db.Column(db.String(200))  # From main directory
    external_url = db.Column(db.String(500))  # Or custom link
    note = db.Column(db.Text)  # Why this resource?
    order = db.Column(db.Integer, default=0)
```

**Display:**
```html
<div class="resource-collections">
  <h2>📚 My Curated Collections</h2>
  {% for collection in collections %}
  <div class="collection-card">
    <h3>{{ collection.name }}</h3>
    <p>{{ collection.description }}</p>
    <span class="collection-count">{{ collection.items.count() }} resources</span>
    <a href="/collections/{{ collection.id }}" class="btn-view-collection">View Collection</a>
  </div>
  {% endfor %}
</div>
```

---

### 4.8 Auto Dark Mode 🌙
**Why:** Eye comfort. Modern UX.

**Features:**
- Auto-detect system preference
- Manual toggle override
- Remember user preference
- Smooth transition
- Dark mode compatible themes

**Implementation:**
```javascript
// Detect system preference
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

// Check user preference (localStorage)
const userPreference = localStorage.getItem('darkMode');

// Apply dark mode
if (userPreference === 'dark' || (userPreference === null && prefersDark)) {
    document.body.classList.add('dark-mode');
}

// Toggle function
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode',
        document.body.classList.contains('dark-mode') ? 'dark' : 'light'
    );
}
```

**CSS:**
```css
body.dark-mode {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

body.dark-mode .profile-room {
    background-color: #2c2c2c;
}

body.dark-mode .stat-card {
    background: #333;
    color: #fff;
}
```

---

## 📊 Implementation Priority Matrix

| Phase | Feature | Impact | Effort | Priority |
|-------|---------|--------|--------|----------|
| 1 | Profile Pictures | HIGH | LOW | ⭐⭐⭐⭐⭐ |
| 1 | Privacy Controls | HIGH | LOW | ⭐⭐⭐⭐⭐ |
| 1 | Better Favorites | HIGH | MEDIUM | ⭐⭐⭐⭐⭐ |
| 1 | Visitor Counter | MEDIUM | LOW | ⭐⭐⭐⭐ |
| 1 | Favorite Quote | MEDIUM | LOW | ⭐⭐⭐⭐ |
| 1 | Years Teaching | MEDIUM | LOW | ⭐⭐⭐⭐ |
| 1 | Location Display | LOW | LOW | ⭐⭐⭐ |
| 2 | Classroom Gallery | HIGH | MEDIUM | ⭐⭐⭐⭐⭐ |
| 2 | Teaching Journey | MEDIUM | MEDIUM | ⭐⭐⭐⭐ |
| 2 | Collaboration Board | HIGH | LOW | ⭐⭐⭐⭐⭐ |
| 3 | Guestbook | HIGH | MEDIUM | ⭐⭐⭐⭐⭐ |
| 3 | Follow Display | HIGH | LOW | ⭐⭐⭐⭐⭐ |
| 3 | Activity Feed | MEDIUM | MEDIUM | ⭐⭐⭐⭐ |
| 3 | Top Friends | MEDIUM | LOW | ⭐⭐⭐ |
| 3 | Skill Endorsements | MEDIUM | MEDIUM | ⭐⭐⭐ |
| 4 | Direct Messaging | HIGH | HIGH | ⭐⭐⭐⭐ |
| 4 | Analytics Dashboard | MEDIUM | MEDIUM | ⭐⭐⭐ |
| 4 | Resource Collections | HIGH | MEDIUM | ⭐⭐⭐⭐ |
| 4 | Dark Mode | LOW | LOW | ⭐⭐⭐ |

---

## 🎯 Success Metrics

### Phase 1
- [ ] 80%+ of users upload profile picture
- [ ] Privacy settings used by 50%+ users
- [ ] Average favorites per user increases 2x
- [ ] Visitor counter viewed on 90%+ profile visits

### Phase 2
- [ ] 40%+ users add classroom photos
- [ ] Teaching timeline created by 30%+ users
- [ ] Collaboration board filled out by 60%+ users

### Phase 3
- [ ] Average 5+ guestbook entries per active profile
- [ ] 50%+ increase in follow/follower activity
- [ ] 70%+ users with at least one skill endorsement

### Phase 4
- [ ] 30%+ users create at least one resource collection
- [ ] Direct messages sent: 100+ per week
- [ ] Analytics dashboard viewed 2x per week (per user)

---

## 🔒 Security Considerations

### File Uploads (Phase 1, 2)
- Validate file types (whitelist: jpg, png, gif)
- Limit file sizes (5MB for images)
- Scan for malware
- Store in separate directory with restricted execution
- Generate unique filenames

### Privacy (All Phases)
- Respect profile_public settings
- Honor show_favorites_public toggle
- FERPA compliance (no student data)
- Ability to delete all data (GDPR)

### Messaging (Phase 4)
- Rate limiting (prevent spam)
- Block/report functionality
- Content moderation flags
- No external links in messages (or validate)

### User-Generated Content
- Sanitize all HTML input
- XSS prevention
- CSRF tokens on all forms
- SQL injection protection (parameterized queries)

---

## 🚀 Getting Started

### Ready to Begin Phase 1?

**First Steps:**
1. ✅ Create uploads directory structure
2. ✅ Add file upload handling to edit_profile route
3. ✅ Update profile.html to display uploaded photos
4. ✅ Add privacy toggle UI
5. ✅ Implement privacy enforcement logic
6. ✅ Enhanced favorites display

**Estimated Time:** 2-3 hours for complete Phase 1

---

## 📝 Notes

- All database migrations will be handled automatically by SQLAlchemy
- Backward compatibility maintained (existing profiles won't break)
- Mobile-responsive design for all new features
- Accessibility (ARIA labels, keyboard navigation)
- i18n ready (future internationalization)

---

**Last Updated:** November 2025
**Status:** Ready for Phase 1 Implementation
**Next Review:** After Phase 1 completion
