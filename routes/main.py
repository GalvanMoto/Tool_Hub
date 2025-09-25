"""
Main routes for ToolHub application.
Handles landing page, authentication, and general pages.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Landing page with hero, features, pricing sections."""
    return render_template('index.html')


@main.route('/home')
def home():
    """Simple home page."""
    return render_template('home.html')


@main.route('/pricing')
def pricing():
    """Pricing page with subscription plans."""
    # TODO: Create pricing.html template
    return render_template('pricing.html')


@main.route('/about')
def about():
    """About page."""
    # TODO: Create about.html template
    return render_template('about.html')


@main.route('/contact')
def contact():
    """Contact page."""
    # TODO: Create contact.html template
    return render_template('contact.html')


@main.route('/privacy')
def privacy():
    """Privacy policy page."""
    # TODO: Create privacy.html template
    return render_template('privacy.html')


@main.route('/help')
def help():
    """Help center page."""
    # TODO: Create help.html template
    return render_template('help.html')


@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - requires authentication."""
    # TODO: Create dashboard.html template
    return render_template('dashboard/index.html', user=current_user)


@main.route('/tools')
def tools():
    """All Tools page - comprehensive view of all available tools."""
    
    # Productivity Tools (from tools blueprint)
    productivity_tools = [
        {
            'name': 'PDF Merge', 
            'description': 'Combine multiple PDF files into one document',
            'icon': '📄',
            'url': '/tools/pdf-merge',
            'category': 'PDF'
        },
        {
            'name': 'Image Resizer', 
            'description': 'Resize images to specific dimensions',
            'icon': '🖼️',
            'url': '/tools/image-resizer',
            'category': 'Image'
        },
        {
            'name': 'QR Generator', 
            'description': 'Create QR codes for text, URLs, and more',
            'icon': '📱',
            'url': '/tools/qr-generator',
            'category': 'QR Code'
        },
        {
            'name': 'Pro QR Generator', 
            'description': 'Advanced QR code generation with custom styles',
            'icon': '✨',
            'url': '/tools/qr-generator-pro',
            'category': 'QR Code'
        },
        {
            'name': 'Traffic Analytics', 
            'description': 'Analyze website traffic patterns and metrics',
            'icon': '📊',
            'url': '/tools/traffic-analytics',
            'category': 'SEO'
        },
        {
            'name': 'Keyword Research', 
            'description': 'Find and analyze SEO keywords',
            'icon': '🔍',
            'url': '/tools/keyword-research',
            'category': 'SEO'
        }
    ]
    
    # AI Tools (from ai_tools blueprint)
    ai_tools = [
        {
            'name': 'Blog Generator', 
            'description': 'Generate complete, SEO-optimized blog posts',
            'icon': '📝',
            'url': '/ai/blog-generator',
            'category': 'AI Content'
        },
        {
            'name': 'Article Summarizer', 
            'description': 'Summarize long articles and documents',
            'icon': '📋',
            'url': '/ai/article-summarizer',
            'category': 'AI Content'
        },
        {
            'name': 'Paraphraser', 
            'description': 'Rewrite content while maintaining meaning',
            'icon': '🔄',
            'url': '/ai/paraphraser',
            'category': 'AI Content'
        },
        {
            'name': 'Grammar Checker', 
            'description': 'Check and improve grammar and writing',
            'icon': '✅',
            'url': '/ai/grammar-checker',
            'category': 'AI Content'
        },
        {
            'name': 'Headline Generator', 
            'description': 'Create compelling headlines and titles',
            'icon': '📰',
            'url': '/ai/headline-generator',
            'category': 'AI Content'
        },
        {
            'name': 'Meta Description', 
            'description': 'Generate SEO meta descriptions',
            'icon': '🏷️',
            'url': '/ai/meta-description',
            'category': 'AI SEO'
        },
        {
            'name': 'Product Description', 
            'description': 'Create compelling product descriptions',
            'icon': '🛍️',
            'url': '/ai/product-description',
            'category': 'AI Content'
        },
        {
            'name': 'Email Writer', 
            'description': 'Generate professional emails',
            'icon': '📧',
            'url': '/ai/email-writer',
            'category': 'AI Content'
        },
        {
            'name': 'Social Media', 
            'description': 'Create social media captions and posts',
            'icon': '📱',
            'url': '/ai/social-media',
            'category': 'AI Content'
        },
        {
            'name': 'Ad Copy Generator', 
            'description': 'Generate compelling advertisement copy',
            'icon': '📢',
            'url': '/ai/ad-copy',
            'category': 'AI Marketing'
        }
    ]
    
    return render_template('tools/all_tools.html', 
                         productivity_tools=productivity_tools,
                         ai_tools=ai_tools)


@main.route('/tools/')
def tools_index():
    """Tools listing page redirect."""
    # Redirect to the comprehensive tools page
    return redirect(url_for('main.tools'))


@main.route('/blog')
def blog():
    """Blog page."""
    return render_template('blog/index.html')