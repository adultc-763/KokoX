from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, FileField, SelectField, IntegerField, FloatField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_ as db_or_
from datetime import datetime
import os
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Get absolute path for database
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'video_platform.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload directories exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'videos'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails'), exist_ok=True)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500))  # Made nullable since we use embed codes
    embed_code = db.Column(db.Text)  # Full embed code for videos
    thumbnail_url = db.Column(db.String(500))  # Direct image link
    duration = db.Column(db.Integer)  # in seconds
    category = db.Column(db.String(50))  # Category
    tags = db.Column(db.Text)  # Comma-separated tags
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    ad_revenue = db.Column(db.Float, default=0.0)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#007bff')  # Hex color code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WebsiteConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    primary_color = db.Column(db.String(7), default='#007bff')
    secondary_color = db.Column(db.String(7), default='#6c757d')
    background_color = db.Column(db.String(7), default='#ffffff')
    text_color = db.Column(db.String(7), default='#212529')
    css_code = db.Column(db.Text)  # Custom CSS
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'banner', 'native', 'social', 'popunder'
    code = db.Column(db.Text)  # Adsterra code
    is_active = db.Column(db.Boolean, default=True)
    impressions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Adsterra specific codes
    banner_code = db.Column(db.Text, default='''<script>
  atOptions = {
    'key' : '8222901a4a0a0abca1bf6e66669f066d',
    'format' : 'iframe',
    'height' : 90,
    'width' : 728,
    'params' : {}
  };
</script>
<script src="https://www.highperformanceformat.com/8222901a4a0a0abca1bf6e66669f066d/invoke.js"></script>''')
    
    native_code = db.Column(db.Text, default='''<script async="async" data-cfasync="false" src="https://pl27495792.profitablecpmratenetwork.com/8e51db288c92c2ddbe02fec1d76fb9ae/invoke.js"></script>
<div id="container-8e51db288c92c2ddbe02fec1d76fb9ae"></div>''')
    
    social_code = db.Column(db.Text, default='''<script src="https://pl27495784.profitablecpmratenetwork.com/b0/db/62/b0db62ad1f1a1d4102ccae80a8ecdf4a.js"></script>''')
    
    popunder_code = db.Column(db.Text, default='''<script src="https://pl27466028.profitablecpmratenetwork.com/1c/ec/ba/1cecba33959a73dc0225a98248e1e330.js"></script>''')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class VideoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    embed_code = TextAreaField('Embed Code', validators=[DataRequired()], description='Use this for YouTube, Vimeo, etc.')
    thumbnail_url = StringField('Thumbnail URL (image link)', validators=[Length(max=500)])
    duration = IntegerField('Duration (seconds)', validators=[NumberRange(min=1)])
    category = SelectField('Category', coerce=str)
    tags = StringField('Tags (comma separated)', description='Enter tags separated by commas')

class AdForm(FlaskForm):
    name = StringField('Ad Name', validators=[DataRequired(), Length(max=100)])
    type = SelectField('Ad Type', choices=[
        ('banner', 'Banner Ad (728x90)'),
        ('native', 'Native Banner'),
        ('social', 'Social Bar'),
        ('popunder', 'Popunder Ad')
    ], validators=[DataRequired()])
    is_active = BooleanField('Enable Ad')
    
    # Adsterra codes
    banner_code = TextAreaField('Banner Code')
    native_code = TextAreaField('Native Code')
    social_code = TextAreaField('Social Bar Code')
    popunder_code = TextAreaField('Popunder Code')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    display_name = StringField('Display Name', validators=[DataRequired(), Length(max=100)])
    color = StringField('Color', validators=[DataRequired()], description='Hex color code (e.g., #007bff)')

class ThemeForm(FlaskForm):
    name = StringField('Theme Name', validators=[DataRequired(), Length(max=100)])
    primary_color = StringField('Primary Color', validators=[DataRequired()], description='Hex color code')
    secondary_color = StringField('Secondary Color', validators=[DataRequired()], description='Hex color code')
    background_color = StringField('Background Color', validators=[DataRequired()], description='Hex color code')
    text_color = StringField('Text Color', validators=[DataRequired()], description='Hex color code')
    css_code = TextAreaField('Custom CSS', description='Additional CSS rules')

