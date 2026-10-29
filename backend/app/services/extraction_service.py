import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.document import DocumentType


class ExtractedFieldData:
    def __init__(
        self,
        field_name: str,
        extracted_value: str,
        normalized_value: str,
        page_number: int = 1,
        confidence: float = 0.90,
        extraction_method: str = "REGEX_PATTERN",
        snippet: Optional[str] = None
    ):
        self.field_name = field_name
        self.extracted_value = extracted_value
        self.normalized_value = normalized_value
        self.page_number = page_number
        self.confidence = confidence
        self.extraction_method = extraction_method
        self.snippet = snippet


class ExtractionService:
    DATE_PATTERNS = [
        # DD/MM/YYYY or DD-MM-YYYY
        (r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", "%d-%m-%Y"),
        # YYYY-MM-DD
        (r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", "%Y-%m-%d"),
        # DD Month YYYY (e.g. 15 July 2025 or 15th July 2025)
        (r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b", "%d %B %Y"),
    ]

    def normalize_date(self, raw_str: str) -> Optional[str]:
        if not raw_str:
            return None
        cleaned = raw_str.strip()
        
        # Try DD/MM/YYYY or DD-MM-YYYY
        m = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", cleaned)
        if m:
            day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
            try:
                dt = datetime(year, month, day)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Try YYYY-MM-DD
        m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", cleaned)
        if m:
            year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
            try:
                dt = datetime(year, month, day)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Try textual month
        for fmt in ["%d %B %Y", "%d %b %Y"]:
            try:
                # Remove st, nd, rd, th
                cleaned_text = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", cleaned)
                dt = datetime.strptime(cleaned_text, fmt)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                continue

        return raw_str.strip()

    def normalize_institution_id(self, raw_id: str) -> str:
        # Expected standard format: 1-XXXXXXXXXX
        m = re.search(r"1-\d{8,12}", raw_id)
        if m:
            return m.group(0)
        return raw_id.strip()

    def normalize_numeric(self, raw_val: str) -> str:
        digits = re.sub(r"[^\d.]", "", raw_val)
        return digits

    def _get_snippet(self, text: str, match_start: int, match_end: int, window: int = 70) -> str:
        start = max(0, match_start - window)
        end = min(len(text), match_end + window)
        snippet = text[start:end].replace("\n", " ").strip()
        return f"... {snippet} ..."

    def extract_fields(self, full_text: str, page_texts: List[str], doc_type: DocumentType) -> List[ExtractedFieldData]:
        fields: List[ExtractedFieldData] = []
        if not full_text:
            return fields

        # 1. Institution ID (AICTE Standard format: 1-XXXXXXXXXX or Permanent Institute Id)
        id_match = re.search(r"(?:Permanent\s+Institute\s+Id|Institution\s+ID|AICTE\s+ID|PID)[:\s]*([1-9]-\d{8,11})", full_text, re.IGNORECASE)
        if not id_match:
            id_match = re.search(r"\b(1-\d{8,11})\b", full_text)
        if id_match:
            raw_val = id_match.group(1)
            norm_val = self.normalize_institution_id(raw_val)
            page_no = self._find_page(page_texts, raw_val)
            snippet = self._get_snippet(full_text, id_match.start(), id_match.end())
            fields.append(ExtractedFieldData(
                field_name="institution_id",
                extracted_value=raw_val,
                normalized_value=norm_val,
                page_number=page_no,
                confidence=0.96,
                snippet=snippet
            ))

        # 2. Institution Name
        name_match = re.search(r"(?:Name\s+of\s+the\s+(?:Institution|Institute|College)|Institute\s+Name)[:\s]*([^\n\r,]+(?:Institute|College|University|Academy|Engineering|Technology|Sciences)[^\n\r]*)", full_text, re.IGNORECASE)
        if name_match:
            raw_name = name_match.group(1).strip()
            norm_name = re.sub(r"\s+", " ", raw_name).strip()
            page_no = self._find_page(page_texts, raw_name)
            snippet = self._get_snippet(full_text, name_match.start(), name_match.end())
            fields.append(ExtractedFieldData(
                field_name="institution_name",
                extracted_value=raw_name,
                normalized_value=norm_name,
                page_number=page_no,
                confidence=0.92,
                snippet=snippet
            ))

        # 3. Reference / Certificate Number
        ref_match = re.search(r"(?:F\.?\s*No\.?|File\s+No\.?|Letter\s+No\.?|Ref\s+No\.?|Certificate\s+No\.?|NOC\s+No\.?|Order\s+No\.?)[:\s]*([A-Z0-9/_\-\.]{5,40})", full_text, re.IGNORECASE)
        if ref_match:
            raw_ref = ref_match.group(1).strip()
            page_no = self._find_page(page_texts, raw_ref)
            snippet = self._get_snippet(full_text, ref_match.start(), ref_match.end())
            fields.append(ExtractedFieldData(
                field_name="reference_number",
                extracted_value=raw_ref,
                normalized_value=raw_ref.upper(),
                page_number=page_no,
                confidence=0.94,
                snippet=snippet
            ))

        # 4. Issue Date
        issue_date_match = re.search(r"(?:Date\s+of\s+Issue|Issue\s+Date|Dated|Date)[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4}|[0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+[0-9]{4}|[0-9]{4}-[0-9]{2}-[0-9]{2})", full_text, re.IGNORECASE)
        if issue_date_match:
            raw_date = issue_date_match.group(1).strip()
            norm_date = self.normalize_date(raw_date) or raw_date
            page_no = self._find_page(page_texts, raw_date)
            snippet = self._get_snippet(full_text, issue_date_match.start(), issue_date_match.end())
            fields.append(ExtractedFieldData(
                field_name="issue_date",
                extracted_value=raw_date,
                normalized_value=norm_date,
                page_number=page_no,
                confidence=0.91,
                snippet=snippet
            ))

        # 5. Expiry Date / Valid Till
        exp_date_match = re.search(r"(?:Valid\s+(?:up\s+to|till|through)|Expiry\s+Date|Valid\s+for\s+Academic\s+Year|Validity)[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4}|[0-9]{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+[0-9]{4}|[0-9]{4}-[0-9]{2}-[0-9]{2}|202[0-9]-[0-9]{2})", full_text, re.IGNORECASE)
        if exp_date_match:
            raw_exp = exp_date_match.group(1).strip()
            norm_exp = self.normalize_date(raw_exp) or raw_exp
            page_no = self._find_page(page_texts, raw_exp)
            snippet = self._get_snippet(full_text, exp_date_match.start(), exp_date_match.end())
            fields.append(ExtractedFieldData(
                field_name="expiry_date",
                extracted_value=raw_exp,
                normalized_value=norm_exp,
                page_number=page_no,
                confidence=0.89,
                snippet=snippet
            ))

        # 6. Programme & Course
        course_match = re.search(r"(?:Course|Branch|Discipline)[:\s]*([^\n\r]+(?:Computer\s+Science|Information\s+Technology|Electronics|Mechanical|Civil|Electrical|Management|Pharmacy|Engineering|MCA)[^\n\r]*)", full_text, re.IGNORECASE)
        if course_match:
            raw_course = course_match.group(1).strip()
            norm_course = re.sub(r"\s+", " ", raw_course).strip()
            page_no = self._find_page(page_texts, raw_course)
            snippet = self._get_snippet(full_text, course_match.start(), course_match.end())
            fields.append(ExtractedFieldData(
                field_name="course_name",
                extracted_value=raw_course,
                normalized_value=norm_course,
                page_number=page_no,
                confidence=0.90,
                snippet=snippet
            ))

        # 7. Approved / Requested Intake
        intake_match = re.search(r"(?:Approved\s+Intake|Approved\s+Seats|Intake|Sanctioned\s+Intake)[:\s]*(\d{2,4})\b", full_text, re.IGNORECASE)
        if intake_match:
            raw_intake = intake_match.group(1).strip()
            page_no = self._find_page(page_texts, raw_intake)
            snippet = self._get_snippet(full_text, intake_match.start(), intake_match.end())
            fields.append(ExtractedFieldData(
                field_name="approved_intake",
                extracted_value=raw_intake,
                normalized_value=raw_intake,
                page_number=page_no,
                confidence=0.95,
                snippet=snippet
            ))

        # 8. Faculty Counts (For Faculty List / Affidavit)
        fac_match = re.search(r"(?:Total\s+Faculty(?:\s+Count)?|Total\s+Teaching\s+Staff)[:\s]*(\d{1,4})\b", full_text, re.IGNORECASE)
        if fac_match:
            raw_fac = fac_match.group(1).strip()
            page_no = self._find_page(page_texts, raw_fac)
            snippet = self._get_snippet(full_text, fac_match.start(), fac_match.end())
            fields.append(ExtractedFieldData(
                field_name="total_faculty_count",
                extracted_value=raw_fac,
                normalized_value=raw_fac,
                page_number=page_no,
                confidence=0.93,
                snippet=snippet
            ))

        phd_match = re.search(r"(?:Ph\.?D\s+(?:Faculty|Holders)|Doctorate\s+Faculty)[:\s]*(\d{1,3})\b", full_text, re.IGNORECASE)
        if phd_match:
            raw_phd = phd_match.group(1).strip()
            page_no = self._find_page(page_texts, raw_phd)
            snippet = self._get_snippet(full_text, phd_match.start(), phd_match.end())
            fields.append(ExtractedFieldData(
                field_name="phd_faculty_count",
                extracted_value=raw_phd,
                normalized_value=raw_phd,
                page_number=page_no,
                confidence=0.91,
                snippet=snippet
            ))

        # 9. Land / Built-up Area (Infrastructure Evidence)
        land_match = re.search(r"(?:Land\s+Area|Total\s+Land)[:\s]*([0-9\.]+)\s*(?:Acres|Ac|Hectares)?", full_text, re.IGNORECASE)
        if land_match:
            raw_land = land_match.group(1).strip()
            page_no = self._find_page(page_texts, raw_land)
            snippet = self._get_snippet(full_text, land_match.start(), land_match.end())
            fields.append(ExtractedFieldData(
                field_name="land_area_acres",
                extracted_value=raw_land,
                normalized_value=raw_land,
                page_number=page_no,
                confidence=0.90,
                snippet=snippet
            ))

        built_match = re.search(r"(?:Built[- ]?up\s+Area|Instructional\s+Area)[:\s]*([0-9\.,]+)\s*(?:sqm|sq\.m|square\s+meters)?", full_text, re.IGNORECASE)
        if built_match:
            raw_built = built_match.group(1).replace(",", "").strip()
            page_no = self._find_page(page_texts, built_match.group(1))
            snippet = self._get_snippet(full_text, built_match.start(), built_match.end())
            fields.append(ExtractedFieldData(
                field_name="built_up_area_sqm",
                extracted_value=raw_built,
                normalized_value=raw_built,
                page_number=page_no,
                confidence=0.88,
                snippet=snippet
            ))

        # 10. Payment Reference & Status (Payment Evidence)
        pay_ref_match = re.search(r"(?:Transaction\s+(?:ID|Ref|No)|Challan\s+No|UTR\s+(?:No|Number)|Payment\s+Ref)[:\s]*([A-Z0-9\-_]{6,30})", full_text, re.IGNORECASE)
        if pay_ref_match:
            raw_pay = pay_ref_match.group(1).strip()
            page_no = self._find_page(page_texts, raw_pay)
            snippet = self._get_snippet(full_text, pay_ref_match.start(), pay_ref_match.end())
            fields.append(ExtractedFieldData(
                field_name="payment_reference",
                extracted_value=raw_pay,
                normalized_value=raw_pay.upper(),
                page_number=page_no,
                confidence=0.95,
                snippet=snippet
            ))

        pay_amt_match = re.search(r"(?:Amount\s+Paid|Total\s+Amount|Fee\s+Paid)[:\s]*(?:INR|Rs\.?)?\s*([0-9,]+(?:\.[0-9]{2})?)", full_text, re.IGNORECASE)
        if pay_amt_match:
            raw_amt = pay_amt_match.group(1).replace(",", "").strip()
            page_no = self._find_page(page_texts, pay_amt_match.group(1))
            snippet = self._get_snippet(full_text, pay_amt_match.start(), pay_amt_match.end())
            fields.append(ExtractedFieldData(
                field_name="payment_amount",
                extracted_value=raw_amt,
                normalized_value=raw_amt,
                page_number=page_no,
                confidence=0.92,
                snippet=snippet
            ))

        return fields

    def _find_page(self, page_texts: List[str], target_str: str) -> int:
        if not target_str or not page_texts:
            return 1
        for idx, p_text in enumerate(page_texts):
            if target_str in p_text:
                return idx + 1
        return 1


extraction_service = ExtractionService()
