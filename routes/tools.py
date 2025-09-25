"""
Tools routes for ToolHub application.
Handles individual tool pages and tool functionality.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import os
import tempfile
import zipfile
from datetime import datetime
from tools.pdf_merge import PDFMerger

tools = Blueprint('tools', __name__, url_prefix='/tools')

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'txt', 'doc', 'docx', 'mp3', 'mp4', 'avi', 'mov', 'wav'}


def allowed_file(filename, tool=None):
    """Check if file extension is allowed for specific tool."""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    # Tool-specific extensions
    tool_extensions = {
        'convert_from_pdf': {'pdf'},
        'convert_to_pdf': {'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'},
        'extract_text': {'pdf'},
        # PDF tools
        'merge': {'pdf'},
        'split': {'pdf'},
        'compress': {'pdf'},
        'rotate': {'pdf'},
        'protect': {'pdf'},
        'watermark': {'pdf'},
        'organize': {'pdf'},
        'unlock': {'pdf'},
        'ocr': {'pdf'},
        'compare': {'pdf'},
        'redact': {'pdf'},
        'edit': {'pdf'},
        'sign': {'pdf'}
    }
    
    if tool and tool in tool_extensions:
        return ext in tool_extensions[tool]
    
    # Default: all allowed extensions
    return ext in ALLOWED_EXTENSIONS


@tools.route('/')
@tools.route('')
def index():
    """Tools listing page."""
    tools_list = [
        # PDF Tools
        {
            'name': 'PDF Merge',
            'description': 'Combine multiple PDF files into a single document',
            'url': '/tools/pdf/merge',
            'icon': '📄',
            'category': 'PDF'
        },
        {
            'name': 'PDF Split',
            'description': 'Split PDF files into separate pages or extract page ranges',
            'url': '/tools/pdf/split',
            'icon': '✂️',
            'category': 'PDF'
        },
        {
            'name': 'PDF Compress',
            'description': 'Reduce PDF file size while maintaining quality',
            'url': '/tools/pdf/compress',
            'icon': '🗜️',
            'category': 'PDF'
        },
        {
            'name': 'Convert from PDF',
            'description': 'Convert PDF to Word, Excel, or text format',
            'url': '/tools/pdf/convert-from-pdf',
            'icon': '🔄',
            'category': 'PDF'
        },
        {
            'name': 'Convert to PDF',
            'description': 'Convert Word, Excel, PowerPoint files to PDF',
            'url': '/tools/pdf/convert-to-pdf',
            'icon': '📄',
            'category': 'PDF'
        },
        {
            'name': 'PDF Protect',
            'description': 'Add password protection to secure your PDF files',
            'url': '/tools/pdf/protect',
            'icon': '🔐',
            'category': 'PDF'
        },
        {
            'name': 'PDF Watermark',
            'description': 'Add text watermarks to your PDF documents',
            'url': '/tools/pdf/watermark',
            'icon': '🏷️',
            'category': 'PDF'
        },
        {
            'name': 'PDF Rotate',
            'description': 'Rotate PDF pages to correct orientation',
            'url': '/tools/pdf/rotate',
            'icon': '🔄',
            'category': 'PDF'
        },
        {
            'name': 'Extract Text',
            'description': 'Extract text content from PDF files',
            'url': '/tools/pdf/extract-text',
            'icon': '📝',
            'category': 'PDF'
        },
        {
            'name': 'PDF Organize',
            'description': 'Reorder, duplicate, or delete PDF pages',
            'url': '/tools/pdf/organize',
            'icon': '📋',
            'category': 'PDF'
        },
        {
            'name': 'PDF Unlock',
            'description': 'Remove password protection from PDF files',
            'url': '/tools/pdf/unlock',
            'icon': '🔓',
            'category': 'PDF'
        },
        {
            'name': 'PDF OCR',
            'description': 'Extract text from scanned PDF documents',
            'url': '/tools/pdf/ocr',
            'icon': '👁️',
            'category': 'PDF'
        },
        {
            'name': 'PDF Compare',
            'description': 'Compare two PDF documents and find differences',
            'url': '/tools/pdf/compare',
            'icon': '🔍',
            'category': 'PDF'
        },
        {
            'name': 'PDF Redact',
            'description': 'Remove sensitive information from PDF files',
            'url': '/tools/pdf/redact',
            'icon': '🖤',
            'category': 'PDF'
        },
        {
            'name': 'PDF Edit',
            'description': 'Edit text and content in PDF documents',
            'url': '/tools/pdf/edit',
            'icon': '✏️',
            'category': 'PDF'
        },
        {
            'name': 'PDF Sign',
            'description': 'Add digital signatures to PDF documents',
            'url': '/tools/pdf/sign',
            'icon': '✍️',
            'category': 'PDF'
        },
        # Other Tools
        {
            'name': 'Image Resizer',
            'description': 'Resize images while maintaining quality',
            'url': '/tools/image-resizer',
            'icon': '🖼️',
            'category': 'Image'
        },
        {
            'name': 'QR Code Generator',
            'description': 'Generate QR codes for text, URLs, and more',
            'url': '/tools/qr-generator',
            'icon': '📱',
            'category': 'Utility'
        },
        {
            'name': 'File Converter',
            'description': 'Convert between different file formats',
            'url': '/tools/file-converter',
            'icon': '🔄',
            'category': 'Utility'
        },
        # SEO Tools
        {
            'name': 'SEO & Marketing Toolkit',
            'description': 'Complete SEO toolkit with audit, keyword research, and analytics',
            'url': '/tools/seo-tools',
            'icon': '🔍',
            'category': 'SEO'
        },
        {
            'name': 'SEO Audit',
            'description': 'Comprehensive analysis of your website\'s SEO health',
            'url': '/tools/seo-audit',
            'icon': '🔍',
            'category': 'SEO'
        },
        {
            'name': 'Keyword Research',
            'description': 'Discover high-value keywords with search volume and difficulty',
            'url': '/tools/keyword-research',
            'icon': '🔑',
            'category': 'SEO'
        },
        {
            'name': 'Backlink Checker',
            'description': 'Analyze backlink profile and link building opportunities',
            'url': '/tools/backlink-checker',
            'icon': '🔗',
            'category': 'SEO'
        },
        {
            'name': 'Domain Overview',
            'description': 'Get comprehensive domain metrics and authority scores',
            'url': '/tools/domain-overview',
            'icon': '🌐',
            'category': 'SEO'
        },
        {
            'name': 'Traffic Analytics',
            'description': 'Monitor website traffic sources and engagement metrics',
            'url': '/tools/traffic-analytics',
            'icon': '📊',
            'category': 'SEO'
        },
        {
            'name': 'On-Page SEO Checker',
            'description': 'Optimize individual pages for better search rankings',
            'url': '/tools/onpage-seo',
            'icon': '📝',
            'category': 'SEO'
        },
        {
            'name': 'Competitor Analysis',
            'description': 'Compare your website performance against competitors',
            'url': '/tools/competitor-analysis',
            'icon': '⚔️',
            'category': 'SEO'
        },
        {
            'name': 'Content Analyzer',
            'description': 'Analyze content readability and SEO optimization',
            'url': '/tools/content-analyzer',
            'icon': '📄',
            'category': 'SEO'
        },
        {
            'name': 'SERP Tracking',
            'description': 'Track keyword rankings across search engines',
            'url': '/tools/serp-tracking',
            'icon': '📈',
            'category': 'SEO'
        },
        {
            'name': 'Site Speed Test',
            'description': 'Test website loading speed and get optimization tips',
            'url': '/tools/site-speed',
            'icon': '⚡',
            'category': 'SEO'
        },
        {
            'name': 'Ad Campaign Research',
            'description': 'Research competitor ad strategies and profitable keywords',
            'url': '/tools/ad-research',
            'icon': '💰',
            'category': 'SEO'
        }
    ]
    return render_template('tools/index.html', tools=tools_list)


# Individual PDF Tool Routes
@tools.route('/pdf/merge')
def pdf_merge():
    """PDF merge tool page."""
    return render_template('tools/pdf_toolkit/merge.html')


@tools.route('/pdf/split')
def pdf_split():
    """PDF split tool page."""
    return render_template('tools/pdf_toolkit/split.html')


@tools.route('/pdf/compress')
def pdf_compress():
    """PDF compress tool page."""
    return render_template('tools/pdf_toolkit/compress.html')


@tools.route('/pdf/convert-from-pdf')
def pdf_convert_from():
    """Convert from PDF tool page."""
    return render_template('tools/pdf_toolkit/convert_from_pdf.html')


@tools.route('/pdf/convert-to-pdf')
def pdf_convert_to():
    """Convert to PDF tool page."""
    return render_template('tools/pdf_toolkit/convert_to_pdf.html')


@tools.route('/pdf/protect')
def pdf_protect():
    """PDF protect tool page."""
    return render_template('tools/pdf_toolkit/protect.html')


@tools.route('/pdf/watermark')
def pdf_watermark():
    """PDF watermark tool page."""
    return render_template('tools/pdf_toolkit/watermark.html')


@tools.route('/pdf/rotate')
def pdf_rotate():
    """PDF rotate tool page."""
    return render_template('tools/pdf_toolkit/rotate.html')


@tools.route('/pdf/extract-text')
def pdf_extract_text():
    """PDF extract text tool page."""
    return render_template('tools/pdf_toolkit/extract_text.html')


@tools.route('/pdf/organize')
def pdf_organize():
    """PDF organize tool page."""
    return render_template('tools/pdf_toolkit/organize.html')


@tools.route('/pdf/unlock')
def pdf_unlock():
    """PDF unlock tool page."""
    return render_template('tools/pdf_toolkit/unlock.html')


@tools.route('/pdf/ocr')
def pdf_ocr():
    """PDF OCR tool page."""
    return render_template('tools/pdf_toolkit/ocr.html')


@tools.route('/pdf/compare')
def pdf_compare():
    """PDF compare tool page."""
    return render_template('tools/pdf_toolkit/compare.html')


@tools.route('/pdf/redact')
def pdf_redact():
    """PDF redact tool page."""
    return render_template('tools/pdf_toolkit/redact.html')


@tools.route('/pdf/edit')
def pdf_edit():
    """PDF edit tool page."""
    return render_template('tools/pdf_toolkit/edit.html')


@tools.route('/pdf/sign')
def pdf_sign():
    """PDF sign tool page."""
    return render_template('tools/pdf_toolkit/sign.html')


# PDF Processing Routes (POST endpoints for form submissions)
@tools.route('/pdf/merge', methods=['POST'])
def pdf_merge_process():
    """Process PDF merge requests."""
    try:
        files = request.files.getlist('pdf_files')
        if not files or len(files) < 2:
            return jsonify({'error': 'At least 2 PDF files are required'}), 400
        
        # Save uploaded files
        input_paths = []
        for file in files:
            if file and file.filename and allowed_file(file.filename, 'merge'):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)
                input_paths.append(filepath)
        
        if len(input_paths) < 2:
            return jsonify({'error': 'At least 2 valid PDF files are required'}), 400
        
        # Process merge
        merger = PDFMerger()
        output_path = merger.merge_pdfs(input_paths)
        
        # Clean up input files
        for path in input_paths:
            if os.path.exists(path):
                os.remove(path)
        
        return send_file(output_path, as_attachment=True, download_name='merged.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Merge failed: {str(e)}'}), 500


@tools.route('/pdf/split', methods=['POST'])
def pdf_split_process():
    """Process PDF split requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'split'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        split_method = request.form.get('split_method', 'all_pages')
        page_range = request.form.get('page_range', '')
        split_interval = int(request.form.get('split_interval', 1))
        
        # Process split
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.split_pdf(filepath, split_method, page_range, split_interval)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        download_name = 'split_pages.zip' if split_method != 'extract_pages' else 'extracted_pages.pdf'
        return send_file(output_path, as_attachment=True, download_name=download_name)
        
    except Exception as e:
        return jsonify({'error': f'Split failed: {str(e)}'}), 500


