"""HealthGuardian AI - Main Application Entry Point"""

import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger
import yaml

from agents.intake_agent import IntakeAgent
from agents.medication_manager import MedicationManager
from agents.vital_signs_monitor import VitalSignsMonitor
from agents.health_advisor import HealthAdvisor
from database.connection import init_database
from api.routes import setup_routes

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="HealthGuardian AI",
    description="Multi-agent healthcare assistant for chronic disease management",
    version="1.0.0"
)

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize agents
agents = {
    'intake': IntakeAgent(config['agents']['intake']),
    'medication_manager': MedicationManager(config['agents']['medication_manager']),
    'vital_signs_monitor': VitalSignsMonitor(config['agents']['vital_signs_monitor']),
    'health_advisor': HealthAdvisor(config['agents']['health_advisor'])
}

@app.on_event("startup")
async def startup_event():
    """Initialize application components on startup"""
    logger.info("Starting HealthGuardian AI...")
    
    # Initialize database
    await init_database()
    
    # Start agent monitoring tasks
    for agent_name, agent in agents.items():
        if agent.config.get('enabled', True):
            logger.info(f"Initializing {agent_name}...")
            await agent.initialize()
    
    logger.success("HealthGuardian AI started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down HealthGuardian AI...")
    
    for agent_name, agent in agents.items():
        await agent.shutdown()
    
    logger.success("HealthGuardian AI shut down successfully")

# Setup API routes
setup_routes(app, agents)

@app.get("/")
async def root():
    return {
        "message": "HealthGuardian AI - Chronic Disease Management Solution",
        "status": "operational",
        "agents": [name for name, agent in agents.items() if agent.config.get('enabled', True)]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents_status": {name: agent.is_healthy() for name, agent in agents.items()}
    }

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
