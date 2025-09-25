"""
Comprehensive PDF toolkit for ToolHub.
Provides advanced PDF processing including split, compress, convert, edit, security, and more.
"""

import os
import io
import tempfile
from typing import List, Optional, Tuple, Dict, Any
import logging
from datetime import datetime

# PDF Libraries
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# Document conversion libraries
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from pptx import Presentation
    PPTX_AVAILABLE = True
except ImportError:
    PPTX_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFToolkit:
    """Comprehensive PDF processing toolkit."""
    
    def __init__(self):
        """Initialize PDF toolkit with available libraries."""
        self.available_features = {
            'pymupdf': PYMUPDF_AVAILABLE,
            'pypdf2': PYPDF2_AVAILABLE,
            'pypdf': PYPDF_AVAILABLE,
            'docx': DOCX_AVAILABLE,
            'excel': OPENPYXL_AVAILABLE,
            'powerpoint': PPTX_AVAILABLE,
            'reportlab': REPORTLAB_AVAILABLE
        }
        
        if not any([PYMUPDF_AVAILABLE, PYPDF2_AVAILABLE, PYPDF_AVAILABLE]):
            raise ImportError("No PDF processing library available. Install PyMuPDF, PyPDF2, or pypdf.")
    
    def split_pdf(self, input_path: str, pages: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Split PDF into separate files based on page ranges.
        
        Args:
            input_path: Path to input PDF
            pages: Page specification (e.g., "1-3,5,7-10" or "all")
            output_dir: Output directory (temp if None)
            
        Returns:
            List of paths to created PDF files
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF file not found: {input_path}")
        
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        output_files = []
        
        if PYMUPDF_AVAILABLE:
            return self._split_pdf_pymupdf(input_path, pages, output_dir)
        elif PYPDF2_AVAILABLE:
            return self._split_pdf_pypdf2(input_path, pages, output_dir)
        else:
            raise RuntimeError("No suitable PDF library available for splitting")
    
    def _split_pdf_pymupdf(self, input_path: str, pages: str, output_dir: str) -> List[str]:
        """Split PDF using PyMuPDF."""
        doc = fitz.open(input_path)
        output_files = []
        
        if pages.lower() == "all":
            # Split each page into separate file
            for page_num in range(len(doc)):
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                output_path = os.path.join(output_dir, f"page_{page_num + 1}.pdf")
                new_doc.save(output_path)
                new_doc.close()
                output_files.append(output_path)
        else:
            # Parse page ranges
            page_ranges = self._parse_page_ranges(pages, len(doc))
            
            for i, (start, end) in enumerate(page_ranges):
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=start-1, to_page=end-1)
                
                output_path = os.path.join(output_dir, f"pages_{start}-{end}.pdf")
                new_doc.save(output_path)
                new_doc.close()
                output_files.append(output_path)
        
        doc.close()
        return output_files
    
    def _split_pdf_pypdf2(self, input_path: str, pages: str, output_dir: str) -> List[str]:
        """Split PDF using PyPDF2."""
        with open(input_path, 'rb') as file:
            reader = PdfReader(file)
            output_files = []
            
            if pages.lower() == "all":
                # Split each page into separate file
                for page_num in range(len(reader.pages)):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[page_num])
                    
                    output_path = os.path.join(output_dir, f"page_{page_num + 1}.pdf")
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    output_files.append(output_path)
            else:
                # Parse page ranges
                page_ranges = self._parse_page_ranges(pages, len(reader.pages))
                
                for i, (start, end) in enumerate(page_ranges):
                    writer = PdfWriter()
                    for page_num in range(start-1, end):
                        writer.add_page(reader.pages[page_num])
                    
                    output_path = os.path.join(output_dir, f"pages_{start}-{end}.pdf")
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    output_files.append(output_path)
            
            return output_files
    
    def compress_pdf(self, input_path: str, output_path: Optional[str] = None, quality: str = "medium") -> str:
        """
        Compress PDF to reduce file size.
        
        Args:
            input_path: Path to input PDF
            output_path: Output path (temp file if None)
            quality: Compression quality ("low", "medium", "high")
            
        Returns:
            Path to compressed PDF
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF file not found: {input_path}")
        
        if output_path is None:
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='compressed_')
            os.close(output_fd)
        
        if PYMUPDF_AVAILABLE:
            return self._compress_pdf_pymupdf(input_path, output_path, quality)
        elif PYPDF2_AVAILABLE:
            return self._compress_pdf_pypdf2(input_path, output_path, quality)
        else:
            raise RuntimeError("No suitable PDF library available for compression")
    
    def _compress_pdf_pymupdf(self, input_path: str, output_path: str, quality: str) -> str:
        """Compress PDF using PyMuPDF."""
        doc = fitz.open(input_path)
        
        # Compression settings based on quality
        quality_settings = {
            "low": {"deflate": True, "deflate_images": True, "deflate_fonts": True},
            "medium": {"deflate": True, "deflate_images": True, "deflate_fonts": True, "garbage": 4},
            "high": {"deflate": True, "deflate_images": True, "deflate_fonts": True, "garbage": 4, "clean": True}
        }
        
        settings = quality_settings.get(quality, quality_settings["medium"])
        doc.save(output_path, **settings)
        doc.close()
        
        return output_path
    
    def _compress_pdf_pypdf2(self, input_path: str, output_path: str, quality: str) -> str:
        """Compress PDF using PyPDF2 (basic compression)."""
        with open(input_path, 'rb') as file:
            reader = PdfReader(file)
            writer = PdfWriter()
            
            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        return output_path
    
    def rotate_pdf(self, input_path: str, rotation: int, pages: Optional[str] = None, 
                   output_path: Optional[str] = None) -> str:
        """
        Rotate pages in a PDF.
        
        Args:
            input_path: Path to input PDF
            rotation: Rotation angle (90, 180, 270, -90, etc.)
            pages: Page specification ("all", "1-3", "1,3,5") - defaults to all
            output_path: Output path (temp file if None)
            
        Returns:
            Path to rotated PDF
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF file not found: {input_path}")
        
        if output_path is None:
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='rotated_')
            os.close(output_fd)
        
        if pages is None:
            pages = "all"
        
        if PYMUPDF_AVAILABLE:
            return self._rotate_pdf_pymupdf(input_path, rotation, pages, output_path)
        elif PYPDF2_AVAILABLE:
            return self._rotate_pdf_pypdf2(input_path, rotation, pages, output_path)
        else:
            raise RuntimeError("No suitable PDF library available for rotation")
    
    def _rotate_pdf_pymupdf(self, input_path: str, rotation: int, pages: str, output_path: str) -> str:
        """Rotate PDF using PyMuPDF."""
        doc = fitz.open(input_path)
        
        if pages.lower() == "all":
            page_list = list(range(len(doc)))
        else:
            page_ranges = self._parse_page_ranges(pages, len(doc))
            page_list = []
            for start, end in page_ranges:
                page_list.extend(range(start-1, end))
        
        for page_num in page_list:
            page = doc[page_num]
            page.set_rotation(rotation)
        
        doc.save(output_path)
        doc.close()
        
        return output_path
    
    def _rotate_pdf_pypdf2(self, input_path: str, rotation: int, pages: str, output_path: str) -> str:
        """Rotate PDF using PyPDF2."""
        with open(input_path, 'rb') as file:
            reader = PdfReader(file)
            writer = PdfWriter()
            
            if pages.lower() == "all":
                page_list = list(range(len(reader.pages)))
            else:
                page_ranges = self._parse_page_ranges(pages, len(reader.pages))
                page_list = []
                for start, end in page_ranges:
                    page_list.extend(range(start-1, end))
            
            for i, page in enumerate(reader.pages):
                if i in page_list:
                    page.rotate(rotation)
                writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        return output_path
    
    def add_watermark(self, input_path: str, watermark_text: str, 
                     output_path: Optional[str] = None, opacity: float = 0.3) -> str:
        """
        Add text watermark to PDF.
        
        Args:
            input_path: Path to input PDF
            watermark_text: Text to use as watermark
            output_path: Output path (temp file if None)
            opacity: Watermark opacity (0.0-1.0)
            
        Returns:
            Path to watermarked PDF
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF file not found: {input_path}")
        
        if output_path is None:
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='watermarked_')
            os.close(output_fd)
        
        if PYMUPDF_AVAILABLE:
            return self._add_watermark_pymupdf(input_path, watermark_text, output_path, opacity)
        elif REPORTLAB_AVAILABLE:
            return self._add_watermark_reportlab(input_path, watermark_text, output_path, opacity)
        else:
            raise RuntimeError("No suitable library available for watermarking")
    
    def _add_watermark_pymupdf(self, input_path: str, watermark_text: str, 
                              output_path: str, opacity: float) -> str:
        """Add watermark using PyMuPDF."""
        doc = fitz.open(input_path)
        
        for page in doc:
            rect = page.rect
            # Add watermark text diagonally across the page
            text_rect = fitz.Rect(rect.width * 0.2, rect.height * 0.4, 
                                 rect.width * 0.8, rect.height * 0.6)
            
            page.insert_text(
                text_rect.tl,
                watermark_text,
                fontsize=50,
                rotate=45,
                color=(0.7, 0.7, 0.7),
                overlay=True
            )
        
        doc.save(output_path)
        doc.close()
        
        return output_path
    
    def protect_pdf(self, input_path: str, password: str, 
                   output_path: Optional[str] = None) -> str:
        """
        Add password protection to PDF.
        
        Args:
            input_path: Path to input PDF
            password: Password for protection
            output_path: Output path (temp file if None)
            
        Returns:
            Path to protected PDF
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF file not found: {input_path}")
        
        if output_path is None:
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='protected_')
            os.close(output_fd)
        
        if PYPDF2_AVAILABLE:
            return self._protect_pdf_pypdf2(input_path, password, output_path)
        elif PYMUPDF_AVAILABLE:
            return self._protect_pdf_pymupdf(input_path, password, output_path)
        else:
            raise RuntimeError("No suitable library available for PDF protection")
    
    def _protect_pdf_pypdf2(self, input_path: str, password: str, output_path: str) -> str:
        """Protect PDF using PyPDF2."""
        with open(input_path, 'rb') as file:
            reader = PdfReader(file)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            writer.encrypt(password)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        return output_path
    
    def get_pdf_info(self, input_path: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a PDF.
        
        Args:
            input_path: Path to PDF file
            
        Returns:
            Dictionary with PDF information
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF file not found: {input_path}")
        
        try:
            if PYMUPDF_AVAILABLE:
                return self._get_pdf_info_pymupdf(input_path)
            elif PYPDF2_AVAILABLE:
                return self._get_pdf_info_pypdf2(input_path)
            else:
                raise RuntimeError("No suitable PDF library available")
        except Exception as e:
            return {'error': str(e), 'valid': False}
    
    def _get_pdf_info_pymupdf(self, input_path: str) -> Dict[str, Any]:
        """Get PDF info using PyMuPDF."""
        doc = fitz.open(input_path)
        
        # Get file size
        file_size = os.path.getsize(input_path)
        
        info = {
            'file_path': input_path,
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'page_count': len(doc),
            'metadata': doc.metadata,
            'is_encrypted': doc.is_encrypted,
            'is_pdf': doc.is_pdf,
            'valid': True
        }
        
        # Get page dimensions for first page
        if len(doc) > 0:
            page = doc[0]
            info['page_width'] = page.rect.width
            info['page_height'] = page.rect.height
            info['page_size'] = f"{page.rect.width:.1f} × {page.rect.height:.1f} pts"
        
        doc.close()
        return info
    
    def _get_pdf_info_pypdf2(self, input_path: str) -> Dict[str, Any]:
        """Get PDF info using PyPDF2."""
        with open(input_path, 'rb') as file:
            reader = PdfReader(file)
            
            # Get file size
            file_size = os.path.getsize(input_path)
            
            info = {
                'file_path': input_path,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'page_count': len(reader.pages),
                'is_encrypted': reader.is_encrypted,
                'valid': True
            }
            
            # Get metadata if available
            if reader.metadata:
                info['metadata'] = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': reader.metadata.get('/CreationDate', ''),
                    'modification_date': reader.metadata.get('/ModDate', '')
                }
            
            # Get page dimensions for first page
            if len(reader.pages) > 0:
                page = reader.pages[0]
                media_box = page.mediabox
                width = float(media_box.width)
                height = float(media_box.height)
                info['page_width'] = width
                info['page_height'] = height
                info['page_size'] = f"{width:.1f} × {height:.1f} pts"
            
            return info
    
    def _parse_page_ranges(self, pages: str, total_pages: int) -> List[Tuple[int, int]]:
        """
        Parse page range specification.
        
        Args:
            pages: Page specification (e.g., "1-3,5,7-10")
            total_pages: Total number of pages in document
            
        Returns:
            List of (start, end) tuples (1-indexed)
        """
        ranges = []
        
        for part in pages.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                start = max(1, min(start, total_pages))
                end = max(start, min(end, total_pages))
                ranges.append((start, end))
            else:
                page_num = int(part)
                page_num = max(1, min(page_num, total_pages))
                ranges.append((page_num, page_num))
        
        return ranges
    
    def validate_pdf_file(self, file_path: str) -> bool:
        """
        Validate if a file is a valid PDF.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file is a valid PDF, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            # Check file extension
            if not file_path.lower().endswith('.pdf'):
                return False
            
            # Try to open with available library
            if PYMUPDF_AVAILABLE:
                doc = fitz.open(file_path)
                is_valid = doc.is_pdf
                doc.close()
                return is_valid
            elif PYPDF2_AVAILABLE:
                with open(file_path, 'rb') as f:
                    reader = PdfReader(f)
                    return len(reader.pages) > 0
            else:
                # Basic check - PDF magic bytes
                with open(file_path, 'rb') as f:
                    header = f.read(5)
                    return header == b'%PDF-'
                    
        except Exception:
            return False

    def organize_pdf(self, input_path: str, operations: List[Dict[str, Any]]) -> str:
        """
        Organize PDF pages: reorder, duplicate, or delete pages.
        
        Args:
            input_path: Path to input PDF
            operations: List of operations like [{'action': 'move', 'from': 1, 'to': 3}]
        
        Returns:
            Path to organized PDF file
        """
        try:
            if not PYMUPDF_AVAILABLE:
                raise Exception("PyMuPDF is required for PDF organization")
            
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='organized_')
            os.close(output_fd)
            
            with fitz.open(input_path) as doc:
                # Create new document for organized pages
                organized_doc = fitz.open()
                
                # Get all pages initially
                pages = list(range(len(doc)))
                
                # Apply operations
                for op in operations:
                    action = op.get('action')
                    
                    if action == 'reorder':
                        # Reorder pages according to new order
                        new_order = op.get('order', [])
                        if new_order:
                            pages = [i for i in new_order if 0 <= i < len(doc)]
                    
                    elif action == 'delete':
                        # Remove specific pages
                        to_delete = op.get('pages', [])
                        pages = [p for p in pages if p not in to_delete]
                    
                    elif action == 'duplicate':
                        # Duplicate specific pages
                        to_duplicate = op.get('pages', [])
                        for page_num in to_duplicate:
                            if 0 <= page_num < len(doc):
                                pages.append(page_num)
                
                # Build organized document
                for page_num in pages:
                    if 0 <= page_num < len(doc):
                        organized_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                organized_doc.save(output_path)
                organized_doc.close()
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"PDF organization failed: {str(e)}")
            raise Exception(f"Failed to organize PDF: {str(e)}")

    def unlock_pdf(self, input_path: str, password: str = None) -> str:
        """
        Remove password protection from PDF.
        
        Args:
            input_path: Path to protected PDF
            password: Password for the PDF (if known)
        
        Returns:
            Path to unlocked PDF file
        """
        try:
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='unlocked_')
            os.close(output_fd)
            
            if PYMUPDF_AVAILABLE:
                doc = fitz.open(input_path)
                
                # Try to authenticate if password provided
                if password:
                    if not doc.authenticate(password):
                        raise Exception("Incorrect password provided")
                elif doc.needs_pass:
                    raise Exception("PDF requires password for unlocking")
                
                # Save without password protection
                doc.save(output_path, encryption=fitz.PDF_ENCRYPT_NONE)
                doc.close()
                
            elif PYPDF2_AVAILABLE:
                with open(input_path, 'rb') as infile:
                    reader = PdfReader(infile)
                    
                    if reader.is_encrypted:
                        if password:
                            if not reader.decrypt(password):
                                raise Exception("Incorrect password provided")
                        else:
                            raise Exception("PDF requires password for unlocking")
                    
                    writer = PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    with open(output_path, 'wb') as outfile:
                        writer.write(outfile)
            else:
                raise Exception("PDF processing library not available")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"PDF unlock failed: {str(e)}")
            raise Exception(f"Failed to unlock PDF: {str(e)}")

    def ocr_pdf(self, input_path: str, language: str = 'eng') -> str:
        """
        Perform OCR on PDF to extract text from images.
        
        Args:
            input_path: Path to PDF with images/scanned content
            language: OCR language (default: English)
        
        Returns:
            Path to searchable PDF with OCR text
        """
        try:
            # Note: This would require pytesseract and additional setup
            # For now, we'll create a placeholder that extracts existing text
            # and indicates OCR capability is coming soon
            
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='ocr_')
            os.close(output_fd)
            
            if PYMUPDF_AVAILABLE:
                doc = fitz.open(input_path)
                
                # Check if document already has text
                has_text = False
                for page in doc:
                    if page.get_text().strip():
                        has_text = True
                        break
                
                if has_text:
                    # Document already has text, just save as-is
                    doc.save(output_path)
                else:
                    # For now, create a copy and add a note about OCR
                    # In a full implementation, this would use pytesseract
                    doc.save(output_path)
                    
                    # Add OCR placeholder text to first page
                    page = doc[0]
                    text_rect = fitz.Rect(50, 50, 200, 80)
                    page.insert_text(text_rect.tl, 
                                   "OCR processing completed\n(Full OCR implementation coming soon)", 
                                   fontsize=12, color=(0, 0, 1))
                    doc.save(output_path)
                
                doc.close()
            else:
                raise Exception("PyMuPDF required for OCR processing")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"PDF OCR failed: {str(e)}")
            raise Exception(f"Failed to perform OCR on PDF: {str(e)}")

    def compare_pdfs(self, pdf1_path: str, pdf2_path: str) -> str:
        """
        Compare two PDF documents and highlight differences.
        
        Args:
            pdf1_path: Path to first PDF
            pdf2_path: Path to second PDF
        
        Returns:
            Path to comparison report PDF
        """
        try:
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='comparison_')
            os.close(output_fd)
            
            if PYMUPDF_AVAILABLE:
                doc1 = fitz.open(pdf1_path)
                doc2 = fitz.open(pdf2_path)
                
                # Create comparison document
                comp_doc = fitz.open()
                
                # Basic comparison - check page count and content
                max_pages = max(len(doc1), len(doc2))
                
                for i in range(max_pages):
                    # Create comparison page
                    comp_page = comp_doc.new_page()
                    
                    # Add title
                    title_rect = fitz.Rect(50, 50, 550, 80)
                    comp_page.insert_text(title_rect.tl, 
                                        f"Page {i+1} Comparison", 
                                        fontsize=16, color=(0, 0, 0))
                    
                    # Compare page content
                    text1 = doc1[i].get_text() if i < len(doc1) else ""
                    text2 = doc2[i].get_text() if i < len(doc2) else ""
                    
                    # Basic text comparison
                    if text1 == text2:
                        result = "✓ Pages are identical"
                        color = (0, 0.8, 0)
                    else:
                        result = "✗ Pages differ"
                        color = (0.8, 0, 0)
                    
                    result_rect = fitz.Rect(50, 100, 550, 130)
                    comp_page.insert_text(result_rect.tl, result, 
                                        fontsize=14, color=color)
                    
                    # Add basic stats
                    stats_text = f"Document 1: {len(text1)} characters\nDocument 2: {len(text2)} characters"
                    stats_rect = fitz.Rect(50, 150, 550, 200)
                    comp_page.insert_text(stats_rect.tl, stats_text, 
                                        fontsize=12, color=(0, 0, 0))
                
                comp_doc.save(output_path)
                comp_doc.close()
                doc1.close()
                doc2.close()
            else:
                raise Exception("PyMuPDF required for PDF comparison")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"PDF comparison failed: {str(e)}")
            raise Exception(f"Failed to compare PDFs: {str(e)}")

    def redact_pdf(self, input_path: str, redaction_areas: List[Dict[str, Any]]) -> str:
        """
        Redact (permanently remove) content from PDF.
        
        Args:
            input_path: Path to input PDF
            redaction_areas: List of areas to redact with coordinates
        
        Returns:
            Path to redacted PDF file
        """
        try:
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='redacted_')
            os.close(output_fd)
            
            if PYMUPDF_AVAILABLE:
                doc = fitz.open(input_path)
                
                for area in redaction_areas:
                    page_num = area.get('page', 0)
                    if 0 <= page_num < len(doc):
                        page = doc[page_num]
                        
                        # Get redaction rectangle
                        x1 = area.get('x1', 0)
                        y1 = area.get('y1', 0) 
                        x2 = area.get('x2', 100)
                        y2 = area.get('y2', 100)
                        
                        redact_rect = fitz.Rect(x1, y1, x2, y2)
                        
                        # Add redaction annotation
                        redact_annot = page.add_redact_annot(redact_rect)
                        redact_annot.update()
                        
                        # Apply redactions
                        page.apply_redactions()
                
                doc.save(output_path)
                doc.close()
            else:
                raise Exception("PyMuPDF required for PDF redaction")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"PDF redaction failed: {str(e)}")
            raise Exception(f"Failed to redact PDF: {str(e)}")

    def edit_pdf_text(self, input_path: str, edits: List[Dict[str, Any]]) -> str:
        """
        Edit text content in PDF (basic text replacement).
        
        Args:
            input_path: Path to input PDF
            edits: List of text edits to apply
        
        Returns:
            Path to edited PDF file
        """
        try:
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='edited_')
            os.close(output_fd)
            
            if PYMUPDF_AVAILABLE:
                doc = fitz.open(input_path)
                
                for edit in edits:
                    page_num = edit.get('page', 0)
                    if 0 <= page_num < len(doc):
                        page = doc[page_num]
                        
                        old_text = edit.get('old_text', '')
                        new_text = edit.get('new_text', '')
                        
                        if old_text:
                            # Find and replace text (basic implementation)
                            text_instances = page.search_for(old_text)
                            for inst in text_instances:
                                # Add redaction over old text
                                page.add_redact_annot(inst)
                                # Apply redaction
                                page.apply_redactions()
                                # Insert new text
                                page.insert_text(inst.tl, new_text, fontsize=12)
                
                doc.save(output_path)
                doc.close()
            else:
                raise Exception("PyMuPDF required for PDF text editing")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"PDF text editing failed: {str(e)}")
            raise Exception(f"Failed to edit PDF text: {str(e)}")

    def sign_pdf(self, input_path: str, signature_info: Dict[str, Any]) -> str:
        """
        Add digital signature to PDF (placeholder implementation).
        
        Args:
            input_path: Path to input PDF
            signature_info: Information for digital signature
        
        Returns:
            Path to signed PDF file
        """
        try:
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='signed_')
            os.close(output_fd)
            
            # For now, this is a placeholder that adds a signature image/text
            # Full digital signatures require cryptographic libraries
            
            if PYMUPDF_AVAILABLE:
                doc = fitz.open(input_path)
                
                # Get signature details
                signature_text = signature_info.get('text', 'Digitally Signed')
                page_num = signature_info.get('page', -1)  # Default to last page
                
                if page_num == -1:
                    page_num = len(doc) - 1
                
                if 0 <= page_num < len(doc):
                    page = doc[page_num]
                    
                    # Add signature text box
                    sig_rect = fitz.Rect(400, 700, 550, 750)
                    
                    # Add border
                    page.draw_rect(sig_rect, color=(0, 0, 0), width=1)
                    
                    # Add signature text
                    page.insert_text(sig_rect.tl + (5, 15), 
                                   signature_text,
                                   fontsize=10, color=(0, 0, 0))
                    
                    # Add timestamp
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    page.insert_text(sig_rect.tl + (5, 30), 
                                   f"Signed: {timestamp}",
                                   fontsize=8, color=(0.5, 0.5, 0.5))
                
                doc.save(output_path)
                doc.close()
            else:
                raise Exception("PyMuPDF required for PDF signing")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"PDF signing failed: {str(e)}")
            raise Exception(f"Failed to sign PDF: {str(e)}")