"""Document translation API routes."""

import os
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Request
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import get_session
from models.document import DocumentJob, DocumentStatus
from services.extractors import detect_file_type

router = APIRouter()

# Initialize audit logger
try:
    import sys
    sys.path.insert(0, "/app")
    from shared.services.audit import AuditLogger
    audit_logger = AuditLogger("translate")
except ImportError:
    audit_logger = None


@router.post("", status_code=201)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    target_lang: str = Form(default="eng_Latn"),
    output_format: str = Form(default="json"),
    session: AsyncSession = Depends(get_session),
):
    """
    Upload a document for translation.
    
    Supports: PDF, DOCX, DOC, TXT, MD, CSV
    """
    from config import settings
    import uuid
    
    # Validate file type
    try:
        file_type = detect_file_type(file.filename or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Read file content
    content = await file.read()
    
    # Compute hash
    try:
        import xxhash
        file_hash = xxhash.xxh3_64(content).hexdigest()
    except ImportError:
        import hashlib
        file_hash = hashlib.sha256(content).hexdigest()
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "file")[1]
    upload_dir = settings.upload_dir / "documents"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{file_id}{ext}"
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create job record
    job = DocumentJob(
        filename=f"{file_id}{ext}",
        original_filename=file.filename or "document",
        file_path=str(file_path),
        file_hash=file_hash,
        file_size_bytes=len(content),
        file_type=file_type,
        target_lang=target_lang,
        output_format=output_format,
        status=DocumentStatus.PENDING,
    )
    
    session.add(job)
    await session.commit()
    await session.refresh(job)
    
    # Log audit event
    if audit_logger:
        try:
            await audit_logger.log(
                session=session,
                action="document_uploaded",
                request=request,
                job_id=job.id,
                file_hash=file_hash,
                file_name=file.filename,
                file_size_bytes=len(content),
                status="pending",
                metadata={
                    "file_type": file_type,
                    "target_lang": target_lang,
                    "output_format": output_format,
                },
            )
        except Exception:
            pass
    
    # Queue for processing
    from workers.document_worker import process_document
    process_document.delay(str(job.id))
    
    return job.to_dict()


@router.get("")
async def list_documents(
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_session),
):
    """
    List all document jobs.
    
    Shared workspace - all users see all documents.
    """
    query = select(DocumentJob).order_by(desc(DocumentJob.created_at))
    
    if status:
        query = query.where(DocumentJob.status == status)
    
    query = query.offset(offset).limit(limit)
    
    result = await session.execute(query)
    jobs = result.scalars().all()
    
    return [job.to_dict() for job in jobs]


@router.get("/{job_id}")
async def get_document(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get a specific document job."""
    result = await session.execute(
        select(DocumentJob).where(DocumentJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Document job not found")
    
    return job.to_dict()


@router.get("/{job_id}/download")
async def download_document(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Download translated document output."""
    from fastapi.responses import FileResponse
    
    result = await session.execute(
        select(DocumentJob).where(DocumentJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Document job not found")
    
    if job.status != DocumentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Job not completed. Status: {job.status.value}")
    
    if not job.output_path or not os.path.exists(job.output_path):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    media_type = "application/json" if job.output_format == "json" else "text/csv"
    filename = f"{job.original_filename}_translated.{job.output_format}"
    
    return FileResponse(
        job.output_path,
        media_type=media_type,
        filename=filename,
    )


@router.delete("/{job_id}", status_code=204)
async def delete_document(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Delete a document job and its files."""
    result = await session.execute(
        select(DocumentJob).where(DocumentJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Document job not found")
    
    # Delete files
    if job.file_path and os.path.exists(job.file_path):
        os.remove(job.file_path)
    if job.output_path and os.path.exists(job.output_path):
        os.remove(job.output_path)
    
    await session.delete(job)
    await session.commit()
