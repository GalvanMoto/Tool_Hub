"""
PDF merge functionality for ToolHub.
Provides tools to combine multiple PDF files into a single document.
"""

import os
import tempfile
from typing import List
try:
    from PyPDF2 import PdfMerger
except ImportError:
    # Fallback for older PyPDF2 versions
    try:
        from PyPDF2 import PdfFileMerger as PdfMerger
    except ImportError:
        PdfMerger = None


class PDFMerger:
    """Handles PDF merging operations."""
    
    def __init__(self):
        """Initialize PDF merger."""
        if PdfMerger is None:
            raise ImportError("PyPDF2 is required for PDF operations. Install with: pip install PyPDF2")
    
    def merge_pdfs(self, pdf_paths: List[str], output_filename: str = None) -> str:
        """
        Merge multiple PDF files into a single document.
        
        Args:
            pdf_paths: List of paths to PDF files to merge
            output_filename: Optional output filename, generates temp file if None
            
        Returns:
            Path to the merged PDF file
            
        Raises:
            FileNotFoundError: If any input PDF file doesn't exist
            Exception: If merging fails
        """
        if not pdf_paths or len(pdf_paths) < 2:
            raise ValueError("At least 2 PDF files are required for merging")
        
        # Validate all input files exist
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Generate output path
        if output_filename is None:
            output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='merged_')
            os.close(output_fd)  # Close file descriptor, we'll write to the path directly
        else:
            output_path = output_filename
        
        try:
            # Create merger instance
            merger = PdfMerger()
            
            # Add each PDF to the merger
            for pdf_path in pdf_paths:
                with open(pdf_path, 'rb') as pdf_file:
                    merger.append(pdf_file)
            
            # Write merged PDF
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            # Close merger
            merger.close()
            
            return output_path
            
        except Exception as e:
            # Clean up output file if creation failed
            if os.path.exists(output_path):
                os.remove(output_path)
            raise Exception(f"Failed to merge PDFs: {str(e)}")
    
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
            
            # Simple validation - check file extension and magic bytes
            if not file_path.lower().endswith('.pdf'):
                return False
            
            with open(file_path, 'rb') as f:
                header = f.read(5)
                return header == b'%PDF-'
                
        except Exception:
            return False
    
    def get_pdf_info(self, file_path: str) -> dict:
        """
        Get basic information about a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF information (pages, size, etc.)
        """
        try:
            if not self.validate_pdf_file(file_path):
                raise ValueError("Invalid PDF file")
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Try to get page count using PyPDF2
            try:
                from PyPDF2 import PdfReader
                with open(file_path, 'rb') as f:
                    reader = PdfReader(f)
                    page_count = len(reader.pages)
            except Exception:
                page_count = "Unknown"
            
            return {
                'file_path': file_path,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'page_count': page_count,
                'valid': True
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'valid': False
            }