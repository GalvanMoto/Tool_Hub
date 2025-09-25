"""
Tools routes for ToolHub application.
Handles individual tool pages and tool functionality.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
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
        # Default PDF tools
        'merge': {'pdf'},
        'split': {'pdf'},
        'compress': {'pdf'},
        'rotate': {'pdf'},
        'protect': {'pdf'},
        'watermark': {'pdf'}
    }
    
    if tool and tool in tool_extensions:
        return ext in tool_extensions[tool]
    
    # Default: all allowed extensions
    return ext in ALLOWED_EXTENSIONS


@tools.route('/')
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
            'icon': '�',
            'category': 'Utility'
        },
        {
            'name': 'File Converter',
            'description': 'Convert between different file formats',
            'url': '/tools/file-converter',
            'icon': '🔄',
            'category': 'Utility'
        }
            'description': 'Combine multiple PDF files into one document',
            'url': '/tools/pdf-merge',
            'icon': '�'
        },
        {
            'name': 'Image Resizer',
            'description': 'Resize images while maintaining quality',
            'url': '/tools/image-resizer',
            'icon': '🖼️'
        },
        {
            'name': 'QR Code Generator',
            'description': 'Universal QR generator for all types - URLs, WiFi, vCard, Social Media & more',
            'url': '/tools/qr-generator',
            'icon': '📱'
        }
    ]
    return render_template('tools/index.html', tools=tools_list)


@tools.route('/pdf-merge')
def pdf_merge():
    """PDF merge tool page."""
    return render_template('tools/pdf_merge.html')


@tools.route('/pdf-toolkit')
def pdf_toolkit():
    """Comprehensive PDF toolkit page."""
    return render_template('tools/pdf_toolkit.html')


@tools.route('/pdf-toolkit', methods=['POST'])
def pdf_toolkit_process():
    """Process PDF toolkit requests."""
    try:
        from tools.pdf_toolkit import PDFToolkit
        
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files')
        tool = request.form.get('tool')
        
        if not tool:
            return jsonify({'error': 'No tool specified'}), 400
        
        if len(files) == 0:
            return jsonify({'error': 'No files selected'}), 400
        
        # Save uploaded files
        input_paths = []
        for file in files:
            if file and file.filename and allowed_file(file.filename, tool):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)
                input_paths.append(filepath)
        
        if len(input_paths) == 0:
            return jsonify({'error': 'No valid files uploaded for this tool'}), 400
        
        # Initialize PDF toolkit
        toolkit = PDFToolkit()
        
        # Process based on tool type
        if tool == 'merge':
            if len(input_paths) < 2:
                return jsonify({'error': 'At least 2 files required for merging'}), 400
            
            merge_order = request.form.get('merge_order', 'upload')
            if merge_order == 'alphabetical':
                input_paths.sort()
            
            from tools.pdf_merge import PDFMerger
            merger = PDFMerger()
            output_path = merger.merge_pdfs(input_paths)
            download_name = 'merged.pdf'
            
        elif tool == 'split':
            if len(input_paths) != 1:
                return jsonify({'error': 'Split requires exactly one PDF file'}), 400
            
            split_method = request.form.get('split_method', 'all')
            if split_method == 'ranges':
                page_ranges = request.form.get('page_ranges', '')
                if not page_ranges:
                    return jsonify({'error': 'Page ranges required for range splitting'}), 400
                pages = page_ranges
            else:
                pages = 'all'
            
            output_files = toolkit.split_pdf(input_paths[0], pages)
            
            # Create zip file for multiple outputs
            import zipfile
            zip_fd, zip_path = tempfile.mkstemp(suffix='.zip', prefix='split_')
            os.close(zip_fd)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for i, file_path in enumerate(output_files):
                    zipf.write(file_path, f"page_{i+1}.pdf")
                    os.remove(file_path)  # Clean up individual files
            
            output_path = zip_path
            download_name = 'split_pages.zip'
            
        elif tool == 'compress':
            if len(input_paths) != 1:
                return jsonify({'error': 'Compress requires exactly one PDF file'}), 400
            
            quality = request.form.get('compression_quality', 'medium')
            output_path = toolkit.compress_pdf(input_paths[0], quality=quality)
            download_name = 'compressed.pdf'
            
        elif tool == 'rotate':
            if len(input_paths) != 1:
                return jsonify({'error': 'Rotate requires exactly one PDF file'}), 400
            
            rotation = int(request.form.get('rotation_angle', 90))
            pages = request.form.get('rotate_pages', 'all')
            output_path = toolkit.rotate_pdf(input_paths[0], rotation, pages)
            download_name = 'rotated.pdf'
            
        elif tool == 'protect':
            if len(input_paths) != 1:
                return jsonify({'error': 'Protect requires exactly one PDF file'}), 400
            
            password = request.form.get('pdf_password')
            password_confirm = request.form.get('pdf_password_confirm')
            
            if not password:
                return jsonify({'error': 'Password is required'}), 400
            
            if password != password_confirm:
                return jsonify({'error': 'Passwords do not match'}), 400
            
            output_path = toolkit.protect_pdf(input_paths[0], password)
            download_name = 'protected.pdf'
            
        elif tool == 'watermark':
            if len(input_paths) != 1:
                return jsonify({'error': 'Watermark requires exactly one PDF file'}), 400
            
            watermark_text = request.form.get('watermark_text')
            opacity = float(request.form.get('watermark_opacity', 0.3))
            
            if not watermark_text:
                return jsonify({'error': 'Watermark text is required'}), 400
            
            output_path = toolkit.add_watermark(input_paths[0], watermark_text, opacity=opacity)
            download_name = 'watermarked.pdf'
            
        elif tool == 'convert_from_pdf':
            if len(input_paths) != 1:
                return jsonify({'error': 'PDF conversion requires exactly one PDF file'}), 400
            
            from tools.pdf_converter import PDFConverter
            converter = PDFConverter()
            
            convert_to_format = request.form.get('convert_to_format', 'word')
            
            if convert_to_format == 'word':
                output_path = converter.pdf_to_word(input_paths[0])
                download_name = 'converted.docx'
                mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif convert_to_format == 'excel':
                output_path = converter.pdf_to_excel(input_paths[0])
                download_name = 'converted.xlsx'
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif convert_to_format == 'text':
                text_content = converter.extract_text_from_pdf(input_paths[0])
                
                # Save as text file
                output_fd, output_path = tempfile.mkstemp(suffix='.txt', prefix='extracted_')
                os.close(output_fd)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                download_name = 'extracted_text.txt'
                mimetype = 'text/plain'
            else:
                return jsonify({'error': f'Unsupported conversion format: {convert_to_format}'}), 400
                
        elif tool == 'convert_to_pdf':
            if len(input_paths) != 1:
                return jsonify({'error': 'Office to PDF conversion requires exactly one file'}), 400
            
            from tools.pdf_converter import PDFConverter
            converter = PDFConverter()
            
            file_path = input_paths[0]
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.doc', '.docx']:
                output_path = converter.word_to_pdf(file_path)
            elif file_ext in ['.xls', '.xlsx']:
                output_path = converter.excel_to_pdf(file_path)
            else:
                return jsonify({'error': f'Unsupported file format: {file_ext}'}), 400
            
            download_name = 'converted.pdf'
            mimetype = 'application/pdf'
            
        elif tool == 'extract_text':
            if len(input_paths) != 1:
                return jsonify({'error': 'Text extraction requires exactly one PDF file'}), 400
            
            from tools.pdf_converter import PDFConverter
            converter = PDFConverter()
            
            text_format = request.form.get('text_format', 'txt')
            text_content = converter.extract_text_from_pdf(input_paths[0])
            
            if text_format == 'txt':
                output_fd, output_path = tempfile.mkstemp(suffix='.txt', prefix='extracted_')
                os.close(output_fd)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                download_name = 'extracted_text.txt'
                mimetype = 'text/plain'
            elif text_format == 'docx':
                # Create Word document with extracted text
                from docx import Document
                doc = Document()
                
                for paragraph in text_content.split('\n\n'):
                    if paragraph.strip():
                        doc.add_paragraph(paragraph.strip())
                
                output_fd, output_path = tempfile.mkstemp(suffix='.docx', prefix='extracted_')
                os.close(output_fd)
                doc.save(output_path)
                
                download_name = 'extracted_text.docx'
                mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            else:
                return jsonify({'error': f'Unsupported text format: {text_format}'}), 400
            
        else:
            return jsonify({'error': f'Tool "{tool}" not yet implemented'}), 400
        
        # Clean up input files
        for path in input_paths:
            if os.path.exists(path):
                os.remove(path)
        
        # Return processed file
        if 'mimetype' in locals():
            return send_file(
                output_path,
                as_attachment=True,
                download_name=download_name,
                mimetype=mimetype
            )
        else:
            return send_file(
                output_path,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/pdf' if download_name.endswith('.pdf') else 'application/zip'
            )
    
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@tools.route('/pdf-merge', methods=['POST'])
def pdf_merge_process():
    """Process PDF merge request."""
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            flash('No files uploaded', 'error')
            return redirect(request.url)
        
        files = request.files.getlist('files')
        
        if len(files) < 2:
            flash('Please upload at least 2 PDF files', 'error')
            return redirect(request.url)
        
        # Validate files
        pdf_paths = []
        for file in files:
            if file and file.filename and allowed_file(file.filename, 'merge'):
                filename = secure_filename(file.filename)
                if filename.endswith('.pdf'):
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    pdf_paths.append(filepath)
        
        if len(pdf_paths) < 2:
            flash('Please upload at least 2 valid PDF files', 'error')
            return redirect(request.url)
        
        # Merge PDFs
        merger = PDFMerger()
        output_path = merger.merge_pdfs(pdf_paths)
        
        # Clean up input files
        for path in pdf_paths:
            if os.path.exists(path):
                os.remove(path)
        
        # Return merged file
        return send_file(
            output_path,
            as_attachment=True,
            download_name='merged.pdf',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        flash(f'Error merging PDFs: {str(e)}', 'error')
        return redirect(request.url)


@tools.route('/qr-generator')
def qr_generator():
    """QR code generator tool page."""
    return render_template('tools/qr_generator.html')


@tools.route('/qr-generator', methods=['POST'])
def qr_generator_process():
    """Process universal QR code generation request."""
    try:
        from tools.qr_generator_pro import generate_qr_code, validate_qr_data, format_data_by_type
        
        # Get QR type and form data
        qr_type = request.form.get('qr_type', 'url')
        
        # Handle file upload for file QR type
        if qr_type == 'file' and 'file_upload' in request.files:
            file = request.files['file_upload']
            if file and file.filename:
                # Check file size (limit to 10MB)
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)  # Reset file pointer
                
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    return jsonify({'success': False, 'error': 'File size too large (max 10MB)'})
                
                if not allowed_file(file.filename, None):  # Use default extensions
                    return jsonify({'success': False, 'error': 'File type not allowed'})
                
                filename = secure_filename(file.filename)
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join('static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file with timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_path = os.path.join(upload_dir, f"{timestamp}_{filename}")
                file.save(file_path)
                
                # Create public URL for the file
                file_url = f"{request.host_url}tools/uploads/{timestamp}_{filename}"
                
                # Generate QR code for the file URL
                qr_img, qr_code_b64 = generate_qr_code(
                    data=file_url,
                    size=int(request.form.get('size', 300)),
                    error_correction=request.form.get('error_correction', 'M'),
                    fg_color=request.form.get('fg_color', '#000000'),
                    bg_color=request.form.get('bg_color', '#ffffff')
                )
                
                return jsonify({
                    'success': True,
                    'qr_code': qr_code_b64,
                    'data': file_url,
                    'type': 'file',
                    'filename': filename
                })
        
        # Validate and format data based on QR type
        is_valid, error_msg, formatted_data = validate_qr_data(qr_type, request.form)
        
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg})
        
        # Get customization options
        size = int(request.form.get('size', 300))
        error_correction = request.form.get('error_correction', 'M')
        fg_color = request.form.get('fg_color', '#000000')
        bg_color = request.form.get('bg_color', '#ffffff')
        
        # Handle logo upload if provided
        logo_path = None
        if 'logo' in request.files and request.files['logo'].filename:
            from tools.qr_generator_pro import save_uploaded_logo
            logo_file = request.files['logo']
            logo_path = save_uploaded_logo(logo_file)
        
        # Generate QR code with customization
        qr_img, qr_code_b64 = generate_qr_code(
            data=formatted_data,
            size=size,
            error_correction=error_correction,
            fg_color=fg_color,
            bg_color=bg_color,
            logo=logo_path
        )
        
        if not qr_code_b64:
            return jsonify({'success': False, 'error': 'Failed to generate QR code'})
        
        # Return success response
        return jsonify({
            'success': True,
            'qr_code': qr_code_b64,
            'data': formatted_data,
            'type': qr_type,
            'size': f"{size}x{size}"
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error generating QR code: {str(e)}'})


# Image Resizer route (placeholder for future implementation)
@tools.route('/image-resizer')
def image_resizer():
    """Image resizer tool page."""
    return render_template('tools/image_resizer.html')


@tools.route('/image-resizer', methods=['POST'])
def image_resizer_process():
    """Process image resizing request."""
    try:
        from tools.image_resizer import ImageResizer
        
        # Check if image was uploaded
        if 'image_upload' not in request.files:
            flash('No image uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['image_upload']
        if not file or not file.filename:
            flash('No image selected', 'error')
            return redirect(request.url)
        
        if not allowed_file(file.filename, None):  # Use default extensions
            flash('Invalid file type. Please upload an image file.', 'error')
            return redirect(request.url)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        input_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(input_path)
        
        # Get resize parameters
        resize_method = request.form.get('resize_method', 'dimensions')
        width = request.form.get('width')
        height = request.form.get('height')
        percentage = request.form.get('percentage')
        maintain_aspect = 'maintain_aspect' in request.form
        quality = int(request.form.get('quality', 95))
        output_format = request.form.get('output_format')
        
        # Convert string inputs to integers
        if width:
            width = int(width)
        if height:
            height = int(height)
        if percentage and resize_method == 'percentage':
            percentage = float(percentage)
        else:
            percentage = None
        
        # Resize image
        resizer = ImageResizer()
        output_path = resizer.resize_image(
            image_path=input_path,
            width=width if resize_method == 'dimensions' else None,
            height=height if resize_method == 'dimensions' else None,
            percentage=percentage,
            maintain_aspect=maintain_aspect,
            quality=quality,
            output_format=output_format
        )
        
        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)
        
        # Determine output filename
        original_name = os.path.splitext(filename)[0]
        if output_format:
            output_extension = f".{output_format.lower()}"
        else:
            output_extension = os.path.splitext(filename)[1]
        
        download_name = f"{original_name}_resized{output_extension}"
        
        # Return resized image
        return send_file(
            output_path,
            as_attachment=True,
            download_name=download_name,
            mimetype=f'image/{output_format.lower() if output_format else "jpeg"}'
        )
    
    except Exception as e:
        flash(f'Error resizing image: {str(e)}', 'error')
        return redirect(request.url)


@tools.route('/qr/<qr_id>')
def qr_redirect(qr_id):
    """Redirect dynamic QR codes and track analytics."""
    from models import QRCode, QRScan
    from datetime import datetime
    
    try:
        qr_record = QRCode.query.filter_by(qr_id=qr_id, is_active=True).first()
        
        if not qr_record:
            return "QR Code not found", 404
        
        # Check if expired
        if qr_record.expires_at and qr_record.expires_at < datetime.utcnow():
            return "QR Code expired", 410
        
        # Record scan analytics
        try:
            scan = QRScan.create_scan(qr_record, request)
            qr_record.increment_scan_count()
        except Exception as scan_error:
            print(f"Scan tracking error: {scan_error}")
        
        # Redirect to current data
        return redirect(qr_record.get_redirect_url())
        
    except Exception as e:
        print(f"QR redirect error: {e}")
        return "Error processing QR code", 500


@tools.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files for QR codes."""
    try:
        upload_dir = os.path.join('static', 'uploads')
        return send_file(os.path.join(upload_dir, filename))
    except Exception as e:
        return "File not found", 404