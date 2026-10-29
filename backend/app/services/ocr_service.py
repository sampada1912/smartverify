import os
import json
from typing import Dict, List, Any, Tuple
import fitz  # PyMuPDF
from PIL import Image
import io

import csv

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


class DocumentExtractionResult:
    def __init__(
        self,
        full_text: str,
        page_texts: List[str],
        page_count: int,
        engine_used: str,
        metadata: Dict[str, Any]
    ):
        self.full_text = full_text
        self.page_texts = page_texts
        self.page_count = page_count
        self.engine_used = engine_used
        self.metadata = metadata


class OCRService:
    def __init__(self):
        self.tesseract_available = PYTESSERACT_AVAILABLE
        if self.tesseract_available:
            try:
                # Test tesseract binary responsiveness
                pytesseract.get_tesseract_version()
            except Exception:
                self.tesseract_available = False

    def extract_from_file(self, file_path: str, mime_type: str) -> DocumentExtractionResult:
        if mime_type == "application/pdf" or file_path.lower().endswith(".pdf"):
            return self._extract_pdf(file_path)
        elif file_path.lower().endswith(".csv") or mime_type in ("text/csv", "application/csv"):
            return self._extract_csv(file_path)
        else:
            return self._extract_image(file_path)

    def _extract_csv(self, file_path: str) -> DocumentExtractionResult:
        rows: List[List[str]] = []
        encoding = "utf-8"
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                for row in reader:
                    rows.append(row)
        except UnicodeDecodeError:
            encoding = "latin-1"
            rows = []
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        rows.append(row)
            except Exception as e:
                return DocumentExtractionResult(
                    full_text=f"[CSV Parsing Error: {str(e)}]",
                    page_texts=[""],
                    page_count=1,
                    engine_used="CSV_PARSER_ERROR",
                    metadata={"format": "csv", "error": str(e)}
                )
        except Exception as e:
            return DocumentExtractionResult(
                full_text=f"[CSV Parsing Error: {str(e)}]",
                page_texts=[""],
                page_count=1,
                engine_used="CSV_PARSER_ERROR",
                metadata={"format": "csv", "error": str(e)}
            )

        headers = rows[0] if rows else []
        row_count = len(rows) - 1 if len(rows) > 1 else len(rows)
        
        text_lines = [
            f"[Structured CSV Data: {row_count} rows, {len(headers)} columns]",
            f"Columns: {', '.join(headers)}"
        ]
        for row in rows[1:101]:
            text_lines.append(" | ".join(row))
        if len(rows) > 101:
            text_lines.append(f"... [{len(rows) - 101} more rows truncated]")

        full_text = "\n".join(text_lines)
        metadata = {
            "format": "csv",
            "encoding": encoding,
            "row_count": row_count,
            "column_count": len(headers),
            "columns": headers[:20]
        }
        
        return DocumentExtractionResult(
            full_text=full_text,
            page_texts=[full_text],
            page_count=1,
            engine_used="CSV_PARSER",
            metadata=metadata
        )

    def _extract_pdf(self, file_path: str) -> DocumentExtractionResult:
        doc = fitz.open(file_path)
        page_count = len(doc)
        page_texts: List[str] = []
        full_text_chunks: List[str] = []
        engine_used = "PYMUPDF_NATIVE"
        
        # Read PDF metadata
        raw_metadata = doc.metadata or {}
        cleaned_metadata = {
            "title": raw_metadata.get("title", ""),
            "author": raw_metadata.get("author", ""),
            "subject": raw_metadata.get("subject", ""),
            "creator": raw_metadata.get("creator", ""),
            "producer": raw_metadata.get("producer", ""),
            "creationDate": raw_metadata.get("creationDate", ""),
            "modDate": raw_metadata.get("modDate", ""),
        }

        scanned_pages_count = 0

        for i in range(page_count):
            page = doc[i]
            text = page.get_text().strip()
            
            # If native text is empty or very short, attempt OCR if available
            if len(text) < 30:
                scanned_pages_count += 1
                ocr_text = self._try_ocr_pdf_page(page)
                if ocr_text:
                    text = ocr_text
                    engine_used = "TESSERACT_OCR_HYBRID"
            
            page_texts.append(text)
            full_text_chunks.append(text)

        doc.close()
        full_text = "\n\n--- PAGE BREAK ---\n\n".join(full_text_chunks)
        
        return DocumentExtractionResult(
            full_text=full_text,
            page_texts=page_texts,
            page_count=page_count,
            engine_used=engine_used,
            metadata=cleaned_metadata
        )

    def _try_ocr_pdf_page(self, page) -> str:
        if not self.tesseract_available:
            return ""
        try:
            pix = page.get_pixmap(dpi=150)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)
            return text.strip()
        except Exception:
            return ""

    def _extract_image(self, file_path: str) -> DocumentExtractionResult:
        metadata = {"format": "image"}
        if self.tesseract_available:
            try:
                img = Image.open(file_path)
                metadata["size"] = f"{img.width}x{img.height}"
                text = pytesseract.image_to_string(img).strip()
                return DocumentExtractionResult(
                    full_text=text,
                    page_texts=[text],
                    page_count=1,
                    engine_used="TESSERACT_OCR",
                    metadata=metadata
                )
            except Exception as e:
                return DocumentExtractionResult(
                    full_text=f"[OCR Processing Error: {str(e)}]",
                    page_texts=[""],
                    page_count=1,
                    engine_used="OCR_FAILED",
                    metadata=metadata
                )
        else:
            return DocumentExtractionResult(
                full_text="[Image uploaded. Native Tesseract OCR binary not detected on host system. Please install tesseract or upload native text PDFs.]",
                page_texts=[""],
                page_count=1,
                engine_used="OCR_NOT_AVAILABLE",
                metadata=metadata
            )


ocr_service = OCRService()
