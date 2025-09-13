import asyncio
import hashlib
import json
from typing import Dict, Any, Callable, List, Optional
from pydantic import BaseModel
from datetime import datetime
from .import_validation import ImportSummary, RowError

class ImportJobStatus(BaseModel):
    id: str
    filename_list: List[str]
    state: str  # queued|running|completed|failed|canceled
    progress: float = 0.0
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    summary: Optional[ImportSummary] = None
    error: Optional[str] = None

class ImportQueue:
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.jobs: Dict[str, ImportJobStatus] = {}
        self._stop = False
        self._worker_task: Optional[asyncio.Task] = None

    async def start(self, worker_handler: Callable[[str, List[str], Dict[str, Any]], ImportSummary]):
        async def worker():
            while not self._stop:
                try:
                    job_id, files, ctx = await self.queue.get()
                    status = self.jobs[job_id]
                    status.state = "running"
                    status.started_at = datetime.utcnow()
                    try:
                        summary = await worker_handler(job_id, files, ctx)
                        status.summary = summary
                        status.progress = 1.0
                        status.state = "completed"
                    except Exception as e:
                        status.state = "failed"
                        status.error = str(e)
                    finally:
                        status.finished_at = datetime.utcnow()
                        self.queue.task_done()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"Worker error: {e}")
        self._worker_task = asyncio.create_task(worker())

    async def enqueue(self, job_id: str, files: List[str], ctx: Dict[str, Any]):
        self.jobs[job_id] = ImportJobStatus(id=job_id, filename_list=files, state="queued")
        await self.queue.put((job_id, files, ctx))

    def get(self, job_id: str) -> Optional[ImportJobStatus]:
        return self.jobs.get(job_id)

    def list(self) -> List[ImportJobStatus]:
        return list(self.jobs.values())

import_queue = ImportQueue()
