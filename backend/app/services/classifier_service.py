import re
from abc import ABC, abstractmethod
from typing import Tuple
from app.models.document import DocumentType


class DocumentClassifierBase(ABC):
    @abstractmethod
    def classify(self, text: str, filename: str) -> Tuple[DocumentType, float, str]:
        """Classifies extracted document text, returning (DocumentType, confidence, method_name)"""
        pass


class KeywordHeuristicClassifier(DocumentClassifierBase):
    """
    Lightweight, deterministic regulatory document classifier.
    Designed with a clean interface so an ML/NLP model (e.g. LayoutLM or DistilBERT)
    can drop in as an alternative implementation.
    """
    
    CLASSIFICATION_RULES = {
        DocumentType.PREVIOUS_APPROVAL: {
            "primary": [
                r"approval process handbook",
                r"extension of approval",
                r"all india council for technical education",
                r"aicte approval",
                r"eoa report",
                r"grant of approval",
                r"letter of approval"
            ],
            "secondary": [r"intake", r"programme", r"affiliating", r"aicte"],
            "filename_patterns": [r"eoa", r"approval", r"aicte_letter"]
        },
        DocumentType.AFFIDAVIT: {
            "primary": [
                r"affidavit",
                r"solemnly affirm",
                r"undertaking",
                r"deponent",
                r"non-judicial stamp",
                r"format[- ]?[0-9]+"
            ],
            "secondary": [r"notary", r"sworn before", r"verified at", r"attestation"],
            "filename_patterns": [r"affidavit", r"undertaking", r"format"]
        },
        DocumentType.FACULTY_LIST: {
            "primary": [
                r"faculty details",
                r"cadre ratio",
                r"teaching faculty",
                r"assistant professor",
                r"associate professor",
                r"list of faculty members",
                r"faculty student ratio"
            ],
            "secondary": [r"ph\.?d", r"qualification", r"date of joining", r"specialization"],
            "filename_patterns": [r"faculty", r"staff", r"cadre", r"teacher"]
        },
        DocumentType.NOC: {
            "primary": [
                r"no objection certificate",
                r"noc",
                r"state government permission",
                r"directorate of technical education",
                r"affiliating university noc"
            ],
            "secondary": [r"government of", r"department of higher education", r"objection"],
            "filename_patterns": [r"noc", r"permission", r"state_approval"]
        },
        DocumentType.ACCREDITATION_CERT: {
            "primary": [
                r"national board of accreditation",
                r"nba",
                r"naac",
                r"certificate of accreditation",
                r"accredited",
                r"tier-[iI]+",
                r"grade a\+?"
            ],
            "secondary": [r"valid up to", r"academic years", r"assessment cycle"],
            "filename_patterns": [r"nba", r"naac", r"accredit"]
        },
        DocumentType.INFRASTRUCTURE_EVIDENCE: {
            "primary": [
                r"land area",
                r"built[- ]?up area",
                r"infrastructure details",
                r"sqm",
                r"square meters",
                r"instructional area",
                r"barrier free campus",
                r"occupancy certificate"
            ],
            "secondary": [r"survey number", r"building plan", r"architect certificate", r"khasra"],
            "filename_patterns": [r"infra", r"land", r"building", r"area"]
        },
        DocumentType.PAYMENT_RECEIPT: {
            "primary": [
                r"ter charges",
                r"processing fee",
                r"transaction receipt",
                r"payment details",
                r"utr number",
                r"aicte portal payment",
                r"challan"
            ],
            "secondary": [r"amount paid", r"transaction id", r"payment gateway", r"successful"],
            "filename_patterns": [r"payment", r"receipt", r"fee", r"challan", r"ter"]
        }
    }

    def classify(self, text: str, filename: str) -> Tuple[DocumentType, float, str]:
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        best_type = DocumentType.OTHER
        max_score = 0.0

        for doc_type, criteria in self.CLASSIFICATION_RULES.items():
            score = 0.0
            
            # Match primary phrases (worth 3 points each)
            for pattern in criteria["primary"]:
                if re.search(pattern, text_lower):
                    score += 3.0

            # Match secondary keywords (worth 1 point each)
            for pattern in criteria["secondary"]:
                if re.search(pattern, text_lower):
                    score += 1.0

            # Match filename keywords (worth 2 points)
            for pattern in criteria["filename_patterns"]:
                if re.search(pattern, filename_lower):
                    score += 2.0

            if score > max_score:
                max_score = score
                best_type = doc_type

        # Compute confidence based on relative score
        if max_score >= 6.0:
            confidence = min(0.98, 0.75 + (max_score * 0.03))
        elif max_score >= 3.0:
            confidence = 0.70
        elif max_score > 0.0:
            confidence = 0.50
        else:
            confidence = 0.20
            best_type = DocumentType.OTHER

        return best_type, round(confidence, 2), "KEYWORD_HEURISTIC_V1"


classifier_service = KeywordHeuristicClassifier()
