import os
import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.application import Application
from app.models.document import Document, DocumentType, OCRStatus
from app.models.extracted_field import ExtractedField
from app.models.checklist import ApplicationChecklistItem
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.auth_service import get_current_user, verify_application_access, verify_document_access
from app.services.storage_service import storage_service
from app.services.ocr_service import ocr_service
from app.services.classifier_service import classifier_service
from app.services.extraction_service import extraction_service
from app.services.validation_engine import validation_engine
from app.services.compliance_engine import compliance_engine
from app.services.audit_service import record_audit_event

router = APIRouter(tags=["Documents"])


def _doc_to_response(doc: Document) -> DocumentResponse:
    preview = None
    if doc.extracted_text:
        preview = doc.extracted_text[:250].replace("\n", " ").strip()
        if len(doc.extracted_text) > 250:
            preview += "..."

    return DocumentResponse(
        id=doc.id,
        application_id=doc.application_id,
        original_filename=doc.original_filename,
        stored_filename=doc.stored_filename,
        file_size_bytes=doc.file_size_bytes,
        mime_type=doc.mime_type,
        sha256_hash=doc.sha256_hash,
        doc_type=doc.doc_type,
        classification_confidence=doc.classification_confidence,
        classification_method=doc.classification_method,
        ocr_status=doc.ocr_status,
        ocr_engine_used=doc.ocr_engine_used,
        page_count=doc.page_count,
        uploaded_at=doc.uploaded_at,
        extracted_text_preview=preview
    )


@router.post("/applications/{application_id}/documents", response_model=DocumentUploadResponse)
async def upload_documents(
    application_id: str,
    files: List[UploadFile] = File(...),
    doc_types: Optional[List[str]] = Form(None),
    doc_type: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)

    uploaded_docs: List[DocumentResponse] = []

    for idx, file in enumerate(files):
        # 1. Save File Securely & Compute SHA-256
        stored_filename, file_path, file_size, sha256_hash = await storage_service.save_file(file)

        doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
        mime_type = file.content_type or "application/octet-stream"

        # 2. Text Extraction & OCR
        extraction_res = ocr_service.extract_from_file(file_path, mime_type)

        # 3. Document Classification (with optional manual override)
        override_candidate = None
        if doc_types and idx < len(doc_types) and doc_types[idx]:
            override_candidate = doc_types[idx].strip().upper()
        elif doc_type:
            override_candidate = doc_type.strip().upper()

        if override_candidate and hasattr(DocumentType, override_candidate):
            classified_type = DocumentType(override_candidate)
            confidence = 1.0
            method = "MANUAL_USER_ASSIGNED"
        else:
            classified_type, confidence, method = classifier_service.classify(
                text=extraction_res.full_text,
                filename=file.filename
            )

        doc = Document(
            id=doc_id,
            application_id=app.id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            file_size_bytes=file_size,
            mime_type=mime_type,
            sha256_hash=sha256_hash,
            doc_type=classified_type,
            classification_confidence=confidence,
            classification_method=method,
            ocr_status=OCRStatus.COMPLETED if extraction_res.full_text else OCRStatus.FAILED,
            ocr_engine_used=extraction_res.engine_used,
            extracted_text=extraction_res.full_text,
            page_count=extraction_res.page_count,
            pdf_metadata_json=json.dumps(extraction_res.metadata)
        )
        db.add(doc)
        db.commit()

        # 4. Structured Field Extraction
        extracted_fields_data = extraction_service.extract_fields(
            full_text=extraction_res.full_text,
            page_texts=extraction_res.page_texts,
            doc_type=classified_type
        )

        for ef in extracted_fields_data:
            field_rec = ExtractedField(
                document_id=doc.id,
                application_id=app.id,
                field_name=ef.field_name,
                extracted_value=ef.extracted_value,
                normalized_value=ef.normalized_value,
                page_number=ef.page_number,
                confidence=ef.confidence,
                extraction_method=ef.extraction_method,
                snippet=ef.snippet
            )
            db.add(field_rec)

        # 5. Link Document to Checklist Items
        chk_item = db.query(ApplicationChecklistItem).filter(
            ApplicationChecklistItem.application_id == app.id,
            ApplicationChecklistItem.document_type == classified_type.value
        ).first()

        if chk_item:
            chk_item.is_submitted = True
            chk_item.document_id = doc.id
            chk_item.validation_status = "SATISFIED"
            chk_item.explanation = f"Submitted as '{file.filename}' (classified as {classified_type.value})"
            chk_item.evidence_summary = f"Pages: {doc.page_count}, Hash: {sha256_hash[:10]}..."

        db.commit()

        # Record Audit Event
        record_audit_event(
            db=db,
            actor_id=current_user.username,
            actor_role=current_user.role.value,
            action="DOCUMENT_UPLOADED",
            entity_type="DOCUMENT",
            entity_id=doc.id,
            application_id=app.id,
            after_state=f"Uploaded '{file.filename}', Classified as {classified_type.value} ({confidence*100:.0f}%)",
            details=f"Extracted {len(extracted_fields_data)} structured fields; SHA-256: {sha256_hash}"
        )

        uploaded_docs.append(_doc_to_response(doc))

    # 6. Re-run Validation Engine and Compliance Engine across application
    validation_engine.run_validation(db, app.id)
    compliance_engine.evaluate_compliance(db, app.id)

    return DocumentUploadResponse(
        message=f"Successfully processed {len(uploaded_docs)} document(s).",
        documents=uploaded_docs
    )


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = verify_document_access(document_id, db, current_user)
    app = db.query(Application).filter(Application.id == doc.application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Associated application not found")

    if current_user.role == UserRole.INSTITUTION and app.status.value != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete documents from a submitted application. Please request application reopening."
        )

    # 1. Unlink any ApplicationChecklistItem referencing this document
    chk_items = db.query(ApplicationChecklistItem).filter(
        ApplicationChecklistItem.application_id == app.id,
        ApplicationChecklistItem.document_id == doc.id
    ).all()
    for chk in chk_items:
        chk.document_id = None
        chk.is_submitted = False
        chk.validation_status = "MISSING"
        chk.explanation = f"Document '{doc.original_filename}' was removed"
        chk.evidence_summary = None

    # 2. Delete physical file from storage
    storage_service.delete_file(doc.stored_filename)

    # 3. Record audit event
    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="DOCUMENT_DELETED",
        entity_type="DOCUMENT",
        entity_id=doc.id,
        application_id=app.id,
        before_state=f"Filename: '{doc.original_filename}', Type: {doc.doc_type.value}",
        details=f"Document deleted by {current_user.username}"
    )

    # 4. Remove database record
    db.delete(doc)
    db.commit()

    # 5. Re-run validation and compliance
    validation_engine.run_validation(db, app.id)
    compliance_engine.evaluate_compliance(db, app.id)

    return {"message": f"Document '{doc.original_filename}' deleted successfully.", "deleted_id": document_id}


