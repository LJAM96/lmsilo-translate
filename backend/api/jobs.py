"""Job management API routes for Translate."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import get_session
from models.job import TranslationJob
from schemas.job import JobStatus, TranslationJobCreate, TranslationJobResponse

router = APIRouter()

# Initialize audit logger
try:
    import sys
    sys.path.insert(0, "/app")
    from shared.services.audit import AuditLogger
    audit_logger = AuditLogger("translate")
except ImportError:
    audit_logger = None


@router.post("", status_code=201, response_model=TranslationJobResponse)
async def create_job(
    request_data: TranslationJobCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new translation job.
    
    Queues text for async translation.
    """
    from models.database import Model
    
    # Get default model if not specified
    model_id = request_data.model_id
    model_name = None
    
    if not model_id:
        result = await session.execute(
            select(Model).where(Model.is_default == True).limit(1)
        )
        default_model = result.scalar_one_or_none()
        if default_model:
            model_id = default_model.id
            model_name = default_model.name
    
    # Create job record
    job = TranslationJob(
        text=request_data.text,
        source_lang=request_data.source_lang,
        target_lang=request_data.target_lang,
        model_id=model_id,
        model_name=model_name,
        status=JobStatus.PENDING,
    )
    
    session.add(job)
    await session.commit()
    await session.refresh(job)
    
    # Log audit event
    if audit_logger:
        try:
            await audit_logger.log(
                session=session,
                action="job_created",
                request=request,
                job_id=job.id,
                model_used=model_name,
                status="pending",
                metadata={
                    "source_lang": request_data.source_lang,
                    "target_lang": request_data.target_lang,
                    "text_length": len(request_data.text),
                },
            )
        except Exception:
            pass  # Don't fail job creation if audit fails
    
    # Queue for processing
    from workers.tasks import translate_text_task
    translate_text_task.delay(str(job.id))
    
    return TranslationJobResponse(
        id=job.id,
        status=JobStatus(job.status),
        text=job.text,
        source_lang=job.source_lang,
        target_lang=job.target_lang,
        translation=job.translation,
        error=job.error,
        model_used=job.model_name,
        processing_time_ms=job.processing_time_ms,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


@router.get("", response_model=List[dict])
async def list_jobs(
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0),
    session: AsyncSession = Depends(get_session),
):
    """
    List all translation jobs.
    
    Shared workspace - all users see all jobs.
    """
    query = select(TranslationJob).order_by(desc(TranslationJob.created_at))
    
    if status:
        query = query.where(TranslationJob.status == status)
    
    query = query.offset(offset).limit(limit)
    
    result = await session.execute(query)
    jobs = result.scalars().all()
    
    return [job.to_dict() for job in jobs]


@router.get("/{job_id}", response_model=dict)
async def get_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get a specific translation job."""
    result = await session.execute(
        select(TranslationJob).where(TranslationJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Return full text for single job view
    return {
        **job.to_dict(),
        "text": job.text,  # Full text
        "translation": job.translation,  # Full translation
    }


@router.delete("/{job_id}", status_code=204)
async def delete_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Delete a translation job."""
    result = await session.execute(
        select(TranslationJob).where(TranslationJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    await session.delete(job)
    await session.commit()