@tools.route('/pdf/compress', methods=['POST'])
def pdf_compress_process():
    """Process PDF compress requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'compress'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        quality = int(request.form.get('quality', 50))
        
        # Process compression
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.compress_pdf(filepath, quality=quality)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(output_path, as_attachment=True, download_name='compressed.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Compression failed: {str(e)}'}), 500


@tools.route('/pdf/rotate', methods=['POST'])
def pdf_rotate_process():
    """Process PDF rotate requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'rotate'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        rotation = int(request.form.get('rotation', 90))
        pages = request.form.get('pages', 'all')
        
        # Process rotation
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.rotate_pdf(filepath, rotation, pages)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(output_path, as_attachment=True, download_name='rotated.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Rotation failed: {str(e)}'}), 500


@tools.route('/pdf/protect', methods=['POST'])
def pdf_protect_process():
    """Process PDF protect requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'protect'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        password = request.form.get('password')
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Process protection
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.protect_pdf(filepath, password)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(output_path, as_attachment=True, download_name='protected.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Protection failed: {str(e)}'}), 500


@tools.route('/pdf/watermark', methods=['POST'])
def pdf_watermark_process():
    """Process PDF watermark requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'watermark'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        watermark_text = request.form.get('watermark_text', 'WATERMARK')
        opacity = float(request.form.get('opacity', 0.3))
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Process watermarking
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.add_watermark(filepath, watermark_text, opacity=opacity)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(output_path, as_attachment=True, download_name='watermarked.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Watermarking failed: {str(e)}'}), 500


