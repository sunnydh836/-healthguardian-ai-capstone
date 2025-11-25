"""API routes for HealthGuardian AI"""

from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger


class PatientIntakeRequest(BaseModel):
    """Request model for patient intake"""
    patient_info: Dict[str, Any]


class VitalSignsRequest(BaseModel):
    """Request model for recording vital signs"""
    patient_id: str
    vital_signs: Dict[str, Any]


class HealthAdviceRequest(BaseModel):
    """Request model for health advice"""
    patient_id: str
    query: str


def setup_routes(app: FastAPI, agents: Dict[str, Any]):
    """Setup API routes"""
    
    @app.post("/api/intake")
    async def patient_intake(request: PatientIntakeRequest):
        """Process patient intake"""
        try:
            intake_agent = agents.get('intake')
            if not intake_agent:
                raise HTTPException(status_code=500, detail="Intake agent not available")
            
            result = await intake_agent.collect_patient_data(str(request.patient_info))
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error in patient intake: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/vital-signs")
    async def record_vital_signs(request: VitalSignsRequest):
        """Record patient vital signs"""
        try:
            monitor = agents.get('vital_signs_monitor')
            if not monitor:
                raise HTTPException(status_code=500, detail="Vital signs monitor not available")
            
            # In production, convert request to VitalSigns model
            return {"success": True, "message": "Vital signs recorded"}
        except Exception as e:
            logger.error(f"Error recording vital signs: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/advice")
    async def get_health_advice(request: HealthAdviceRequest):
        """Get personalized health advice"""
        try:
            advisor = agents.get('health_advisor')
            if not advisor:
                raise HTTPException(status_code=500, detail="Health advisor not available")
            
            # In production, fetch patient profile and generate advice
            return {
                "success": True,
                "advice": "Personalized health advice based on your profile"
            }
        except Exception as e:
            logger.error(f"Error getting health advice: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/patients/{patient_id}")
    async def get_patient_info(patient_id: str):
        """Get patient information"""
        try:
            # In production, query database for patient info
            return {
                "patient_id": patient_id,
                "status": "active",
                "message": "Patient information retrieved"
            }
        except Exception as e:
            logger.error(f"Error getting patient info: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/agents/status")
    async def get_agents_status():
        """Get status of all agents"""
        try:
            status = {}
            for name, agent in agents.items():
                status[name] = {
                    "healthy": agent.is_healthy(),
                    "name": agent.name
                }
            return {"agents": status}
        except Exception as e:
            logger.error(f"Error getting agents status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    logger.info("API routes configured successfully")
