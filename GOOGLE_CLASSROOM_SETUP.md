# Google Classroom Integration Setup Guide

This guide will walk you through setting up Google Classroom integration for the Teaching Resources Hub.

## Prerequisites

- A Google account (preferably a Google Workspace for Education account)
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- Administrator access to your Teaching Resources Hub installation

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top
3. Click "NEW PROJECT"
4. Enter a project name (e.g., "Teaching Resources Hub")
5. Click "CREATE"

## Step 2: Enable Google Classroom API

1. In your Google Cloud project, go to **APIs & Services > Library**
2. Search for "Google Classroom API"
3. Click on it and click "ENABLE"
4. Also enable "People API" (for user profile information)

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services > OAuth consent screen**
2. Choose **External** user type (unless you have a Google Workspace organization)
3. Click "CREATE"

4. Fill in the required information:
   - **App name**: Teaching Resources Hub
   - **User support email**: Your email
   - **Developer contact email**: Your email
   - **App logo** (optional): Upload your app logo

5. Click "SAVE AND CONTINUE"

6. **Scopes**: Click "ADD OR REMOVE SCOPES" and add:
   - `.../auth/classroom.courses.readonly`
   - `.../auth/classroom.coursework.students`
   - `.../auth/classroom.announcements`
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`

7. Click "SAVE AND CONTINUE"

8. **Test users** (only needed for development):
   - Add your email and any other test users
   - Click "SAVE AND CONTINUE"

9. Review and click "BACK TO DASHBOARD"

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click "+ CREATE CREDENTIALS" at the top
3. Select "OAuth client ID"
4. Choose application type: **Web application**
5. Give it a name (e.g., "Teaching Resources Hub Web")

6. **Authorized redirect URIs**:
   - Add: `http://localhost:5000/google/callback` (for local development)
   - Add: `https://yourdomain.com/google/callback` (for production)

7. Click "CREATE"

8. **IMPORTANT**: Copy your Client ID and Client Secret
   - Keep these secure!
   - You'll need them in the next step

## Step 5: Configure Your Application

### Method 1: Environment Variables (Recommended)

Set environment variables:

```bash
# Windows (Command Prompt)
set GOOGLE_CLIENT_ID=your_client_id_here
set GOOGLE_CLIENT_SECRET=your_client_secret_here

# Windows (PowerShell)
$env:GOOGLE_CLIENT_ID="your_client_id_here"
$env:GOOGLE_CLIENT_SECRET="your_client_secret_here"

# Linux/Mac
export GOOGLE_CLIENT_ID="your_client_id_here"
export GOOGLE_CLIENT_SECRET="your_client_secret_here"
```

### Method 2: Direct Configuration

Edit `config.py` and replace the placeholders:

```python
GOOGLE_CLIENT_ID = 'your_actual_client_id_here'
GOOGLE_CLIENT_SECRET = 'your_actual_client_secret_here'
```

**⚠️ Security Warning**: Never commit actual credentials to version control!

## Step 6: Update Database Schema

Run the following to update your database with Google Classroom fields:

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

## Step 7: Restart Your Application

```bash
python run.py
```

## Step 8: Test the Integration

1. Log in to your Teaching Resources Hub account
2. Go to your profile page
3. Look for the "Connect Google Classroom" button
4. Click it and follow the Google OAuth flow
5. Grant the requested permissions
6. You should see "Successfully connected to Google Classroom!"

## Using Google Classroom Integration

### For Teachers:

1. **Browse resources** on the Resources page
2. **Click "Share to Classroom"** button on any resource
3. **Select your course** from the dropdown
4. **Choose how to share**:
   - **Announcement**: Post as a class announcement
   - **Material**: Add as course material
5. Click "Share"
6. Check your Google Classroom to see the shared resource!

### API Endpoints:

- `GET /api/google/courses` - Get your Google Classroom courses
- `POST /api/google/share-resource` - Share a resource as announcement
- `POST /api/google/create-material` - Add resource as course material

## Troubleshooting

### "Google Classroom integration is not configured"

- Make sure you've set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- Check that they're not set to the placeholder values

### "Invalid authentication state"

- Clear your browser cookies for localhost
- Try the OAuth flow again

### "Access blocked: This app's request is invalid"

- Check that your redirect URI in Google Cloud Console matches exactly
- Make sure you've enabled the Google Classroom API

### "Insufficient Permission"

- Verify all required scopes are added in OAuth consent screen
- Try disconnecting and reconnecting your Google account

### Token expired errors

- The app will automatically refresh tokens
- If issues persist, disconnect and reconnect Google Classroom

## Production Deployment

When deploying to production:

1. **Update redirect URI** in Google Cloud Console to your production URL
2. **Use environment variables** for credentials (never hard-code)
3. **Verify OAuth consent screen** is published (not in testing mode)
4. **Use HTTPS** for all production URLs
5. **Consider domain verification** in Google Search Console

## Security Best Practices

1. ✅ Store credentials in environment variables
2. ✅ Never commit credentials to git
3. ✅ Use HTTPS in production
4. ✅ Regularly rotate OAuth client secrets
5. ✅ Monitor API usage in Google Cloud Console
6. ✅ Implement rate limiting on your endpoints
7. ✅ Log authentication events for security auditing

## Additional Resources

- [Google Classroom API Documentation](https://developers.google.com/classroom)
- [OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Google API Scopes](https://developers.google.com/identity/protocols/oauth2/scopes)

## Support

If you encounter issues:

1. Check the application logs for detailed error messages
2. Verify your Google Cloud Console configuration
3. Test with a fresh browser session (incognito mode)
4. Review the Google Cloud Console quota/usage limits

## Quota Limits

Google Classroom API has the following default limits:

- **Queries per day**: 50,000 (can request increase)
- **Queries per 100 seconds per user**: 1,500

Monitor your usage in Google Cloud Console under **APIs & Services > Dashboard**.
