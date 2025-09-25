"""
Gemini AI Service for ToolHub
Handles all AI-powered content generation using Google's Gemini API.
Updated to use the official Google GenAI SDK.
"""

import google.genai as genai
import logging
import os
from typing import Dict, Any, Optional
import time
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)


class GeminiService:
    """Service class for Gemini AI operations using official Google GenAI SDK."""
    
    def __init__(self):
        self.client = None
        self.model_name = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client with API key."""
        try:
            # Load environment variables
            load_dotenv()
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.warning("Gemini API key not found in environment")
                return
            
            # Create client with explicit API key
            self.client = genai.Client(api_key=api_key)
            self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            logger.info(f"Gemini client initialized successfully with model {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None
    
    def _generate_content(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Generate content using Gemini with retry logic."""
        if not self.client:
            # Try to reinitialize
            self._initialize_client()
            if not self.client:
                return "AI service is currently unavailable. Please check configuration."
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                if response.text:
                    return response.text.strip()
                else:
                    logger.warning(f"Empty response from Gemini (attempt {attempt + 1})")
                    
            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry
                else:
                    return f"AI generation failed: {str(e)}"
        
        return "Failed to generate content after multiple attempts."
    
    def generate_content(self, prompt: str) -> str:
        """Generic content generation method."""
        return self._generate_content(prompt)
    
    def generate_blog_post(self, topic: str, keywords: str, tone: str, word_count: int = 800) -> str:
        """Generate SEO-optimized blog post."""
        prompt = f"""
        Write a comprehensive, SEO-optimized blog post about "{topic}".
        
        Requirements:
        - Target keywords: {keywords}
        - Tone: {tone}
        - Word count: approximately {word_count} words
        - Include an engaging introduction and conclusion
        - Use proper headings (H2, H3) for structure
        - Make it informative and valuable for readers
        - Naturally incorporate the keywords without keyword stuffing
        
        Structure the content with:
        1. Compelling headline
        2. Introduction hook
        3. Main content with subheadings
        4. Actionable insights
        5. Strong conclusion with call-to-action
        
        Write in a {tone} tone that engages the target audience.
        """
        
        return self._generate_content(prompt)
    
    def summarize_article(self, content: str, summary_type: str = "paragraph") -> str:
        """Summarize long-form content."""
        summary_format = {
            "paragraph": "Write a concise paragraph summary (3-5 sentences)",
            "bullet": "Create 5-7 bullet points highlighting key information",
            "executive": "Write an executive summary with main points and conclusions"
        }
        
        format_instruction = summary_format.get(summary_type, summary_format["paragraph"])
        
        prompt = f"""
        {format_instruction} of the following content:
        
        {content[:4000]}  # Limit content length
        
        Focus on:
        - Main arguments and key points
        - Important facts and statistics
        - Conclusions and recommendations
        - Actionable insights
        
        Keep the summary clear, concise, and well-organized.
        """
        
        return self._generate_content(prompt)
    
    def paraphrase_text(self, text: str, style: str = "formal") -> str:
        """Paraphrase text in different styles."""
        style_instructions = {
            "formal": "Rewrite in formal, professional language suitable for business communication",
            "casual": "Rewrite in casual, conversational tone for everyday communication", 
            "academic": "Rewrite in academic style with precise, scholarly language",
            "simple": "Rewrite using simple, easy-to-understand language"
        }
        
        instruction = style_instructions.get(style, style_instructions["formal"])
        
        prompt = f"""
        {instruction}:
        
        "{text}"
        
        Requirements:
        - Maintain the original meaning and key information
        - Use different sentence structures and vocabulary
        - Ensure the rewrite is clear and well-written
        - Keep the same approximate length as the original
        """
        
        return self._generate_content(prompt)
    
    def check_grammar_and_style(self, text: str) -> str:
        """Check and correct grammar, spelling, and style."""
        prompt = f"""
        Analyze and improve the following text for grammar, spelling, style, and clarity:
        
        "{text}"
        
        Provide:
        1. Corrected version of the text
        2. Brief explanation of major changes made
        3. Style recommendations for improvement
        
        Focus on:
        - Grammar and spelling errors
        - Sentence structure and flow
        - Word choice and clarity
        - Punctuation and formatting
        
        Format your response as:
        **CORRECTED TEXT:**
        [Your corrected version]
        
        **CHANGES MADE:**
        [Brief explanation of corrections]
        
        **STYLE SUGGESTIONS:**
        [Recommendations for improvement]
        """
        
        return self._generate_content(prompt)
    
    def generate_headlines(self, topic: str, count: int = 10) -> str:
        """Generate catchy headlines for articles or blog posts."""
        prompt = f"""
        Generate {count} compelling, SEO-friendly headlines for content about "{topic}".
        
        Create headlines that are:
        - Attention-grabbing and clickable
        - SEO-optimized (50-60 characters)
        - Clear and benefit-focused
        - Include power words when appropriate
        - Varied in style (how-to, listicle, question, etc.)
        
        Provide different headline types:
        - How-to guides
        - Listicles
        - Questions
        - Problem/solution
        - Benefit-focused
        
        Format each headline with a number (1., 2., etc.)
        """
        
        return self._generate_content(prompt)
    
    def generate_meta_description(self, title: str, keywords: str) -> str:
        """Generate SEO meta descriptions."""
        prompt = f"""
        Create a compelling meta description for a page with:
        - Title: "{title}"
        - Target keywords: {keywords}
        
        Requirements:
        - 150-160 characters maximum
        - Include primary keyword naturally
        - Create urgency or curiosity
        - Include a call-to-action
        - Make it click-worthy for search results
        
        Provide 3 different variations to choose from.
        """
        
        return self._generate_content(prompt)
    
    def generate_product_description(self, product_name: str, features: str, tone: str) -> str:
        """Generate e-commerce product descriptions."""
        prompt = f"""
        Write a compelling product description for "{product_name}".
        
        Product features/details:
        {features}
        
        Tone: {tone}
        
        Create a description that:
        - Highlights key benefits and features
        - Addresses customer pain points
        - Uses persuasive language
        - Includes emotional triggers
        - Has a clear call-to-action
        - Is optimized for conversions
        
        Structure:
        1. Attention-grabbing headline
        2. Key benefits (bullet points)
        3. Detailed features
        4. Social proof elements
        5. Strong call-to-action
        """
        
        return self._generate_content(prompt)
    
    def generate_email(self, purpose: str, details: str, tone: str) -> str:
        """Generate professional emails for various purposes."""
        prompt = f"""
        Write a professional email for: {purpose}
        
        Details/Context:
        {details}
        
        Tone: {tone}
        
        Include:
        - Compelling subject line
        - Proper greeting
        - Clear and concise message
        - Appropriate call-to-action
        - Professional closing
        
        Make the email:
        - Personalized and engaging
        - Goal-oriented
        - Professional yet {tone}
        - Action-focused
        
        Format:
        Subject: [Subject line]
        
        [Email body]
        """
        
        return self._generate_content(prompt)
    
    def generate_social_media_captions(self, platform: str, topic: str, hashtags: bool = True) -> str:
        """Generate social media captions for different platforms."""
        platform_specs = {
            "instagram": "engaging, visual-focused, 1-2 sentences + emojis",
            "linkedin": "professional, thought-provoking, business-focused",
            "twitter": "concise, witty, under 280 characters",
            "facebook": "conversational, community-building, engaging"
        }
        
        spec = platform_specs.get(platform.lower(), "engaging and platform-appropriate")
        
        prompt = f"""
        Create 5 different {platform} captions about "{topic}".
        
        Make them {spec}.
        
        Requirements for {platform}:
        - Platform-optimized length and style  
        - Engaging and shareable
        - Include call-to-action
        - Use appropriate emojis
        {"- Include relevant hashtags (5-10)" if hashtags else "- No hashtags needed"}
        
        Provide 5 variations with different angles:
        1. Educational/informative
        2. Entertaining/humorous  
        3. Inspirational/motivational
        4. Question/engagement-focused
        5. Behind-the-scenes/personal
        """
        
        return self._generate_content(prompt)
    
    def generate_ad_copy(self, product_service: str, target_audience: str, platform: str) -> str:
        """Generate ad copy for Facebook/Google Ads."""
        prompt = f"""
        Create high-converting ad copy for "{product_service}".
        
        Target Audience: {target_audience}
        Platform: {platform}
        
        Generate:
        1. 3 compelling headlines (30 chars each for Google, 40 for Facebook)
        2. 3 primary text variations (90 chars for Google, 125 for Facebook)
        3. 3 call-to-action options
        4. 2 description lines (90 chars each)
        
        Focus on:
        - Pain points of target audience
        - Unique value proposition
        - Urgency and scarcity
        - Clear benefits
        - Strong call-to-action
        
        Make the copy persuasive, benefit-focused, and conversion-optimized.
        """
        
        return self._generate_content(prompt)


# Global instance
gemini_service = GeminiService()