class ConfigForm(FlaskForm):
    site_title = StringField('Site Title', validators=[DataRequired()])
    site_description = TextAreaField('Site Description')
    welcome_message = TextAreaField('Welcome Message')
    footer_text = StringField('Footer Text')

# Routes
@app.context_processor
def inject_theme():
    active_theme = Theme.query.filter_by(is_active=True).first()
    configs = WebsiteConfig.query.all()
    config_dict = {config.key: config.value for config in configs}
    categories = Category.query.order_by(Category.display_name.asc()).all()
    
    return {
        'active_theme': active_theme,
        'configs': config_dict,
        'categories': categories
    }

@app.context_processor
def inject_ads():
    ads = Ad.query.filter_by(is_active=True).all()
    ad_codes = {}
    for ad in ads:
        ad_codes[ad.type] = ad
    
    # Increment impressions
    for ad in ads:
        ad.impressions += 1
        db.session.commit()
    
    return {'ads': ad_codes}

@app.route('/age-verify')
def age_verification():
    # Don't redirect if already on age verification page
    if request.referrer and 'age-verify' in request.referrer:
        return render_template('age_verify.html')
    
    # Check if already verified
    age_verified = request.cookies.get('age_verified')
    if age_verified == 'true':
        return redirect(url_for('index'))
    
    return render_template('age_verify.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/')
