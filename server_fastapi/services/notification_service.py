import logging
from datetime import datetime, timedelta
from config.database import get_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from bson import ObjectId

from utils.mailer import send_email

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def check_deadlines(self):
        """
        Periodically checks the database for upcoming case deadlines.
        Sends email to the lawyer a day before or on the due date if not yet notified.
        """
        logger.info("[NotificationService] Running automated deadline/event scan...")
        try:
            from config.database import database
            db = database.db
            if db is None:
                return

            now = datetime.utcnow()
            
            # Find reminders that are not completed, not yet notified, 
            # and due soon (within notifyBeforeDays or just overdue)
            reminders = await db.reminders.find({
                "isCompleted": False,
                "notificationSent": False
            }).to_list(None)

            for reminder in reminders:
                # Check if it's time to notify
                due_date = reminder.get("dueDate")
                if not due_date:
                    continue
                
                if isinstance(due_date, datetime) and due_date.tzinfo is not None:
                    due_date = due_date.replace(tzinfo=None)
                
                notify_days = reminder.get("notifyBeforeDays", 1)
                notification_threshold = due_date - timedelta(days=notify_days)

                if now >= notification_threshold:
                    user_id = reminder.get("userId")
                    emails_to_notify = []
                    
                    # 1. Get the lawyer/user who created the reminder
                    try:
                        object_id = ObjectId(user_id) if isinstance(user_id, str) else user_id
                        user = await db.users.find_one({"_id": object_id, "role": {"$in": ["advocate", "admin"]}})
                        if user and user.get("email"):
                            emails_to_notify.append(user["email"])
                    except Exception:
                        pass
                        
                    # 2. Get ALL admins to ensure they are also notified
                    admins = await db.users.find({"role": "admin"}).to_list(None)
                    for admin in admins:
                        if admin.get("email") and admin["email"] not in emails_to_notify:
                            emails_to_notify.append(admin["email"])
                    
                    if emails_to_notify:
                        case_title = reminder.get("title", "Important Deadline")
                        html_content = f"""
                        <h2>Important Deadline Alert</h2>
                        <p>Matter/Reminder: <strong>{case_title}</strong></p>
                        <p>Description: {reminder.get('description', '')}</p>
                        <p>Due Date: {due_date.strftime('%Y-%m-%d %H:%M')}</p>
                        <p>Action Required! Log in to your LexiBot Dashboard to manage this.</p>
                        """
                        
                        for recipient_email in emails_to_notify:
                            try:
                                await send_email(
                                    to_email=recipient_email,
                                    subject=f"URGENT: Upcoming Deadline for {case_title}",
                                    html_content=html_content
                                )
                                logger.info(f"Notified {recipient_email} about reminder {reminder['_id']}")
                            except Exception as e:
                                logger.error(f"Could not send email to {recipient_email}: {e}")
                        
                        # Mark as sent
                        await db.reminders.update_one(
                            {"_id": reminder["_id"]},
                            {"$set": {"notificationSent": True, "notificationSentAt": now}}
                        )

        except Exception as e:
            logger.error(f"Error in NotificationService deadline scan: {e}")

    def start(self):
        """Initializes the background cron simulation"""
        if not self.scheduler.running:
            # Add job to check deadlines every minute for real-time responsiveness
            self.scheduler.add_job(
                self.check_deadlines,
                'interval',
                minutes=1,
                id='deadline_scanner',
                replace_existing=True
            )
            self.scheduler.start()
            # Run an initial scan immediately on boot
            asyncio.create_task(self.check_deadlines())
            logger.info("✅ NotificationService (APScheduler) initialized and scanning for case deadlines.")

    def stop(self):
        """Gracfully stop the cron scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("NotificationService shutdown complete.")

def get_notification_service() -> NotificationService:
    return NotificationService()
