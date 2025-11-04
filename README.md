# Teaching Resources Hub

A comprehensive web application that provides teaching-related resources and tools to help educators across all subjects, grade levels, and teaching environments.

## Overview

Teaching Resources Hub is designed to support teachers with various tools and resources including:

- **Lesson Plan Generator** - Create comprehensive lesson plans with AI assistance
- **Resource Library** - Organize and search teaching materials
- **Quiz Creator** - Generate quizzes and assessments
- **Gradebook** - Track student progress and manage grades
- **Curriculum Planner** - Plan and organize curriculum
- **Student Tracker** - Monitor individual student progress

## Project Structure

```
Project 10 - Teach/
├── .claude/              # Claude Code instructions
├── app/                  # Main application package
│   ├── __init__.py      # Flask app initialization
│   ├── routes.py        # Web routes and endpoints
│   ├── templates/       # HTML templates
│   │   ├── base.html   # Base template with navigation
│   │   └── index.html  # Home page
│   └── static/          # Static assets
│       ├── css/        # Stylesheets
│       └── js/         # JavaScript files
├── data/                # Database and data files
├── utils/               # Utility functions
├── config.py            # Application configuration
├── requirements.txt     # Python dependencies
├── run.py              # Application entry point
└── README.md           # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "C:\Users\brent\OneDrive\Documents\ClaudeCode\Project 10 - Teach"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Open your browser**
   Navigate to: `http://127.0.0.1:5000`

## Configuration

The application can be configured through `config.py`:

- **SECRET_KEY**: Set via environment variable for production
- **DEBUG**: Currently enabled for development
- **CLAUDE_API_KEY**: Set via environment variable for AI features (future)

### Environment Variables

Create a `.env` file in the project root for sensitive configuration:

```env
SECRET_KEY=your-secret-key-here
CLAUDE_API_KEY=your-claude-api-key-here
```

## Development

### Adding New Features

1. Add route handlers in `app/routes.py`
2. Create corresponding templates in `app/templates/`
3. Add styles in `app/static/css/style.css`
4. Add JavaScript in `app/static/js/main.js`

### Database

Currently uses SQLite for simplicity. Database files will be stored in the `data/` directory.

## Technology Stack

- **Backend**: Python 3 with Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Template Engine**: Jinja2
- **Database**: SQLite (planned)
- **AI Integration**: Claude API (planned)

## Future Features

- AI-powered lesson plan generation
- Resource recommendation system
- Collaborative features for sharing materials
- Export capabilities (PDF, Word, etc.)
- Calendar integration
- Mobile app

## Contributing

This is a personal project. For suggestions or issues, please create an issue in the project repository.

## License

Copyright © 2025 Teaching Resources Hub. All rights reserved.

## Support

For questions or support, please refer to the project documentation or create an issue in the repository.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-03