@router.patch("/documents/{document_id}/type", response_model=DocumentResponse)
def update_document_type(
    document_id: str,
    doc_type: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = verify_document_access(document_id, db, current_user)
    app = db.query(Application).filter(Application.id == doc.application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Associated application not found")

    if current_user.role == UserRole.INSTITUTION and app.status.value != "DRAFT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reclassify documents on a submitted application."
        )

    clean_type = doc_type.strip().upper()
    try:
        new_doc_type = DocumentType(clean_type)
    except ValueError:
        valid_types = [t.value for t in DocumentType]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document type '{doc_type}'. Allowed: {valid_types}"
        )

    old_type = doc.doc_type.value
    doc.doc_type = new_doc_type
    doc.classification_method = "MANUAL_USER_OVERRIDE"
    doc.classification_confidence = 1.0

    # Unlink old checklist item if it pointed to this doc
    old_chk = db.query(ApplicationChecklistItem).filter(
        ApplicationChecklistItem.application_id == app.id,
        ApplicationChecklistItem.document_id == doc.id
    ).first()
    if old_chk and old_chk.document_type != new_doc_type.value:
        old_chk.document_id = None
        old_chk.is_submitted = False
        old_chk.validation_status = "MISSING"
        old_chk.explanation = "Document reclassified to another requirement"
        old_chk.evidence_summary = None

    # Link new checklist item if exists
    new_chk = db.query(ApplicationChecklistItem).filter(
        ApplicationChecklistItem.application_id == app.id,
        ApplicationChecklistItem.document_type == new_doc_type.value
    ).first()
    if new_chk:
        new_chk.is_submitted = True
        new_chk.document_id = doc.id
        new_chk.validation_status = "SATISFIED"
        new_chk.explanation = f"Submitted as '{doc.original_filename}' (manually classified as {new_doc_type.value})"
        new_chk.evidence_summary = f"Pages: {doc.page_count}, Hash: {doc.sha256_hash[:10]}..."

    db.commit()

    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role.value,
        action="DOCUMENT_RECLASSIFIED",
        entity_type="DOCUMENT",
        entity_id=doc.id,
        application_id=app.id,
        before_state=old_type,
        after_state=new_doc_type.value,
        details=f"User updated document type from {old_type} to {new_doc_type.value}"
    )

    validation_engine.run_validation(db, app.id)
    compliance_engine.evaluate_compliance(db, app.id)
    db.refresh(doc)
    return _doc_to_response(doc)


@router.get("/applications/{application_id}/documents", response_model=List[DocumentResponse])
def get_application_documents(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = verify_application_access(application_id, db, current_user)
    docs = db.query(Document).filter(Document.application_id == app.id).all()
    return [_doc_to_response(d) for d in docs]


@router.get("/documents/{document_id}/view")
def view_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doc = verify_document_access(document_id, db, current_user)

    safe_path = storage_service.get_file_path(doc.stored_filename)
    return FileResponse(
        path=safe_path,
        media_type=doc.mime_type,
        filename=doc.original_filename,
        content_disposition_type="inline"
    )
