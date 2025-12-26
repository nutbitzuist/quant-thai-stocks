"""
Scheduler Service
Manages background job execution for scheduled scans.
Uses APScheduler with AsyncIOScheduler.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, update
from datetime import datetime
import logging
import asyncio

from app.database import get_db, engine, async_session_maker
from app.database.models import ScheduledScan, RunHistory, User
from app.api.routes.models import ALL_MODELS, run_model
from app.data.fetcher import get_fetcher
from app.data.universe import get_tickers
from app.services.custom_universe import get_custom_universe_manager
from app.services.history import get_history_service

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()

async def run_scan_job(scan_id: str):
    """
    Execute a single scheduled scan.
    This function is called by the scheduler.
    """
    logger.info(f"🚀 Starting scheduled scan job: {scan_id}")
    
    async with async_session_maker() as db:
        try:
            # 1. Fetch scan details
            query = select(ScheduledScan).where(ScheduledScan.id == scan_id)
            result = await db.execute(query)
            scan = result.scalar_one_or_none()
            
            if not scan:
                logger.error(f"Scan {scan_id} not found, skipping execution")
                return
            
            if not scan.enabled or scan.deleted_at:
                logger.info(f"Scan {scan_id} is disabled or deleted, skipping")
                return

            logger.info(f"Running model {scan.model_id} for user {scan.user_id} on {scan.universe}")

            # 2. Prepare for execution
            # Resolve tickers
            custom_manager = get_custom_universe_manager()
            custom_universe = await custom_manager.get_universe(db, scan.universe, scan.user_id)
            
            if custom_universe:
                tickers = custom_universe['tickers']
            else:
                tickers = get_tickers(scan.universe)
            
            if not tickers:
                logger.warning(f"No tickers found for universe {scan.universe}, skipping")
                return

            # 3. Fetch Data
            fetcher = get_fetcher()
            price_data = fetcher.get_bulk_price_data(tickers, period="1y")
            
            # 4. Run Model
            if scan.model_id not in ALL_MODELS:
                logger.error(f"Model {scan.model_id} not found")
                return
                
            model_class = ALL_MODELS[scan.model_id]
            params = scan.parameters or {}
            model = model_class(**params)
            
            model_result = model.run(price_data) # Add fundamental if needed later
            
            # 5. Save History
            history_service = get_history_service()
            record = await history_service.add_run(
                db=db,
                model_id=scan.model_id,
                model_name=model_result.model_name,
                category=model_result.category,
                universe=scan.universe,
                total_analyzed=len(tickers),
                stocks_with_data=len(price_data),
                buy_signals=[s.to_dict() for s in model_result.get_buy_signals(50)],
                sell_signals=[s.to_dict() for s in model_result.get_sell_signals(50)],
                parameters=model_result.parameters,
                errors=model_result.errors,
                user_id=scan.user_id
            )
            
            # 6. Update Last Run
            scan.last_run = datetime.now()
            await db.commit()
            
            logger.info(f"✅ Scheduled scan {scan_id} completed successfully. History ID: {record['id']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to run scheduled scan {scan_id}: {str(e)}", exc_info=True)


async def start_scheduler():
    """Start the scheduler and load existing jobs"""
    if scheduler.running:
        return

    scheduler.start()
    logger.info("⏰ Scheduler started")
    
    # Load existing jobs from DB
    await sync_jobs_from_db()


async def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("🛑 Scheduler stopped")


async def sync_jobs_from_db():
    """
    Clear all jobs and reload from database.
    Useful on startup or when massive changes happen.
    """
    scheduler.remove_all_jobs()
    logger.info("Syncing jobs from database...")
    
    async with async_session_maker() as db:
        query = select(ScheduledScan).where(
            ScheduledScan.enabled == True,
            ScheduledScan.deleted_at.is_(None)
        )
        result = await db.execute(query)
        scans = result.scalars().all()
        
        count = 0
        for scan in scans:
            add_job_for_scan(scan)
            count += 1
            
        logger.info(f"Loaded {count} scheduled jobs")


def add_job_for_scan(scan: ScheduledScan):
    """Add a single scan to the scheduler"""
    if not scan.enabled or scan.deleted_at:
        return

    # Parse schedule time (HH:MM)
    try:
        hour, minute = map(int, scan.schedule_time.split(':'))
        
        # Parse days (e.g. ['Mon', 'Tue'])
        # APScheduler expects day_of_week as 'mon,tue,wed'
        days_map = {
            'Mon': 'mon', 'Tue': 'tue', 'Wed': 'wed', 'Thu': 'thu', 'Fri': 'fri', 
            'Sat': 'sat', 'Sun': 'sun'
        }
        
        cron_days = ",".join([days_map.get(d, d.lower()) for d in scan.days])
        
        scheduler.add_job(
            run_scan_job,
            CronTrigger(hour=hour, minute=minute, day_of_week=cron_days, timezone='Asia/Bangkok'),
            args=[scan.id],
            id=str(scan.id),
            replace_existing=True
        )
        logger.debug(f"Added job for scan {scan.id} at {scan.schedule_time} on {cron_days}")
        
    except Exception as e:
        logger.error(f"Failed to add job for scan {scan.id}: {e}")


def remove_job(scan_id: str):
    """Remove a job from the scheduler"""
    if scheduler.get_job(str(scan_id)):
        scheduler.remove_job(str(scan_id))
        logger.debug(f"Removed job {scan_id}")