def index():
    # Check age verification (but not if coming from age verification page)
    age_verified = request.cookies.get('age_verified')
    if not age_verified or age_verified != 'true':
        return redirect(url_for('age_verification'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '')
    
    # Build query
    query = Video.query
    
    # Apply search filter
    if search:
        query = query.filter(
            db_or_(
                Video.title.contains(search),
                Video.description.contains(search),
                Video.tags.contains(search)
            )
        )
    
    # Apply category filter (filter by category name string)
    if category_filter:
        query = query.filter(Video.category == category_filter)
    
    # Apply pagination
    videos = query.order_by(Video.created_at.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    
    return render_template('index.html', videos=videos, search=search, category_filter=category_filter)

@app.route('/video/<int:video_id>')
def watch_video(video_id):
    # Check age verification
    age_verified = request.cookies.get('age_verified')
    if not age_verified or age_verified != 'true':
        return redirect(url_for('age_verification'))
    
    video = Video.query.get_or_404(video_id)
    if not video.is_published:
        flash('This video is not available.')
        return redirect(url_for('index'))
    
    # Increment view count
    video.views += 1
    db.session.commit()
    
    # Get related videos (same category or similar tags)
    related_videos = []
    if video.category:
        # Videos from same category (excluding current video)
        related_videos = Video.query.filter(
            Video.category == video.category,
            Video.id != video.id,
            Video.is_published == True
        ).order_by(Video.created_at.desc()).limit(6).all()
    
    # If not enough from category, add videos with similar tags
    if len(related_videos) < 6 and video.tags:
        video_tags = [tag.strip() for tag in video.tags.split(',')]
        for tag in video_tags[:3]:  # Check up to 3 tags
            tag_videos = Video.query.filter(
                Video.tags.contains(tag),
                Video.id != video.id,
                Video.is_published == True
            ).order_by(Video.created_at.desc()).limit(3).all()
            
            for tag_video in tag_videos:
                if tag_video not in related_videos and len(related_videos) < 6:
                    related_videos.append(tag_video)
    
    pre_roll_ad = Ad.query.filter_by(type='pre_roll', is_active=True).first()
    banner_ad = Ad.query.filter_by(type='banner', is_active=True).first()
    
    return render_template('watch.html', video=video, related_videos=related_videos, pre_roll_ad=pre_roll_ad, banner_ad=banner_ad)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin'))
        flash('Invalid username or password')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    videos = Video.query.order_by(Video.created_at.desc()).all()
    total_views = db.session.query(db.func.sum(Video.views)).scalar() or 0
    total_revenue = db.session.query(db.func.sum(Video.ad_revenue)).scalar() or 0
    
    return render_template('admin.html', videos=videos, total_views=total_views, total_revenue=total_revenue)

@app.route('/admin/upload', methods=['GET', 'POST'])
@login_required
def upload_video():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    form = VideoForm()
    # Populate category choices
    categories = Category.query.all()
    form.category.choices = [(cat.name, cat.display_name) for cat in categories]
    
    if form.validate_on_submit():
        # Create video with embed code
        video = Video(
            title=form.title.data,
            description=form.description.data,
            embed_code=form.embed_code.data,
            thumbnail_url=form.thumbnail_url.data,
            duration=form.duration.data,
            category=form.category.data,
            tags=form.tags.data
        )
        db.session.add(video)
        db.session.commit()
        
        flash('Video uploaded successfully!')
        return redirect(url_for('admin'))
    
    return render_template('upload.html', form=form)

@app.route('/admin/edit-video/<int:video_id>', methods=['GET', 'POST'])
@login_required
def edit_video(video_id):
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    video = Video.query.get_or_404(video_id)
    form = VideoForm(obj=video)
    
    # Populate category choices
    categories = Category.query.all()
    form.category.choices = [(cat.name, cat.display_name) for cat in categories]
    
    if form.validate_on_submit():
        video.title = form.title.data
        video.description = form.description.data
        video.embed_code = form.embed_code.data
        video.thumbnail_url = form.thumbnail_url.data
        video.duration = form.duration.data
        video.category = form.category.data
        video.tags = form.tags.data
        db.session.commit()
        
        flash('Video updated successfully!')
        return redirect(url_for('admin'))
    
    return render_template('edit_video.html', form=form, video=video)

@app.route('/admin/categories')
@login_required
def manage_categories():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    categories = Category.query.order_by(Category.display_name.asc()).all()
    return render_template('categories.html', categories=categories)

@app.route('/admin/categories/new', methods=['GET', 'POST'])
@login_required
def create_category():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            display_name=form.display_name.data,
            color=form.color.data
        )
        db.session.add(category)
        db.session.commit()
        
        flash('Category created successfully!')
        return redirect(url_for('manage_categories'))
    
    return render_template('category_form.html', form=form)

@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.display_name = form.display_name.data
        category.color = form.color.data
        db.session.commit()
        
        flash('Category updated successfully!')
        return redirect(url_for('manage_categories'))
    
    return render_template('category_form.html', form=form, category=category)

@app.route('/admin/categories/delete/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/admin/ads')
@login_required
def manage_ads():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    ads_list = Ad.query.all()
    # Convert to dictionary format expected by template
    ads_dict = {}
    for ad in ads_list:
        ads_dict[ad.type] = ad
    
    return render_template('ads.html', ads=ads_dict)

@app.route('/admin/ads/new', methods=['GET', 'POST'])
@login_required
def create_ad():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    form = AdForm()
    if form.validate_on_submit():
        ad = Ad(
            name=form.name.data,
            type=form.type.data,
            is_active=form.is_active.data
        )
        db.session.add(ad)
        db.session.commit()
        
        flash('Ad created successfully!')
        return redirect(url_for('manage_ads'))
    
    return render_template('ad_form.html', form=form)

@app.route('/admin/ads/<int:ad_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ad(ad_id):
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    ad = Ad.query.get_or_404(ad_id)
    form = AdForm(obj=ad)
    
    if form.validate_on_submit():
        ad.name = form.name.data
        ad.type = form.type.data
        ad.is_active = form.is_active.data
        db.session.commit()
        
        flash('Ad updated successfully!')
        return redirect(url_for('manage_ads'))
    
    return render_template('ad_form.html', form=form, ad=ad)

@app.route('/admin/ads/<int:ad_id>/delete', methods=['DELETE'])
@login_required
def delete_ad(ad_id):
    if not current_user.is_admin:
        return jsonify({'status': 'error', 'message': 'Access denied'})
    
    ad = Ad.query.get_or_404(ad_id)
    db.session.delete(ad)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/api/track-engagement', methods=['POST'])
def track_engagement():
    data = request.get_json()
    video_id = data.get('video_id')
    watch_time = data.get('watch_time', 0)
    
    if video_id:
        video = Video.query.get(video_id)
        if video:
            # Calculate ad revenue based on watch time
            # Simple formula: $0.01 per 30 seconds of watch time
            revenue_increment = (watch_time // 30) * 0.01
            video.ad_revenue += revenue_increment
            db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/admin/delete-video/<int:video_id>', methods=['DELETE'])
@login_required
def delete_video(video_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    video = Video.query.get_or_404(video_id)
    
    # No need to delete files since we're using URLs
    db.session.delete(video)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/admin/themes')
@login_required
def manage_themes():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    themes = Theme.query.all()
    return render_template('themes.html', themes=themes)

@app.route('/admin/themes/new', methods=['GET', 'POST'])
@login_required
def create_theme():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    form = ThemeForm()
    if form.validate_on_submit():
        # Check if theme name already exists
        existing_theme = Theme.query.filter_by(name=form.name.data).first()
        if existing_theme:
            flash('Theme name already exists! Please choose a different name.')
            return render_template('theme_form.html', form=form)
        
        # Set all other themes as inactive
        Theme.query.update({'is_active': False})
        
        theme = Theme(
            name=form.name.data,
            primary_color=form.primary_color.data,
            secondary_color=form.secondary_color.data,
            background_color=form.background_color.data,
            text_color=form.text_color.data,
            css_code=form.css_code.data,
            is_active=True
        )
        db.session.add(theme)
        db.session.commit()
        
        flash('Theme created successfully!')
        return redirect(url_for('manage_themes'))
    
    return render_template('theme_form.html', form=form)

@app.route('/admin/themes/activate/<int:theme_id>', methods=['POST'])
@login_required
def activate_theme(theme_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    # Set all themes as inactive
    Theme.query.update({'is_active': False})
    
    # Activate selected theme
    theme = Theme.query.get_or_404(theme_id)
    theme.is_active = True
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/admin/themes/delete/<int:theme_id>', methods=['DELETE'])
@login_required
def delete_theme(theme_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    theme = Theme.query.get_or_404(theme_id)
    
    # Don't allow deletion of active theme
    if theme.is_active:
        return jsonify({'error': 'Cannot delete active theme'}), 400
    
    db.session.delete(theme)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@app.route('/admin/settings')
@login_required
def website_settings():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    # Get current settings
    settings = {}
    configs = WebsiteConfig.query.all()
    for config in configs:
        settings[config.key] = config.value
    
    form = ConfigForm(data=settings)
    return render_template('settings.html', form=form)

@app.route('/admin/settings', methods=['POST'])
@login_required
def save_settings():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('index'))
    
    form = ConfigForm()
    if form.validate_on_submit():
        # Save each setting
        settings = {
            'site_title': form.site_title.data,
            'site_description': form.site_description.data,
            'welcome_message': form.welcome_message.data,
            'footer_text': form.footer_text.data
        }
        
        for key, value in settings.items():
            config = WebsiteConfig.query.filter_by(key=key).first()
            if config:
                config.value = value
                config.updated_at = datetime.utcnow()
            else:
                config = WebsiteConfig(key=key, value=value, description=key.replace('_', ' ').title())
                db.session.add(config)
        
        db.session.commit()
        flash('Settings saved successfully!')
    
    return redirect(url_for('website_settings'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Create default Adsterra ads if not exists
        ad_types = [
            ('banner', 'Banner Ad (728x90)'),
            ('native', 'Native Banner'),
            ('social', 'Social Bar'),
            ('popunder', 'Popunder Ad')
        ]
        
        for ad_type, ad_name in ad_types:
            existing_ad = Ad.query.filter_by(type=ad_type).first()
            if not existing_ad:
                new_ad = Ad(
                    name=ad_name,
                    type=ad_type,
                    is_active=True
                )
                db.session.add(new_ad)
        
        db.session.commit()
        
        app.run(debug=True)
