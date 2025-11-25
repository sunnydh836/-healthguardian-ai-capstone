"""Vital Signs Monitor Agent - Continuous monitoring and alerts"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from loguru import logger


class VitalSigns(BaseModel):
    """Vital signs data model"""
    patient_id: str
    timestamp: datetime
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: int
    temperature: float  # Celsius
    blood_glucose: Optional[int] = None
    oxygen_saturation: Optional[int] = None


class VitalSignsMonitor:
    """Agent for monitoring vital signs and generating alerts"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'Vital Signs Monitor')
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        self.thresholds = config.get('thresholds', {})
        self._is_initialized = False
        self.patient_data: Dict[str, List[VitalSigns]] = {}
    
    async def initialize(self):
        """Initialize the monitor"""
        logger.info(f"{self.name} initializing...")
        self._is_initialized = True
        logger.success(f"{self.name} initialized successfully")
    
    async def shutdown(self):
        """Cleanup on shutdown"""
        logger.info(f"{self.name} shutting down...")
        self._is_initialized = False
    
    def is_healthy(self) -> bool:
        """Check if agent is healthy"""
        return self._is_initialized
    
    async def record_vital_signs(self, vital_signs: VitalSigns) -> Dict[str, Any]:
        """Record new vital signs and check for alerts"""
        logger.info(f"Recording vital signs for patient {vital_signs.patient_id}")
        
        # Store the data
        if vital_signs.patient_id not in self.patient_data:
            self.patient_data[vital_signs.patient_id] = []
        self.patient_data[vital_signs.patient_id].append(vital_signs)
        
        # Check for threshold violations
        alerts = await self._check_thresholds(vital_signs)
        
        if alerts:
            logger.warning(f"Alert triggered for patient {vital_signs.patient_id}: {alerts}")
        
        return {
            "recorded": True,
            "alerts": alerts,
            "timestamp": vital_signs.timestamp
        }
    
    async def _check_thresholds(self, vital_signs: VitalSigns) -> List[Dict[str, Any]]:
        """Check if vital signs exceed thresholds"""
        alerts = []
        
        # Blood pressure check
        bp_thresholds = self.thresholds.get('blood_pressure', {})
        systolic_range = bp_thresholds.get('systolic', [90, 140])
        diastolic_range = bp_thresholds.get('diastolic', [60, 90])
        
        if not (systolic_range[0] <= vital_signs.blood_pressure_systolic <= systolic_range[1]):
            alerts.append({
                "type": "blood_pressure_systolic",
                "value": vital_signs.blood_pressure_systolic,
                "threshold": systolic_range,
                "severity": "high" if vital_signs.blood_pressure_systolic > systolic_range[1] else "low"
            })
        
        # Heart rate check
        hr_range = self.thresholds.get('heart_rate', [60, 100])
        if not (hr_range[0] <= vital_signs.heart_rate <= hr_range[1]):
            alerts.append({
                "type": "heart_rate",
                "value": vital_signs.heart_rate,
                "threshold": hr_range,
                "severity": "high" if vital_signs.heart_rate > hr_range[1] else "low"
            })
        
        # Temperature check
        temp_range = self.thresholds.get('temperature', [36.1, 37.8])
        if not (temp_range[0] <= vital_signs.temperature <= temp_range[1]):
            alerts.append({
                "type": "temperature",
                "value": vital_signs.temperature,
                "threshold": temp_range,
                "severity": "high" if vital_signs.temperature > temp_range[1] else "low"
            })
        
        return alerts
    
    async def analyze_trends(self, patient_id: str, days: int = 7) -> Dict[str, Any]:
        """Analyze vital signs trends over time"""
        logger.info(f"Analyzing trends for patient {patient_id}")
        
        if patient_id not in self.patient_data or not self.patient_data[patient_id]:
            return {"error": "No data available"}
        
        # Get recent readings
        recent_readings = self.patient_data[patient_id][-days*3:]  # Assuming 3 readings per day
        
        prompt = f"""Analyze the following vital signs trends and provide insights:
        Number of readings: {len(recent_readings)}
        Latest BP: {recent_readings[-1].blood_pressure_systolic}/{recent_readings[-1].blood_pressure_diastolic}
        Latest HR: {recent_readings[-1].heart_rate}
        Latest Temp: {recent_readings[-1].temperature}
        
        Provide a summary of trends and any concerns.
        """
        
        chain = ChatPromptTemplate.from_template(prompt) | self.llm
        analysis = await chain.ainvoke({})
        
        return {
            "patient_id": patient_id,
            "period_days": days,
            "readings_analyzed": len(recent_readings),
            "analysis": analysis.content
        }