@tools.route('/pdf/extract-text', methods=['POST'])
def pdf_extract_text_process():
    """Process PDF text extraction requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'extract_text'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Process text extraction
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        text_content = toolkit.extract_text(filepath)
        
        # Save text to file
        text_filename = f"extracted_text_{timestamp}.txt"
        text_filepath = os.path.join(UPLOAD_FOLDER, text_filename)
        with open(text_filepath, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(text_filepath, as_attachment=True, download_name='extracted_text.txt', mimetype='text/plain')
        
    except Exception as e:
        return jsonify({'error': f'Text extraction failed: {str(e)}'}), 500


@tools.route('/pdf/organize', methods=['POST'])
def pdf_organize_process():
    """Process PDF organize requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'organize'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Parse operations
        operations = []
        if request.form.get('remove_pages'):
            pages_to_remove = request.form.get('pages_to_remove', '').strip()
            if pages_to_remove:
                operations.append({'action': 'remove', 'pages': pages_to_remove})
        
        if request.form.get('reorder_pages'):
            new_order = request.form.get('new_order', '').strip()
            if new_order:
                order = [int(p.strip()) for p in new_order.split(',') if p.strip().isdigit()]
                if order:
                    operations.append({'action': 'reorder', 'order': order})
        
        if request.form.get('duplicate_pages'):
            pages_to_duplicate = request.form.get('pages_to_duplicate', '').strip()
            if pages_to_duplicate:
                operations.append({'action': 'duplicate', 'pages': pages_to_duplicate})
        
        if not operations:
            return jsonify({'error': 'No organization operations specified'}), 400
        
        # Process organization
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.organize_pdf(filepath, operations)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(output_path, as_attachment=True, download_name='organized.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Organization failed: {str(e)}'}), 500


@tools.route('/pdf/unlock', methods=['POST'])
def pdf_unlock_process():
    """Process PDF unlock requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'unlock'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        password = request.form.get('password')
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Process unlock
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.unlock_pdf(filepath, password)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(output_path, as_attachment=True, download_name='unlocked.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Unlock failed: {str(e)}'}), 500


@tools.route('/pdf/ocr', methods=['POST'])
def pdf_ocr_process():
    """Process PDF OCR requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'ocr'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Get OCR options
        language = request.form.get('language', 'eng')
        output_format = request.form.get('output_format', 'searchable_pdf')
        quality = request.form.get('quality', 'balanced')
        
        ocr_options = {
            'language': language,
            'output_format': output_format,
            'quality': quality
        }
        
        # Process OCR
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.ocr_pdf(filepath, ocr_options)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        if output_format == 'text_file':
            return send_file(output_path, as_attachment=True, download_name='ocr_result.txt', mimetype='text/plain')
        else:
            return send_file(output_path, as_attachment=True, download_name='searchable.pdf')
        
    except Exception as e:
        return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500


@tools.route('/pdf/compare', methods=['POST'])
def pdf_compare_process():
    """Process PDF compare requests."""
    try:
        file1 = request.files.get('pdf_file1')
        file2 = request.files.get('pdf_file2')
        
        if not file1 or not file2 or not allowed_file(file1.filename, 'compare') or not allowed_file(file2.filename, 'compare'):
            return jsonify({'error': 'Two valid PDF files are required'}), 400
        
        # Save uploaded files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename1 = secure_filename(file1.filename)
        filepath1 = os.path.join(UPLOAD_FOLDER, f"{timestamp}_1_{filename1}")
        file1.save(filepath1)
        
        filename2 = secure_filename(file2.filename)
        filepath2 = os.path.join(UPLOAD_FOLDER, f"{timestamp}_2_{filename2}")
        file2.save(filepath2)
        
        # Get comparison options
        options = {
            'comparison_type': request.form.get('comparison_type', 'text'),
            'report_format': request.form.get('report_format', 'pdf'),
            'sensitivity': request.form.get('sensitivity', 'medium'),
            'ignore_formatting': 'ignore_formatting' in request.form,
            'ignore_whitespace': 'ignore_whitespace' in request.form,
            'show_statistics': 'show_statistics' in request.form
        }
        
        # Process comparison
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.compare_pdfs(filepath1, filepath2, options)
        
        # Clean up input files
        for path in [filepath1, filepath2]:
            if os.path.exists(path):
                os.remove(path)
        
        report_format = options['report_format']
        if report_format == 'html':
            return send_file(output_path, as_attachment=True, download_name='comparison_report.html', mimetype='text/html')
        elif report_format == 'text':
            return send_file(output_path, as_attachment=True, download_name='comparison_report.txt', mimetype='text/plain')
        else:
            return send_file(output_path, as_attachment=True, download_name='comparison_report.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Comparison failed: {str(e)}'}), 500


