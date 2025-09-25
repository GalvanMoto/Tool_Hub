#!/usr/bin/env python3

from services.seo_analyzer import SEOAnalyzer

def test_seo_analyzer():
    """Test the SEO analyzer functionality."""
    try:
        analyzer = SEOAnalyzer()
        result = analyzer.audit_website('https://example.com')
        
        print("SEO Analysis Results:")
        print(f"Overall Score: {result.get('overall_score', 'N/A')}")
        print(f"Technical Score: {result.get('technical_score', 'N/A')}")
        print(f"Content Score: {result.get('content_score', 'N/A')}")
        print(f"Performance Score: {result.get('performance_score', 'N/A')}")
        print(f"Critical Issues: {len(result.get('critical_issues', []))}")
        print(f"Warnings: {len(result.get('warnings', []))}")
        
        # Show first critical issue if any
        if result.get('critical_issues'):
            print(f"First issue: {result['critical_issues'][0]['title']}")
        
        return True
        
    except Exception as e:
        print(f"Error testing SEO analyzer: {e}")
        return False

if __name__ == "__main__":
    success = test_seo_analyzer()
    print(f"Test {'PASSED' if success else 'FAILED'}")