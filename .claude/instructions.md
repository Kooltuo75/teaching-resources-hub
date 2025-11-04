# Teaching Resources Project - Claude Instructions

## ⚠️ CRITICAL WORKFLOW REQUIREMENT
**ALWAYS follow this process before implementing any feature or making changes:**
1. Create a detailed proposed plan for the task
2. Present the plan to the user
3. Ask for approval with "Y" (proceed) or "N" (revise)
4. If the user responds "N", ask what they want to change
5. Only proceed with implementation after receiving "Y" approval

## Project Overview
This project is a comprehensive teaching support system that gathers teaching-related resources and helps teachers in many ways. It is designed to support educators across all subjects, grade levels, and teaching contexts.

## Project Scope
- **Features**: All teaching-related tools (lesson planning, resource management, grading, quiz creation, curriculum development, scheduling, student tracking, content generation, etc.)
- **Subjects**: All subjects (Math, Science, Language Arts, Social Studies, Arts, Physical Education, etc.)
- **Grade Levels**: All levels (K-12, Higher Education, Professional Development, Special Education)
- **Use Cases**: Classroom teaching, remote learning, hybrid environments, homeschooling support

## Technology Stack
**Primary**: Python-based development for rapid prototyping and Claude integration
- **Web Framework**: Flask or FastAPI for web applications
- **Frontend**: HTML/CSS/JavaScript (vanilla or minimal frameworks for simplicity)
- **Data Storage**: SQLite for simple database needs, JSON/CSV for resource files
- **AI Integration**: Direct Claude API integration for content generation and assistance
- **Additional**: Markdown for documentation, Jinja2 for templates

**Rationale**: Python provides the easiest development process with Claude Code, excellent library support for educational tools, and straightforward AI integration.

## Coding Standards

### File Organization
- Keep resources organized by subject, grade level, or topic
- Use clear, descriptive file and folder names
- Maintain a logical directory structure

### Code Style
- Write clear, readable code with educational context in mind
- Add comments explaining educational concepts or methodologies
- Prioritize accessibility and ease of use for educators
- Follow Python PEP 8 style guidelines
- Use descriptive variable and function names
- Keep functions focused and modular

### Development Approach
- **Flexibility**: No strict coding preferences - use best judgment for each situation
- **Pragmatism**: Prioritize working solutions over perfect code
- **Iteration**: Build incrementally, get feedback, and refine
- **Simplicity**: Choose the simplest solution that meets the requirements

### Documentation
- Document all features with teacher-friendly explanations
- Include examples and use cases relevant to teaching scenarios
- Provide clear instructions for non-technical users

## Working with Educational Content
- Ensure all content is appropriate for educational settings
- Consider different grade levels and learning styles
- Respect copyright and licensing for educational materials
- Include attribution for any external resources

## Testing and Quality
- Test features with real teaching scenarios in mind
- Ensure accessibility for teachers with varying technical skills
- Validate educational content for accuracy

## Communication
- Use teacher-friendly language in user-facing content
- Avoid technical jargon when communicating with end users
- Provide helpful error messages and guidance

## Special Considerations
- Consider privacy and student data protection
- Ensure compliance with educational standards and regulations
- Design with classroom and remote teaching environments in mind
