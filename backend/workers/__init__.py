"""Workers package for Translate."""

from workers.celery_app import celery_app

__all__ = ["celery_app"]
