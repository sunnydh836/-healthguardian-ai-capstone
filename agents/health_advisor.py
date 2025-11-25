"""Health Advisor Agent - Personalized health recommendations"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from loguru import logger


class HealthAdvisor:
    """Agent providing personalized health advice and recommendations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'Health Advisor')
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        self._is_initialized = False
        
        # System prompt for health advisory
        self.advisor_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an experienced healthcare advisor specializing in 
            chronic disease management. Provide evidence-based, personalized health 
            recommendations. Always emphasize consulting with healthcare providers 
            for medical decisions. Focus on lifestyle modifications, medication 
            adherence, and symptom management."""),
            ("human", "{input}")
        ])
    
    async def initialize(self):
        """Initialize the health advisor"""
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
    
    async def get_personalized_advice(self, patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized health advice based on patient profile"""
        logger.info(f"Generating advice for patient {patient_profile.get('patient_id', 'Unknown')}")
        
        prompt = f"""Provide personalized health advice for a patient with:
        
        Conditions: {', '.join(patient_profile.get('chronic_conditions', []))}
        Age: {patient_profile.get('age')}
        Current Medications: {', '.join(patient_profile.get('current_medications', []))}
        Recent Concern: {patient_profile.get('recent_concern', 'General wellness')}
        
        Provide advice on:
        1. Lifestyle modifications
        2. Diet recommendations
        3. Exercise guidelines
        4. Stress management
        5. Sleep hygiene
        """
        
        chain = self.advisor_prompt | self.llm
        advice = await chain.ainvoke({"input": prompt})
        
        return {
            "patient_id": patient_profile.get('patient_id'),
            "generated_at": datetime.now().isoformat(),
            "advice": advice.content,
            "follow_up_recommended": True
        }
    
    async def assess_symptom(self, symptom_description: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess a reported symptom and provide guidance"""
        logger.info("Assessing symptom...")
        
        prompt = f"""A patient with {', '.join(patient_context.get('conditions', []))} 
        reports: \"{symptom_description}\"
        
        Provide:
        1. Possible explanations related to their conditions
        2. Self-care recommendations
        3. Warning signs requiring immediate medical attention
        4. When to contact their healthcare provider
        """
        
        chain = self.advisor_prompt | self.llm
        assessment = await chain.ainvoke({"input": prompt})
        
        return {
            "symptom": symptom_description,
            "assessment": assessment.content,
            "urgency_level": "routine",  # Would be determined by LLM in production
            "timestamp": datetime.now().isoformat()
        }
    
    async def generate_wellness_plan(self, patient_id: str, goals: List[str]) -> Dict[str, Any]:
        """Generate a comprehensive wellness plan"""
        logger.info(f"Creating wellness plan for patient {patient_id}")
        
        prompt = f"""Create a 30-day wellness plan for a patient with goals:
        {chr(10).join([f'- {goal}' for goal in goals])}
        
        Include:
        - Weekly objectives
        - Daily habits to develop
        - Milestones and checkpoints
        - Success metrics
        """
        
        chain = self.advisor_prompt | self.llm
        plan = await chain.ainvoke({"input": prompt})
        
        return {
            "patient_id": patient_id,
            "goals": goals,
            "plan": plan.content,
            "duration_days": 30,
            "created_at": datetime.now().isoformat()
        }
    
    async def provide_education(self, topic: str, patient_level: str = "basic") -> Dict[str, Any]:
        """Provide patient education on health topics"""
        logger.info(f"Providing education on: {topic}")
        
        prompt = f"""Provide patient education on: {topic}
        
        Level: {patient_level}
        
        Include:
        - Clear explanation in simple terms
        - Why it matters for their health
        - Practical tips
        - Common misconceptions
        - Resources for learning more
        """
        
        chain = self.advisor_prompt | self.llm
        education = await chain.ainvoke({"input": prompt})
        
        return {
            "topic": topic,
            "level": patient_level,
            "content": education.content,
            "generated_at": datetime.now().isoformat()
        }
