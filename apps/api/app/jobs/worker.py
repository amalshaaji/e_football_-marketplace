import logging
import time

from app.core.config import get_settings
from app.jobs.queue import RedisJobQueue
from app.jobs.tasks import HANDLERS, JobNotConfigured

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("marketplace.jobs.worker")


def run_worker() -> None:
    queue = RedisJobQueue()
    recovered = queue.requeue_abandoned()
    if recovered:
        logger.warning("requeued jobs left in processing list count=%d", recovered)
    logger.info("background worker started")
    last_cleanup = 0.0
    while True:
        if time.monotonic() - last_cleanup >= 60:
            queue.enqueue("orders.expire_reservations", {})
            last_cleanup = time.monotonic()
        job = queue.reserve()
        if job is None:
            continue
        job_id = job.get("id", "unknown")
        name = job.get("name", "")
        try:
            handler = HANDLERS.get(name)
            if handler is None:
                raise JobNotConfigured(f"Unknown job type: {name}")
            handler(job.get("payload", {}))
            queue.acknowledge(job)
            logger.info("job completed id=%s name=%s", job_id, name)
        except Exception as exc:  # noqa: BLE001
            reserved_job = job.copy()
            job["attempts"] = int(job.get("attempts", 0)) + 1
            logger.exception("job failed id=%s name=%s attempt=%s", job_id, name, job["attempts"])
            if job["attempts"] >= get_settings().job_max_attempts or isinstance(exc, JobNotConfigured):
                queue.acknowledge(reserved_job)
                queue.dead_letter(job)
                logger.error("job moved to dead-letter queue id=%s", job_id)
            else:
                queue.acknowledge(reserved_job)
                time.sleep(min(2**job["attempts"], 60))
                queue.enqueue(name, job.get("payload", {}), attempts=job["attempts"], job_id=job_id)


if __name__ == "__main__":
    run_worker()
