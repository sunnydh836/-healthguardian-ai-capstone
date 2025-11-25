"""Medication Manager Agent - Track medications and send reminders"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger


class Medication(BaseModel):
    """Medication data model"""
    name: str
    dosage: str
    frequency: str  # e.g., "twice daily", "every 8 hours"
    times: List[str]  # e.g., ["08:00", "20:00"]
    instructions: str
    refill_date: datetime


class MedicationManager:
    """Agent for managing medications and reminders"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'Medication Manager')
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        self.scheduler = AsyncIOScheduler()
        self._is_initialized = False
        self.active_medications: Dict[str, Medication] = {}
    
    async def initialize(self):
        """Initialize the medication manager"""
        logger.info(f"{self.name} initializing...")
        self.scheduler.start()
        self._is_initialized = True
        logger.success(f"{self.name} initialized successfully")
    
    async def shutdown(self):
        """Cleanup on shutdown"""
        logger.info(f"{self.name} shutting down...")
        self.scheduler.shutdown()
        self._is_initialized = False
    
    def is_healthy(self) -> bool:
        """Check if agent is healthy"""
        return self._is_initialized and self.scheduler.running
    
    async def add_medication(self, patient_id: str, medication: Medication):
        """Add a new medication to tracking"""
        logger.info(f"Adding medication {medication.name} for patient {patient_id}")
        
        med_id = f"{patient_id}_{medication.name}"
        self.active_medications[med_id] = medication
        
        # Schedule reminders
        for time in medication.times:
            hour, minute = map(int, time.split(':'))
            self.scheduler.add_job(
                self._send_reminder,
                'cron',
                hour=hour,
                minute=minute,
                args=[patient_id, medication]
            )
        
        logger.success(f"Medication {medication.name} added with reminders")
    
    async def _send_reminder(self, patient_id: str, medication: Medication):
        """Send medication reminder to patient"""
        logger.info(f"Sending reminder for {medication.name} to patient {patient_id}")
        
        prompt = f"""Generate a friendly medication reminder for:
        Medication: {medication.name}
        Dosage: {medication.dosage}
        Instructions: {medication.instructions}
        """
        
        chain = ChatPromptTemplate.from_template(prompt) | self.llm
        reminder = await chain.ainvoke({})
        
        # In production, send via SMS/email/push notification
        logger.info(f"Reminder sent: {reminder.content[:100]}...")
        return reminder.content
    
    async def check_adherence(self, patient_id: str) -> Dict[str, Any]:
        """Check medication adherence for a patient"""
        logger.info(f"Checking medication adherence for patient {patient_id}")
        
        # In production, query database for actual adherence data
        adherence_data = {
            "patient_id": patient_id,
            "adherence_rate": 0.85,  # 85%
            "missed_doses": 3,
            "streak_days": 12
        }
        
        return adherence_data
    
    async def check_refills(self, patient_id: str) -> List[Dict[str, Any]]:
        """Check which medications need refilling"""
        logger.info(f"Checking refills for patient {patient_id}")
        
        refills_needed = []
        for med_id, med in self.active_medications.items():
            if patient_id in med_id:
                days_until_refill = (med.refill_date - datetime.now()).days
                if days_until_refill <= 7:
                    refills_needed.append({
                        "medication": med.name,
                        "days_remaining": days_until_refill
                    })
        
        return refills_needed
