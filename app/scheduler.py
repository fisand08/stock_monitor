# scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from .models import scheduler_function

def setup_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduler_function, trigger='interval', seconds=60)
    scheduler.start()
