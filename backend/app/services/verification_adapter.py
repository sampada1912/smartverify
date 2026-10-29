from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.verification import MockAuthorityRecord, VerificationStatus, VerificationResult


class VerificationOutcome:
    def __init__(
        self,
        status: VerificationStatus,
        authority_name: str,
        certificate_number: str,
        is_simulated: bool = True,
        mismatch_details: Optional[str] = None,
        raw_response: Optional[Dict[str, Any]] = None
    ):
        self.status = status
        self.authority_name = authority_name
        self.certificate_number = certificate_number
        self.is_simulated = is_simulated
        self.mismatch_details = mismatch_details
        self.raw_response = raw_response or {}


class VerificationAdapterBase(ABC):
    @abstractmethod
    def verify(
        self,
        db: Session,
        authority_name: str,
        certificate_number: str,
        submitted_data: Dict[str, Any]
    ) -> VerificationOutcome:
        """Executes verification against external or mock issuing authority."""
        pass


class MockAuthorityVerificationAdapter(VerificationAdapterBase):
    """
    Simulated verification adapter using deterministic synthetic test records.
    Explicitly labeled as SIMULATED to distinguish from authorized external systems.
    """

    def verify(
        self,
        db: Session,
        authority_name: str,
        certificate_number: str,
        submitted_data: Dict[str, Any]
    ) -> VerificationOutcome:
        clean_cert = certificate_number.strip().upper()

        # Handle explicit simulated failure prefixes for demonstration
        if clean_cert.startswith("UNAVAIL") or "DOWN" in clean_cert:
            return VerificationOutcome(
                status=VerificationStatus.SOURCE_UNAVAILABLE,
                authority_name=authority_name,
                certificate_number=clean_cert,
                is_simulated=True,
                mismatch_details="Simulated issuing authority registry connection timeout (HTTP 503 Gateway Timeout).",
                raw_response={"error": "SOURCE_SERVICE_UNAVAILABLE", "retry_after_sec": 300}
            )

        # Lookup in simulated registry
        mock_rec = db.query(MockAuthorityRecord).filter(
            MockAuthorityRecord.certificate_number == clean_cert
        ).first()

        if not mock_rec:
            # Check case-insensitive fallback
            mock_rec = db.query(MockAuthorityRecord).filter(
                MockAuthorityRecord.certificate_number.ilike(clean_cert)
            ).first()

        if not mock_rec:
            return VerificationOutcome(
                status=VerificationStatus.MISMATCH_DETECTED,
                authority_name=authority_name,
                certificate_number=clean_cert,
                is_simulated=True,
                mismatch_details=f"Certificate number '{clean_cert}' not found in {authority_name} database.",
                raw_response={"status": "RECORD_NOT_FOUND", "query_certificate": clean_cert}
            )

        # 1. Check if expired
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        if mock_rec.status == "EXPIRED" or (mock_rec.expiry_date and mock_rec.expiry_date < today_str):
            return VerificationOutcome(
                status=VerificationStatus.EXPIRED,
                authority_name=mock_rec.authority_name,
                certificate_number=mock_rec.certificate_number,
                is_simulated=True,
                mismatch_details=f"Certificate expired on {mock_rec.expiry_date}. Status in authority register is EXPIRED.",
                raw_response={
                    "status": "EXPIRED",
                    "issued_on": mock_rec.issue_date,
                    "expired_on": mock_rec.expiry_date
                }
            )

        # 2. Check for manual review flag in mock record
        if mock_rec.status == "SUSPENDED" or mock_rec.status == "MANUAL_REVIEW":
            return VerificationOutcome(
                status=VerificationStatus.MANUAL_REVIEW_REQUIRED,
                authority_name=mock_rec.authority_name,
                certificate_number=mock_rec.certificate_number,
                is_simulated=True,
                mismatch_details="Issuing authority has placed this record under administrative hold / investigation.",
                raw_response={"status": mock_rec.status, "reason": "Administrative inquiry pending"}
            )

        # 3. Check submitted field consistency against mock record
        mismatches = []
        sub_inst_id = submitted_data.get("institution_id")
        if sub_inst_id and mock_rec.institution_id:
            if sub_inst_id.strip() != mock_rec.institution_id.strip():
                mismatches.append(f"Institution ID mismatch: Submitted '{sub_inst_id}' vs Authority Record '{mock_rec.institution_id}'")

        sub_inst_name = submitted_data.get("institution_name")
        if sub_inst_name and mock_rec.institution_name:
            if sub_inst_name.strip().lower() not in mock_rec.institution_name.strip().lower() and \
               mock_rec.institution_name.strip().lower() not in sub_inst_name.strip().lower():
                mismatches.append(f"Institution Name mismatch: Submitted '{sub_inst_name}' vs Authority Record '{mock_rec.institution_name}'")

        if mismatches:
            return VerificationOutcome(
                status=VerificationStatus.MISMATCH_DETECTED,
                authority_name=mock_rec.authority_name,
                certificate_number=mock_rec.certificate_number,
                is_simulated=True,
                mismatch_details="; ".join(mismatches),
                raw_response={
                    "status": "MISMATCH",
                    "authority_institution_id": mock_rec.institution_id,
                    "authority_institution_name": mock_rec.institution_name,
                    "discrepancies": mismatches
                }
            )

        # Clean verification
        return VerificationOutcome(
            status=VerificationStatus.VERIFIED,
            authority_name=mock_rec.authority_name,
            certificate_number=mock_rec.certificate_number,
            is_simulated=True,
            mismatch_details=None,
            raw_response={
                "status": "VERIFIED_ACTIVE",
                "issued_to_id": mock_rec.institution_id,
                "issued_to_name": mock_rec.institution_name,
                "document_type": mock_rec.doc_type,
                "valid_till": mock_rec.expiry_date
            }
        )


verification_adapter = MockAuthorityVerificationAdapter()
