"""Intake Agent - Initial patient data collection and triage"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from loguru import logger


class PatientIntake(BaseModel):
    """Patient intake data model"""
    patient_id: str
    name: str
    age: int
    gender: str
    chronic_conditions: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    emergency_contact: Dict[str, str]
    primary_concern: str
    intake_date: datetime = Field(default_factory=datetime.now)


class IntakeAgent:
    """Agent responsible for patient intake and initial assessment"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'Intake Agent')
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7
        )
        self.intake_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a compassionate healthcare intake specialist.
            Your role is to collect comprehensive patient information while making 
            them feel comfortable and understood. Ask clear, empathetic questions 
            and validate their concerns."""),
            ("human", "{input}")
        ])
        self._is_initialized = False
    
    async def initialize(self):
        """Initialize the agent"""
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
    
    async def collect_patient_data(self, initial_input: str) -> PatientIntake:
        """Collect initial patient data through conversation"""
        logger.info(f"Starting patient intake...")
        
        # Simulate conversational data collection
        chain = self.intake_prompt | self.llm
        response = await chain.ainvoke({"input": initial_input})
        
        # Extract structured data from conversation
        # In production, this would involve multiple conversation turns
        patient_data = self._extract_patient_data(response.content)
        
        logger.success(f"Patient intake completed for {patient_data.get('name', 'Unknown')}")
        return patient_data
    
    def _extract_patient_data(self, conversation: str) -> Dict[str, Any]:
        """Extract structured data from conversation"""
        # Placeholder implementation
        # In production, use LLM with structured output or form validation
        return {
            "patient_id": f"PT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": "Sample Patient",
            "age": 45,
            "gender": "Female",
            "chronic_conditions": ["Type 2 Diabetes", "Hypertension"],
            "current_medications": ["Metformin 500mg", "Lisinopril 10mg"],
            "allergies": ["Penicillin"],
            "emergency_contact": {"name": "John Doe", "phone": "555-0123"},
            "primary_concern": "Blood sugar management"
        }
    
    async def perform_triage(self, patient_data: PatientIntake) -> Dict[str, Any]:
        """Perform initial triage assessment"""
        logger.info(f"Performing triage for patient {patient_data.patient_id}")
        
        triage_prompt = f"""Based on the following patient information, 
        provide a triage assessment and recommend priority level:
        
        Conditions: {', '.join(patient_data.chronic_conditions)}
        Current Concern: {patient_data.primary_concern}
        """
        
        chain = self.intake_prompt | self.llm
        response = await chain.ainvoke({"input": triage_prompt})
        
        return {
            "priority": "medium",  # Would be extracted from LLM response
            "recommended_agents": ["medication_manager", "vital_signs_monitor"],
            "notes": response.content
        }