@tools.route('/pdf/redact', methods=['POST'])
def pdf_redact_process():
    """Process PDF redact requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'redact'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Get redaction options
        redaction_method = request.form.get('redaction_method', 'text_search')
        redaction_options = {
            'method': redaction_method,
            'color': request.form.get('redaction_color', 'black'),
            'case_sensitive': 'case_sensitive' in request.form
        }
        
        if redaction_method == 'text_search':
            search_terms = request.form.get('search_terms', '').strip()
            regex_patterns = request.form.get('regex_patterns', '').strip()
            quick_patterns = request.form.getlist('quick_patterns')
            
            redaction_options.update({
                'search_terms': search_terms.split(',') if search_terms else [],
                'regex_patterns': regex_patterns.split(',') if regex_patterns else [],
                'quick_patterns': quick_patterns
            })
        else:
            coordinates = request.form.get('coordinates', '').strip()
            redaction_options['coordinates'] = coordinates
        
        # Process redaction
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.redact_pdf(filepath, redaction_options)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(output_path, as_attachment=True, download_name='redacted.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Redaction failed: {str(e)}'}), 500


@tools.route('/pdf/edit', methods=['POST'])
def pdf_edit_process():
    """Process PDF edit requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'edit'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Get edit options
        operation_type = request.form.get('operation_type', 'find_replace')
        edit_options = {
            'operation_type': operation_type,
            'font_size': int(request.form.get('font_size', 12)),
            'font_color': request.form.get('font_color', 'black'),
            'font_style': request.form.get('font_style', 'normal'),
            'case_sensitive': 'case_sensitive' in request.form,
            'whole_word': 'whole_word' in request.form,
            'regex_search': 'regex_search' in request.form
        }
        
        if operation_type == 'find_replace':
            edit_options.update({
                'find_text': request.form.get('find_text', ''),
                'replace_text': request.form.get('replace_text', '')
            })
        elif operation_type == 'insert_text':
            edit_options.update({
                'insert_text': request.form.get('insert_text', ''),
                'insert_x': int(request.form.get('insert_x', 100)),
                'insert_y': int(request.form.get('insert_y', 700)),
                'insert_page': int(request.form.get('insert_page', 1))
            })
        elif operation_type == 'delete_text':
            edit_options['delete_text'] = request.form.get('delete_text', '')
        
        # Process editing
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.edit_pdf_text(filepath, edit_options)
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(output_path, as_attachment=True, download_name='edited.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Editing failed: {str(e)}'}), 500


