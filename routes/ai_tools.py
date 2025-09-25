"""
AI Content Tools routes for ToolHub application.
Handles AI-powered content generation with freemium limitations.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from models import db, User, Usage
from services.gemini_service import gemini_service
import logging

# Configure logging
logger = logging.getLogger(__name__)

ai_tools = Blueprint('ai_tools', __name__, url_prefix='/ai')


def check_usage_limit(tool_name: str) -> dict:
    """Check if user can use the AI tool based on freemium limits."""
    if not current_user.is_authenticated:
        return {'allowed': False, 'message': 'Please login to use AI tools', 'redirect': 'auth.login'}
    
    if current_user.is_premium():
        return {'allowed': True, 'message': 'Premium user - unlimited access'}
    
    # Check daily usage for free users
    daily_usage = current_user.get_daily_usage_count()
    if daily_usage >= 3:
        return {
            'allowed': False, 
            'message': f'Daily limit reached ({daily_usage}/3). Upgrade to Premium for unlimited access.',
            'redirect': 'auth.upgrade'
        }
    
    return {'allowed': True, 'message': f'Free usage: {daily_usage + 1}/3 today'}


def record_usage(tool_name: str, input_data: str = None, output_data: str = None):
    """Record tool usage for freemium tracking."""
    if current_user.is_authenticated and not current_user.is_premium():
        try:
            usage = Usage(
                user_id=current_user.id,
                tool_name=tool_name,
                used_at=datetime.utcnow(),
                input_data=input_data[:500] if input_data else None,  # Truncate for storage
                output_data=output_data[:1000] if output_data else None
            )
            db.session.add(usage)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")


@ai_tools.route('/generate', methods=['POST'])
@login_required
def ai_generate():
    """Generic AI content generation endpoint."""
    try:
        data = request.json
        prompt = data.get("prompt")
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        # Check usage limits
        usage_check = check_usage_limit("ai_generate")
        if not usage_check['allowed']:
            return jsonify({"error": usage_check['message']}), 403
        
        # Generate content using Gemini
        response = gemini_service.generate_content(prompt)
        
        if response.startswith("AI service is currently unavailable"):
            return jsonify({"error": response}), 503
        
        # Record usage
        record_usage("ai_generate", prompt, response)
        
        return jsonify({"output": response})
        
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        return jsonify({"error": "Content generation failed"}), 500


@ai_tools.route('/test')
@login_required
def ai_test():
    """Test page for AI generation."""
    return render_template('ai_test.html')


@ai_tools.route('/')
def dashboard():
    """AI Tools dashboard."""
    if current_user.is_authenticated:
        daily_usage = current_user.get_daily_usage_count()
        usage_limit = "Unlimited" if current_user.is_premium() else "3"
        
        return render_template('ai_tools/dashboard.html', 
                             daily_usage=daily_usage,
                             usage_limit=usage_limit)
    else:
        return render_template('ai_tools/dashboard.html', 
                             daily_usage=0,
                             usage_limit="3")


@ai_tools.route('/blog-generator', methods=['GET', 'POST'])
@login_required
def blog_generator():
    """AI Blog Post Generator."""
    if request.method == 'POST':
        # Check usage limit
        limit_check = check_usage_limit('blog_generator')
        if not limit_check['allowed']:
            return jsonify({
                'success': False, 
                'error': limit_check['message'],
                'redirect': limit_check.get('redirect')
            })
        
        try:
            topic = request.form.get('topic', '').strip()
            keywords = request.form.get('keywords', '').strip()
            tone = request.form.get('tone', 'professional')
            word_count = int(request.form.get('word_count', 800))
            
            if not topic:
                return jsonify({'success': False, 'error': 'Topic is required'})
            
            # Generate blog post
            result = gemini_service.generate_blog_post(topic, keywords, tone, word_count)
            
            # Record usage
            record_usage('blog_generator', f"Topic: {topic}, Keywords: {keywords}", result[:200])
            
            return jsonify({
                'success': True, 
                'result': result,
                'message': limit_check['message']
            })
            
        except Exception as e:
            logger.error(f"Blog generator error: {e}")
            return jsonify({'success': False, 'error': 'Generation failed. Please try again.'})
    
    return render_template('ai_tools/blog_generator.html')


@ai_tools.route('/article-summarizer', methods=['GET', 'POST']) 
@login_required
def article_summarizer():
    """AI Article Summarizer."""
    if request.method == 'POST':
        # Check usage limit
        limit_check = check_usage_limit('article_summarizer')
        if not limit_check['allowed']:
            return jsonify({
                'success': False,
                'error': limit_check['message'],
                'redirect': limit_check.get('redirect')
            })
        
        try:
            content = request.form.get('content', '').strip()
            summary_type = request.form.get('summary_type', 'paragraph')
            
            if not content:
                return jsonify({'success': False, 'error': 'Content is required'})
            
            if len(content) < 100:
                return jsonify({'success': False, 'error': 'Content is too short to summarize'})
            
            # Generate summary
            result = gemini_service.summarize_article(content, summary_type)
            
            # Record usage
            record_usage('article_summarizer', f"Length: {len(content)} chars", result[:200])
            
            return jsonify({
                'success': True,
                'result': result,
                'message': limit_check['message']
            })
            
        except Exception as e:
            logger.error(f"Summarizer error: {e}")
            return jsonify({'success': False, 'error': 'Summarization failed. Please try again.'})
    
    return render_template('ai_tools/article_summarizer.html')


@ai_tools.route('/paraphraser', methods=['GET', 'POST'])
@login_required  
def paraphraser():
    """AI Paraphrasing Tool."""
    if request.method == 'POST':
        # Check usage limit
        limit_check = check_usage_limit('paraphraser')
        if not limit_check['allowed']:
            return jsonify({
                'success': False,
                'error': limit_check['message'],
                'redirect': limit_check.get('redirect')
            })
        
        try:
            text = request.form.get('text', '').strip()
            style = request.form.get('style', 'formal')
            
            if not text:
                return jsonify({'success': False, 'error': 'Text is required'})
            
            # Generate paraphrase
            result = gemini_service.paraphrase_text(text, style)
            
            # Record usage
            record_usage('paraphraser', f"Style: {style}, Length: {len(text)}", result[:200])
            
            return jsonify({
                'success': True,
                'result': result,
                'message': limit_check['message']
            })
            
        except Exception as e:
            logger.error(f"Paraphraser error: {e}")
            return jsonify({'success': False, 'error': 'Paraphrasing failed. Please try again.'})
    
    return render_template('ai_tools/paraphraser.html')


@ai_tools.route('/grammar-checker', methods=['GET', 'POST'])
@login_required
def grammar_checker():
    """AI Grammar & Style Checker.""" 
    if request.method == 'POST':
        # Check usage limit
        limit_check = check_usage_limit('grammar_checker')
        if not limit_check['allowed']:
            return jsonify({
                'success': False,
                'error': limit_check['message'],
                'redirect': limit_check.get('redirect')
            })
        
        try:
            text = request.form.get('text', '').strip()
            
            if not text:
                return jsonify({'success': False, 'error': 'Text is required'})
            
            # Check grammar and style
            result = gemini_service.check_grammar_and_style(text)
            
            # Record usage
            record_usage('grammar_checker', f"Length: {len(text)} chars", result[:200])
            
            return jsonify({
                'success': True,
                'result': result,
                'message': limit_check['message']
            })
            
        except Exception as e:
            logger.error(f"Grammar checker error: {e}")
            return jsonify({'success': False, 'error': 'Grammar check failed. Please try again.'})
    
    return render_template('ai_tools/grammar_checker.html')


@ai_tools.route('/headline-generator', methods=['GET', 'POST'])
@login_required
def headline_generator():
    """AI Headline Generator."""
    if request.method == 'POST':
        # Check usage limit  
        limit_check = check_usage_limit('headline_generator')
        if not limit_check['allowed']:
            return jsonify({
                'success': False,
                'error': limit_check['message'],
                'redirect': limit_check.get('redirect')
            })
        
        try:
            topic = request.form.get('topic', '').strip()
            count = int(request.form.get('count', 10))
            
            if not topic:
                return jsonify({'success': False, 'error': 'Topic is required'})
            
            # Generate headlines
            result = gemini_service.generate_headlines(topic, count)
            
            # Record usage
            record_usage('headline_generator', f"Topic: {topic}, Count: {count}", result[:200])
            
            return jsonify({
                'success': True,
                'result': result,
                'message': limit_check['message']
            })
            
        except Exception as e:
            logger.error(f"Headline generator error: {e}")
            return jsonify({'success': False, 'error': 'Headline generation failed. Please try again.'})
    
    return render_template('ai_tools/headline_generator.html')


@ai_tools.route('/meta-description', methods=['GET', 'POST'])
@login_required
def meta_description():
    """AI Meta Description Generator."""
    if request.method == 'POST':
        # Check usage limit
        limit_check = check_usage_limit('meta_description_generator') 
        if not limit_check['allowed']:
            return jsonify({
                'success': False,
                'error': limit_check['message'],
                'redirect': limit_check.get('redirect')
            })
        
        try:
            title = request.form.get('title', '').strip()
            keywords = request.form.get('keywords', '').strip()
            
            if not title:
                return jsonify({'success': False, 'error': 'Title is required'})
            
            # Generate meta descriptions
            result = gemini_service.generate_meta_description(title, keywords)
            
            # Record usage
            record_usage('meta_description_generator', f"Title: {title}, Keywords: {keywords}", result[:200])
            
            return jsonify({
                'success': True,
                'result': result,
                'message': limit_check['message']
            })
            
        except Exception as e:
            logger.error(f"Meta description error: {e}")
            return jsonify({'success': False, 'error': 'Meta description generation failed. Please try again.'})
    
    return render_template('ai_tools/meta_description.html')


@ai_tools.route('/product-description', methods=['GET', 'POST'])
@login_required
def product_description():
    """AI Product Description Generator."""
    if request.method == 'POST':
        # Check usage limit
        limit_check = check_usage_limit('product_description_generator')
        if not limit_check['allowed']:
            return jsonify({
                'success': False,
                'error': limit_check['message'], 
                'redirect': limit_check.get('redirect')
            })
        
        try:
            product_name = request.form.get('product_name', '').strip()
            features = request.form.get('features', '').strip()
            tone = request.form.get('tone', 'professional')
            
            if not product_name:
                return jsonify({'success': False, 'error': 'Product name is required'})
            
            # Generate product description
            result = gemini_service.generate_product_description(product_name, features, tone)
            
            # Record usage
            record_usage('product_description_generator', f"Product: {product_name}", result[:200])
            
            return jsonify({
                'success': True,
                'result': result,
                'message': limit_check['message']
            })
            
        except Exception as e:
            logger.error(f"Product description error: {e}")
            return jsonify({'success': False, 'error': 'Product description generation failed. Please try again.'})
    
    return render_template('ai_tools/product_description.html')


@ai_tools.route('/email-writer', methods=['GET', 'POST'])
@login_required
def email_writer():
    """AI Email Writer."""
    if request.method == 'POST':
        # Check usage limit
        limit_check = check_usage_limit('email_writer')
        if not limit_check['allowed']:
            return jsonify({
                'success': False,
                'error': limit_check['message'],
                'redirect': limit_check.get('redirect')
            })
        
        try:
            purpose = request.form.get('purpose', '').strip()
            details = request.form.get('details', '').strip()
            tone = request.form.get('tone', 'professional')
            
            if not purpose:
                return jsonify({'success': False, 'error': 'Email purpose is required'})
            
            # Generate email
            result = gemini_service.generate_email(purpose, details, tone)
            
            # Record usage
            record_usage('email_writer', f"Purpose: {purpose}", result[:200])
            
            return jsonify({
                'success': True,
                'result': result,
                'message': limit_check['message']
            })
            
        except Exception as e:
            logger.error(f"Email writer error: {e}")
            return jsonify({'success': False, 'error': 'Email generation failed. Please try again.'})
    
    return render_template('ai_tools/email_writer.html')


@ai_tools.route('/social-media', methods=['GET', 'POST'])
@login_required
def social_media():
    """AI Social Media Caption Generator."""
    if request.method == 'POST':
        # Check usage limit
        limit_check = check_usage_limit('social_media_generator')
        if not limit_check['allowed']:
            return jsonify({
                'success': False,
                'error': limit_check['message'],
                'redirect': limit_check.get('redirect')
            })
        
        try:
            platform = request.form.get('platform', 'instagram')
            topic = request.form.get('topic', '').strip()
            hashtags = request.form.get('hashtags') == 'on'
            
            if not topic:
                return jsonify({'success': False, 'error': 'Topic is required'})
            
            # Generate social media captions
            result = gemini_service.generate_social_media_captions(platform, topic, hashtags)
            
            # Record usage
            record_usage('social_media_generator', f"Platform: {platform}, Topic: {topic}", result[:200])
            
            return jsonify({
                'success': True,
                'result': result,
                'message': limit_check['message']
            })
            
        except Exception as e:
            logger.error(f"Social media error: {e}")
            return jsonify({'success': False, 'error': 'Caption generation failed. Please try again.'})
    
    return render_template('ai_tools/social_media.html')


@ai_tools.route('/ad-copy', methods=['GET', 'POST'])
@login_required
def ad_copy():
    """AI Ad Copy Generator."""
    if request.method == 'POST':
        # Check usage limit
        limit_check = check_usage_limit('ad_copy_generator')
        if not limit_check['allowed']:
            return jsonify({
                'success': False,
                'error': limit_check['message'],
                'redirect': limit_check.get('redirect')
            })
        
        try:
            product_service = request.form.get('product_service', '').strip()
            target_audience = request.form.get('target_audience', '').strip()
            platform = request.form.get('platform', 'facebook')
            
            if not product_service:
                return jsonify({'success': False, 'error': 'Product/service description is required'})
            
            # Generate ad copy
            result = gemini_service.generate_ad_copy(product_service, target_audience, platform)
            
            # Record usage
            record_usage('ad_copy_generator', f"Product: {product_service}, Platform: {platform}", result[:200])
            
            return jsonify({
                'success': True,
                'result': result,
                'message': limit_check['message']
            })
            
        except Exception as e:
            logger.error(f"Ad copy error: {e}")
            return jsonify({'success': False, 'error': 'Ad copy generation failed. Please try again.'})
    
    return render_template('ai_tools/ad_copy.html')