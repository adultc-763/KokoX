# Video Platform - Monetize Your Content 🚗💨

A complete video content platform with monetization features to help you earn money and achieve your dreams of owning a Benz and BMW!

## Features 🎯

### For Content Creators
- **Video Upload & Management**: Upload videos with custom thumbnails
- **Admin Dashboard**: Track views, revenue, and performance metrics
- **Ad Management**: Create and manage pre-roll, mid-roll, and banner ads
- **Revenue Tracking**: Real-time revenue calculation based on video engagement
- **Goal Tracking**: Visual progress towards your luxury car goals!

### For Viewers
- **Video Streaming**: Watch high-quality videos with adaptive player
- **Ad Experience**: Minimal, non-intrusive advertisements
- **Engagement**: Like and interact with content
- **Responsive Design**: Works perfectly on all devices

## Tech Stack 💻

- **Backend**: Python Flask
- **Database**: SQLite (with SQLAlchemy ORM)
- **Frontend**: Bootstrap 5 + HTML5/CSS3/JavaScript
- **Authentication**: Flask-Login
- **File Upload**: Werkzeug security

## Quick Start 🚀

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project**
   ```bash
   # Navigate to your project directory
   cd windsurf-project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the platform**
   - Main site: http://localhost:5000
   - Admin login: http://localhost:5000/login

### Default Admin Credentials
- **Username**: admin
- **Password**: admin123

## Usage Guide 📖

### For Admins

1. **Login to Admin Panel**
   - Go to `/login` and enter admin credentials
   - Access the dashboard at `/admin`

2. **Upload Videos**
   - Click "Upload Video" in the admin panel
   - Fill in video details (title, description)
   - Upload video file (MP4, WebM, OGG - max 500MB)
   - Optionally upload a thumbnail image

3. **Manage Ads**
   - Go to "Manage Ads" in the admin panel
   - Create new ads with different types:
     - **Pre-roll**: Video ads before content
     - **Mid-roll**: Video ads during content
     - **Banner**: Display ads on video pages
   - Set CPM (Cost Per Mille) rates

4. **Track Performance**
   - View total views and revenue on dashboard
   - Monitor progress towards car goals
   - Track individual video performance

### For Viewers

1. **Browse Videos**
   - Visit the homepage to see latest videos
   - Click on any video to watch

2. **Watch Experience**
   - Videos play with minimal ads
   - Pre-roll ads may appear (5 seconds or skippable)
   - Banner ads appear on the side

## Monetization 💰

### How It Works
- **Ad Revenue**: Earn money from advertisements shown during video playback
- **CPM Model**: Revenue calculated as (Views ÷ 1000) × CPM rate
- **Engagement Tracking**: Revenue increases with longer watch times

### Revenue Calculator
Use the built-in revenue calculator in the admin panel to estimate earnings:
- Input expected views
- Set your average CPM rate
- See projected revenue

### Goal Tracking
Track your progress towards luxury goals:
- **Mercedes-Benz Goal**: $50,000
- **BMW Goal**: $45,000
- Visual progress bars show your achievement percentage

## File Structure 📁

```
windsurf-project/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── instance/
│   └── video_platform.db # SQLite database
├── static/
│   ├── uploads/
│   │   ├── videos/       # Uploaded video files
│   │   └── thumbnails/    # Video thumbnails
│   ├── css/              # Custom CSS files
│   └── js/               # Custom JavaScript files
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Homepage
    ├── watch.html        # Video player page
    ├── login.html        # Admin login
    ├── admin.html        # Admin dashboard
    ├── upload.html       # Video upload form
    ├── ads.html          # Ad management
    └── ad_form.html      # Ad creation form
```

## Configuration ⚙️

### Environment Variables
Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
```

### Database
- Uses SQLite by default (`instance/video_platform.db`)
- Database is created automatically on first run
- Admin user is created automatically

### File Uploads
- **Max file size**: 500MB
- **Supported video formats**: MP4, WebM, OGG
- **Supported image formats**: JPG, PNG (for thumbnails)
- **Upload directory**: `static/uploads/`

## Security 🔒

- Admin authentication required for uploads and management
- File upload security with filename sanitization
- CSRF protection on all forms
- SQL injection prevention with SQLAlchemy ORM

## Development 🛠️

### Adding New Features
1. Add routes to `app.py`
2. Create corresponding templates in `templates/`
3. Update database models if needed
4. Test thoroughly

### Customization
- Modify `templates/base.html` for branding changes
- Update CSS in `static/css/` for styling
- Configure app settings in `app.py`

## Troubleshooting 🔧

### Common Issues

1. **Database not found**
   - Ensure `instance/` directory exists
   - Run the app once to create the database

2. **Upload errors**
   - Check file size limits (max 500MB)
   - Verify file formats are supported
   - Ensure upload directories have proper permissions

3. **Login issues**
   - Use default credentials: admin/admin123
   - Check database contains admin user

4. **Video not playing**
   - Verify video file exists in `static/uploads/videos/`
   - Check browser supports video format
   - Ensure file paths are correct

## Support 📞

For issues or questions:
1. Check this README first
2. Review error logs in the console
3. Verify all dependencies are installed
4. Test with different browsers

## License 📄

This project is for educational and personal use. Modify and use as needed for your video content platform needs!

---

**Start your journey to luxury cars today!** 🏎️💨

*Every view brings you closer to your dreams. Keep creating amazing content!*