@tools.route('/pdf/sign', methods=['POST'])
def pdf_sign_process():
    """Process PDF sign requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'sign'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Get signature options
        signature_type = request.form.get('signature_type', 'text')
        signature_options = {
            'type': signature_type,
            'page': int(request.form.get('position_page', 1)),
            'x': int(request.form.get('position_x', 400)),
            'y': int(request.form.get('position_y', 100)),
            'add_timestamp': 'add_timestamp' in request.form,
            'add_location': 'add_location' in request.form,
            'add_reason': 'add_reason' in request.form
        }
        
        if signature_type == 'text':
            signature_options.update({
                'text': request.form.get('signature_text', 'Digitally Signed'),
                'font': request.form.get('text_font', 'cursive'),
                'size': int(request.form.get('text_size', 16)),
                'color': request.form.get('text_color', 'black')
            })
        elif signature_type == 'image':
            sig_image = request.files.get('signature_image')
            if sig_image:
                sig_filename = secure_filename(sig_image.filename)
                sig_filepath = os.path.join(UPLOAD_FOLDER, f"{timestamp}_sig_{sig_filename}")
                sig_image.save(sig_filepath)
                signature_options['image_path'] = sig_filepath
        elif signature_type == 'certificate':
            cert_file = request.files.get('certificate_file')
            if cert_file:
                cert_filename = secure_filename(cert_file.filename)
                cert_filepath = os.path.join(UPLOAD_FOLDER, f"{timestamp}_cert_{cert_filename}")
                cert_file.save(cert_filepath)
                signature_options.update({
                    'certificate_path': cert_filepath,
                    'certificate_password': request.form.get('certificate_password', '')
                })
        
        if signature_options['add_location']:
            signature_options['location'] = request.form.get('location_text', '')
        
        if signature_options['add_reason']:
            signature_options['reason'] = request.form.get('reason_text', '')
        
        # Process signing
        from tools.pdf_toolkit import PDFToolkit
        toolkit = PDFToolkit()
        output_path = toolkit.sign_pdf(filepath, signature_options)
        
        # Clean up input files
        if os.path.exists(filepath):
            os.remove(filepath)
        if signature_type == 'image' and 'image_path' in signature_options:
            if os.path.exists(signature_options['image_path']):
                os.remove(signature_options['image_path'])
        if signature_type == 'certificate' and 'certificate_path' in signature_options:
            if os.path.exists(signature_options['certificate_path']):
                os.remove(signature_options['certificate_path'])
        
        return send_file(output_path, as_attachment=True, download_name='signed.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Signing failed: {str(e)}'}), 500


# Conversion Processing Routes
@tools.route('/pdf/convert-from-pdf', methods=['POST'])
def pdf_convert_from_process():
    """Process convert from PDF requests."""
    try:
        file = request.files.get('pdf_file')
        if not file or not allowed_file(file.filename, 'convert_from_pdf'):
            return jsonify({'error': 'Valid PDF file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        output_format = request.form.get('output_format', 'docx')
        
        # Process conversion
        from tools.pdf_converter import PDFConverter
        converter = PDFConverter()
        
        if output_format == 'docx':
            output_path = converter.pdf_to_word(filepath)
            download_name = 'converted.docx'
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif output_format == 'xlsx':
            output_path = converter.pdf_to_excel(filepath)
            download_name = 'converted.xlsx'
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            return jsonify({'error': f'Unsupported format: {output_format}'}), 400
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(output_path, as_attachment=True, download_name=download_name, mimetype=mimetype)
        
    except Exception as e:
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@tools.route('/pdf/convert-to-pdf', methods=['POST'])
def pdf_convert_to_process():
    """Process convert to PDF requests."""
    try:
        file = request.files.get('file')
        if not file or not allowed_file(file.filename, 'convert_to_pdf'):
            return jsonify({'error': 'Valid document file is required'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Process conversion
        from tools.pdf_converter import PDFConverter
        converter = PDFConverter()
        
        if file_ext in ['.doc', '.docx']:
            output_path = converter.word_to_pdf(filepath)
        elif file_ext in ['.xls', '.xlsx']:
            output_path = converter.excel_to_pdf(filepath)
        elif file_ext in ['.ppt', '.pptx']:
            output_path = converter.powerpoint_to_pdf(filepath)
        else:
            return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400
        
        # Clean up input file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return send_file(output_path, as_attachment=True, download_name='converted.pdf')
        
    except Exception as e:
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


# Other tool routes (placeholder)
@tools.route('/image-resizer')
def image_resizer():
    """Image resizer tool page."""
    return render_template('tools/coming_soon.html', tool_name="Image Resizer")


@tools.route('/qr-generator')
def qr_generator():
    """QR code generator tool page."""
    return render_template('tools/qr_generator.html')


@tools.route('/qr-generator', methods=['POST'])
def qr_generator_process():
    """Process QR code generation requests."""
    try:
        import qrcode
        import base64
        from io import BytesIO
        
        qr_type = request.form.get('qr_type', 'url')
        
        # Generate QR data based on type
        qr_data = None
        
        if qr_type == 'url':
            qr_data = request.form.get('url', '')
        elif qr_type == 'text':
            qr_data = request.form.get('text', '')
        elif qr_type == 'wifi':
            ssid = request.form.get('wifi_ssid', '')
            password = request.form.get('wifi_password', '')
            security = request.form.get('wifi_security', 'WPA')
            qr_data = f"WIFI:T:{security};S:{ssid};P:{password};;"
        elif qr_type == 'email':
            email = request.form.get('email_address', '')
            subject = request.form.get('email_subject', '')
            body = request.form.get('email_body', '')
            qr_data = f"mailto:{email}?subject={subject}&body={body}"
        elif qr_type == 'phone':
            phone = request.form.get('phone_number', '')
            qr_data = f"tel:{phone}"
        elif qr_type == 'sms':
            phone = request.form.get('sms_phone', '')
            message = request.form.get('sms_message', '')
            qr_data = f"SMSTO:{phone}:{message}"
        elif qr_type == 'vcard':
            name = request.form.get('vcard_name', '')
            phone = request.form.get('vcard_phone', '')
            email = request.form.get('vcard_email', '')
            org = request.form.get('vcard_organization', '')
            qr_data = f"BEGIN:VCARD\nVERSION:3.0\nFN:{name}\nTEL:{phone}\nEMAIL:{email}\nORG:{org}\nEND:VCARD"
        elif qr_type == 'whatsapp':
            phone = request.form.get('whatsapp_phone', '')
            message = request.form.get('whatsapp_message', '')
            qr_data = f"https://wa.me/{phone}?text={message}"
        elif qr_type == 'social':
            platform = request.form.get('social_platform', '')
            username = request.form.get('social_username', '')
            if username.startswith('http'):
                qr_data = username
            else:
                social_urls = {
                    'instagram': f'https://instagram.com/{username}',
                    'facebook': f'https://facebook.com/{username}',
                    'twitter': f'https://twitter.com/{username}',
                    'tiktok': f'https://tiktok.com/@{username}',
                    'linkedin': f'https://linkedin.com/in/{username}',
                    'snapchat': f'https://snapchat.com/add/{username}'
                }
                qr_data = social_urls.get(platform, username)
        elif qr_type == 'youtube':
            qr_data = request.form.get('youtube_url', '')
        elif qr_type == 'location':
            location_type = request.form.get('location_type', 'coordinates')
            if location_type == 'coordinates':
                lat = request.form.get('latitude', '')
                lng = request.form.get('longitude', '')
                qr_data = f"geo:{lat},{lng}"
            elif location_type == 'address':
                address = request.form.get('address', '')
                qr_data = f"geo:0,0?q={address}"
            elif location_type == 'google_maps':
                qr_data = request.form.get('maps_url', '')
        elif qr_type == 'file':
            # Handle file uploads
            file_upload = request.files.get('file_upload')
            if file_upload and file_upload.filename:
                # Save file temporarily
                filename = secure_filename(file_upload.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file_upload.save(filepath)
                
                # Create a download URL
                # Note: In production, you'd use a proper file hosting service
                file_title = request.form.get('file_title', filename)
                download_url = f"{request.host_url}downloads/{unique_filename}"
                qr_data = download_url
                
                # Store file info for potential download (you'd use a database in production)
                # For now, we'll just create a QR with the filename info
            else:
                return jsonify({'success': False, 'error': 'Please select a file to generate QR code'}), 400
        elif qr_type == 'upi':
            upi_id = request.form.get('upi_id', '')
            amount = request.form.get('upi_amount', '')
            note = request.form.get('upi_note', '')
            if amount:
                qr_data = f"upi://pay?pa={upi_id}&am={amount}&tn={note}"
            else:
                qr_data = f"upi://pay?pa={upi_id}&tn={note}"
        elif qr_type == 'paypal':
            paypal_email = request.form.get('paypal_email', '')
            amount = request.form.get('paypal_amount', '')
            currency = request.form.get('paypal_currency', 'USD')
            note = request.form.get('paypal_note', '')
            if amount:
                qr_data = f"https://www.paypal.me/{paypal_email}/{amount}{currency}?note={note}"
            else:
                qr_data = f"https://www.paypal.me/{paypal_email}"
        elif qr_type == 'crypto':
            crypto_type = request.form.get('crypto_type', 'bitcoin')
            address = request.form.get('crypto_address', '')
            amount = request.form.get('crypto_amount', '')
            if crypto_type == 'bitcoin':
                if amount:
                    qr_data = f"bitcoin:{address}?amount={amount}"
                else:
                    qr_data = f"bitcoin:{address}"
            elif crypto_type == 'ethereum':
                if amount:
                    qr_data = f"ethereum:{address}?amount={amount}"
                else:
                    qr_data = f"ethereum:{address}"
            else:
                qr_data = address
        else:
            qr_data = request.form.get('data', '')
        
        if not qr_data:
            return jsonify({'success': False, 'error': 'No data provided for QR generation'}), 400
        
        # Get QR customization options
        size = request.form.get('size', '300')
        error_correction = request.form.get('error_correction', 'M')
        fg_color = request.form.get('fg_color', '#000000')
        bg_color = request.form.get('bg_color', '#ffffff')
        
        # Map size to actual dimensions
        try:
            qr_size = int(size)
        except (ValueError, TypeError):
            qr_size = 300
        
        # Map error correction levels
        error_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        error_level = error_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_level,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR image
        qr_img = qr.make_image(fill_color=fg_color, back_color=bg_color)
        
        # Resize to requested size
        qr_img = qr_img.resize((qr_size, qr_size))
        
        # Convert to base64
        img_buffer = BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qr_code': img_base64,
            'data': qr_data,
            'type': qr_type,
            'size': size,
            'error_correction': error_correction
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'QR generation failed: {str(e)}'}), 500


@tools.route('/qr-generator-pro')
def qr_generator_pro():
    """Pro QR code generator tool page."""
    return render_template('tools/qr_generator_pro.html')


@tools.route('/qr-generator-pro', methods=['POST'])
def qr_generator_pro_process():
    """Process Pro QR code generation requests with advanced features."""
    try:
        from tools.qr_generator_pro import generate_qr_code, validate_qr_data, format_data_by_type
        
        # Get form data
        qr_type = request.form.get('qr_type', 'url')
        
        # Validate and format data based on type
        qr_data = format_data_by_type(qr_type, request.form)
        
        if not qr_data:
            return jsonify({'success': False, 'error': 'No data provided for QR generation'}), 400
        
        # Validate QR data
        is_valid, error_message = validate_qr_data(qr_data, qr_type)
        if not is_valid:
            return jsonify({'success': False, 'error': error_message}), 400
        
        # Get advanced customization options
        design_options = {
            'size': request.form.get('size', '300'),
            'error_correction': request.form.get('error_correction', 'M'),
            'fg_color': request.form.get('fg_color', '#000000'),
            'bg_color': request.form.get('bg_color', '#ffffff'),
            'style': request.form.get('style', 'square'),
            'logo_upload': request.files.get('logo_upload'),
            'frame_style': request.form.get('frame_style', 'none'),
            'frame_color': request.form.get('frame_color', '#000000'),
            'frame_text': request.form.get('frame_text', ''),
            'gradient': request.form.get('gradient') == 'on',
            'gradient_start': request.form.get('gradient_start', '#000000'),
            'gradient_end': request.form.get('gradient_end', '#333333'),
            'eye_style': request.form.get('eye_style', 'square'),
            'data_style': request.form.get('data_style', 'square')
        }
        
        # Generate Pro QR code
        result = generate_qr_code(qr_data, design_options)
        
        if result['success']:
            return jsonify({
                'success': True,
                'qr_code': result['qr_code'],
                'data': qr_data,
                'type': qr_type,
                'filename': result.get('filename'),
                'download_url': result.get('download_url')
            })
        else:
            return jsonify({'success': False, 'error': result['error']}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Pro QR generation failed: {str(e)}'}), 500


@tools.route('/file-converter')
def file_converter():
    """File converter tool page."""
    return render_template('tools/coming_soon.html', tool_name="File Converter")


@tools.route('/downloads/<filename>')
def download_file(filename):
    """Serve uploaded files for download."""
    try:
        # Validate filename for security
        safe_filename = secure_filename(filename)
        if safe_filename != filename:
            return "Invalid filename", 400
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return "File not found", 404
        
        return send_file(filepath, as_attachment=True, download_name=filename.split('_', 1)[-1])
    except Exception as e:
        return f"Error serving file: {str(e)}", 500


# ===== SEO TOOLS ROUTES =====

@tools.route('/seo-tools')
@tools.route('/seo')
def seo_tools_dashboard():
    """SEO Tools dashboard page."""
    return render_template('tools/seo_tools/index.html')


@tools.route('/seo-audit', methods=['GET', 'POST'])
@tools.route('/seo/seo-audit', methods=['GET', 'POST'])
def seo_audit():
    """SEO Audit tool with real analysis."""
    if request.method == 'POST':
        try:
            website_url = request.form.get('website_url')
            audit_depth = request.form.get('audit_depth', 'standard')
            include_mobile = request.form.get('include_mobile') == 'on'
            
            if not website_url:
                return jsonify({'success': False, 'error': 'Website URL is required'}), 400
            
            # Real SEO analysis using our analyzer
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.audit_website(website_url, audit_depth)
            
            return jsonify({'success': True, 'results': results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/seo_audit.html')


@tools.route('/keyword-research', methods=['GET', 'POST'])
@tools.route('/seo/keyword-research', methods=['GET', 'POST'])
def keyword_research():
    """Keyword Research tool with real Google Trends data."""
    if request.method == 'POST':
        try:
            keyword = request.form.get('keyword')
            region = request.form.get('region', 'US')
            language = request.form.get('language', 'en')
            
            if not keyword:
                return jsonify({'success': False, 'error': 'Keyword is required'}), 400
            
            # Real keyword research using Google Trends
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.research_keywords(keyword, region, language)
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/keyword_research.html')


@tools.route('/backlink-checker', methods=['GET', 'POST'])
@tools.route('/seo/backlink-checker', methods=['GET', 'POST'])
def backlink_checker():
    """Backlink Checker tool."""
    if request.method == 'POST':
        try:
            domain = request.form.get('domain')
            
            if not domain:
                return jsonify({'success': False, 'error': 'Domain is required'}), 400
            
            # Real backlink analysis
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.check_backlinks_basic(domain)
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/backlink_checker.html')


@tools.route('/domain-overview', methods=['GET', 'POST'])
@tools.route('/seo/domain-overview', methods=['GET', 'POST'])
def domain_overview():
    """Domain Overview tool."""
    if request.method == 'POST':
        try:
            domain = request.form.get('domain')
            
            if not domain:
                return jsonify({'success': False, 'error': 'Domain is required'}), 400
            
            # Real domain analysis
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.analyze_domain_overview(domain)
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/domain_overview.html')


@tools.route('/traffic-analytics', methods=['GET', 'POST'])
@tools.route('/seo/traffic-analytics', methods=['GET', 'POST'])
def traffic_analytics():
    """Traffic Analytics tool with Google Analytics integration."""
    if request.method == 'POST':
        try:
            domain = request.form.get('domain')
            view_id = request.form.get('view_id')  # Optional GA View ID
            
            if not domain:
                return jsonify({'success': False, 'error': 'Domain is required'}), 400
            
            # Try to get real Google Analytics data first
            from services.google_analytics_enhanced import get_analytics_service
            ga_service = get_analytics_service()
            
            if view_id and ga_service.is_connected():
                # Use real Google Analytics data
                ga_data = ga_service.get_traffic_data(view_id)
                if ga_data:
                    results = {
                        'monthly_visits': ga_data.get('total_sessions', 0),
                        'page_views': ga_data.get('total_pageviews', 0),
                        'users': ga_data.get('total_users', 0),
                        'avg_duration': ga_data.get('avg_session_duration', 0),
                        'bounce_rate': ga_data.get('avg_bounce_rate', 0),
                        'data_source': 'google_analytics',
                        'properties': ga_service.get_property_list()
                    }
                else:
                    raise Exception("Could not fetch Google Analytics data")
            else:
                # Fallback to domain overview analysis
                from services.seo_analyzer import SEOAnalyzer
                analyzer = SEOAnalyzer()
                domain_data = analyzer.analyze_domain_overview(domain)
                
                # Extract traffic-related metrics
                results = {
                    'monthly_visits': domain_data.get('monthly_traffic', 0),
                    'page_views': int(domain_data.get('monthly_traffic', 0) * 2.5),  # Estimated
                    'avg_duration': 180 + (domain_data.get('domain_authority', 30) * 2),  # Authority impacts engagement
                    'bounce_rate': max(20, 70 - domain_data.get('domain_authority', 30)),  # Higher authority = lower bounce
                    'organic_keywords': domain_data.get('organic_keywords', 0),
                    'traffic_value': domain_data.get('traffic_value', 0),
                    'domain_authority': domain_data.get('domain_authority', 0),
                    'data_source': 'estimated'
                }
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/traffic_analytics.html')


@tools.route('/competitor-analysis', methods=['GET', 'POST'])
@tools.route('/seo/competitor-analysis', methods=['GET', 'POST'])
def competitor_analysis():
    """Competitor Analysis tool."""
    if request.method == 'POST':
        try:
            your_domain = request.form.get('your_domain')
            competitor_domain = request.form.get('competitor_domain')
            
            if not your_domain or not competitor_domain:
                return jsonify({'success': False, 'error': 'Both domains are required'}), 400
            
            # Real competitor analysis using domain data
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            
            # Analyze both domains
            your_data = analyzer.analyze_domain_overview(your_domain)
            competitor_data = analyzer.analyze_domain_overview(competitor_domain)
            
            results = {
                'your_site': {
                    'domain': your_domain,
                    'authority': your_data.get('domain_authority', 0),
                    'traffic': your_data.get('monthly_traffic', 0),
                    'keywords': your_data.get('organic_keywords', 0),
                    'backlinks': your_data.get('total_backlinks', 0),
                    'traffic_value': your_data.get('traffic_value', 0)
                },
                'competitor': {
                    'domain': competitor_domain,
                    'authority': competitor_data.get('domain_authority', 0),
                    'traffic': competitor_data.get('monthly_traffic', 0),
                    'keywords': competitor_data.get('organic_keywords', 0),
                    'backlinks': competitor_data.get('total_backlinks', 0),
                    'traffic_value': competitor_data.get('traffic_value', 0)
                },
                'comparison': {
                    'authority_advantage': competitor_data.get('domain_authority', 0) - your_data.get('domain_authority', 0),
                    'traffic_advantage': competitor_data.get('monthly_traffic', 0) - your_data.get('monthly_traffic', 0),
                    'keyword_advantage': competitor_data.get('organic_keywords', 0) - your_data.get('organic_keywords', 0)
                }
            }
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/competitor_analysis.html')


@tools.route('/content-analyzer', methods=['GET', 'POST'])
def content_analyzer():
    """Content Analyzer tool with real analysis."""
    if request.method == 'POST':
        try:
            content = request.form.get('content')
            
            if not content:
                return jsonify({'success': False, 'error': 'Content is required'}), 400
            
            # Real content analysis using our analyzer
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.analyze_content_readability(content)
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/content_analyzer.html')


@tools.route('/serp-tracking', methods=['GET', 'POST'])
def serp_tracking():
    """SERP Tracking tool with real Google search results."""
    if request.method == 'POST':
        try:
            keyword = request.form.get('keyword')
            domain = request.form.get('domain')
            
            if not keyword or not domain:
                return jsonify({'success': False, 'error': 'Keyword and domain are required'}), 400
            
            # Real SERP position checking
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.check_serp_position(keyword, domain)
            
            # Add change simulation (in real app, store previous positions)
            previous_position = results.get('position', 10) + 2
            current_position = results.get('position', 10)
            change = previous_position - current_position if current_position else 0
            
            results.update({
                'current_position': current_position,
                'previous_position': previous_position,
                'change': change,
                'top_competitors': results.get('competitors', [])
            })
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/serp_tracking.html')


@tools.route('/site-speed', methods=['GET', 'POST'])
def site_speed():
    """Site Speed Test tool with real performance analysis."""
    if request.method == 'POST':
        try:
            url = request.form.get('url')
            api_key = request.form.get('api_key', '')  # Optional Google API key
            
            if not url:
                return jsonify({'success': False, 'error': 'URL is required'}), 400
            
            # Real speed analysis
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.analyze_page_speed(url, api_key or None)
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/site_speed.html')


@tools.route('/onpage-seo', methods=['GET', 'POST'])
def onpage_seo():
    """On-Page SEO Checker tool."""
    if request.method == 'POST':
        try:
            url = request.form.get('url')
            keyword = request.form.get('keyword', '')
            
            if not url:
                return jsonify({'success': False, 'error': 'URL is required'}), 400
            
            # Mock on-page SEO analysis
            results = {
                'url': url,
                'keyword': keyword,
                'seo_score': 72,
                'title_tag': {'status': 'good', 'length': 58},
                'meta_description': {'status': 'warning', 'length': 145},
                'h1_tag': {'status': 'good', 'count': 1},
                'keyword_density': 2.1,
                'internal_links': 15,
                'external_links': 8,
                'image_alt_texts': {'total': 12, 'missing': 3}
            }
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/onpage_seo.html')


@tools.route('/ad-research', methods=['GET', 'POST'])
def ad_research():
    """Ad Campaign Research tool."""
    if request.method == 'POST':
        try:
            query = request.form.get('query')
            research_type = request.form.get('type', 'ads')
            
            if not query:
                return jsonify({'success': False, 'error': 'Query is required'}), 400
            
            # Mock ad research data
            if research_type == 'ads':
                results = {
                    'query': query,
                    'type': 'ads',
                    'ads': [
                        {
                            'headline': 'Best Digital Marketing Services',
                            'description': 'Grow your business with our proven strategies',
                            'display_url': 'example-agency.com',
                            'position': 1
                        },
                        {
                            'headline': 'Professional SEO Services',
                            'description': 'Increase your organic traffic today',
                            'display_url': 'seo-company.net',
                            'position': 2
                        }
                    ]
                }
            else:
                results = {
                    'query': query,
                    'type': 'keywords',
                    'keywords': [
                        {'keyword': f'{query} services', 'cpc': 4.50, 'competition': 'High'},
                        {'keyword': f'best {query}', 'cpc': 3.80, 'competition': 'Medium'},
                        {'keyword': f'{query} agency', 'cpc': 5.20, 'competition': 'High'}
                    ]
                }
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/ad_research.html')


@tools.route('/keyword-density', methods=['GET', 'POST'])
@tools.route('/seo/keyword-density', methods=['GET', 'POST'])
def keyword_density():
    """Keyword Density Checker - API-free analysis."""
    if request.method == 'POST':
        try:
            content = request.form.get('content', '')
            url = request.form.get('url', '')
            
            if not content and not url:
                return jsonify({'success': False, 'error': 'Please provide either content or URL'}), 400
            
            # Get content from URL if provided
            if url and not content:
                from services.seo_analyzer import SEOAnalyzer
                analyzer = SEOAnalyzer()
                
                # Ensure URL has protocol
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                response = analyzer.session.get(url, timeout=30)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract text content
                for script in soup(["script", "style"]):
                    script.decompose()
                content = soup.get_text()
            
            # Analyze keyword density
            results = analyzer.analyze_keyword_density(content)
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/keyword_density.html')


@tools.route('/broken-links', methods=['GET', 'POST'])  
@tools.route('/seo/broken-links', methods=['GET', 'POST'])
def broken_links():
    """Broken Link Checker - API-free analysis."""
    if request.method == 'POST':
        try:
            url = request.form.get('url')
            check_external = request.form.get('check_external') == 'on'
            
            if not url:
                return jsonify({'success': False, 'error': 'URL is required'}), 400
            
            # Real broken link analysis
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.check_broken_links(url, check_external)
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/broken_links.html')


@tools.route('/readability-score', methods=['GET', 'POST'])
@tools.route('/seo/readability-score', methods=['GET', 'POST'])
def readability_score():
    """Readability Score Analyzer - API-free analysis."""
    if request.method == 'POST':
        try:
            content = request.form.get('content')
            
            if not content:
                return jsonify({'success': False, 'error': 'Content is required'}), 400
            
            # Real readability analysis
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.analyze_readability_detailed(content)
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/readability_score.html')


@tools.route('/text-analyzer', methods=['GET', 'POST'])
@tools.route('/seo/text-analyzer', methods=['GET', 'POST'])
def text_analyzer():
    """Text Analyzer Tool - API-free analysis."""
    if request.method == 'POST':
        try:
            content = request.form.get('content')
            
            if not content:
                return jsonify({'success': False, 'error': 'Content is required'}), 400
            
            # Real text analysis
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.analyze_text_statistics(content)
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/text_analyzer.html')


@tools.route('/heading-analyzer', methods=['GET', 'POST'])
@tools.route('/seo/heading-analyzer', methods=['GET', 'POST'])  
def heading_analyzer():
    """Heading Structure Analyzer - API-free analysis."""
    if request.method == 'POST':
        try:
            url = request.form.get('url')
            
            if not url:
                return jsonify({'success': False, 'error': 'URL is required'}), 400
            
            # Real heading analysis
            from services.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            results = analyzer.analyze_heading_structure(url)
            
            return jsonify({'success': True, **results})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('tools/seo_tools/heading_analyzer.html')