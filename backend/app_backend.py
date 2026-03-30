"""
FastAPI Backend for Healthcare Dashboard
Provides API endpoints for metrics and AI chatbot analysis
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Dashboard API",
    description="API for healthcare metrics and AI analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Claude client
client = Anthropic()

# Database connection
DATABASE_PATH = "healthcare_dashboard.db"

# ==================== Pydantic Models ====================

class ChatMessage(BaseModel):
    """Chat message model"""
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    analysis: Optional[str] = None
    suggestions: Optional[List[str]] = None

class MetricsResponse(BaseModel):
    """Metrics response model"""
    metric_name: str
    value: float
    target: float
    status: str
    trend: str

class ProviderMetrics(BaseModel):
    """Provider metrics model"""
    provider_id: str
    provider_name: str
    patient_satisfaction_score: float
    quality_score: float
    patient_retention_rate: float
    no_show_rate: float

# ==================== Database Functions ====================

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query: str, params: tuple = ()):
    """Execute a database query and return results"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_query_as_dataframe(query: str, params: tuple = ()) -> pd.DataFrame:
    """Execute query and return as DataFrame"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ==================== Claude AI Functions ====================

class HealthcareAnalystChat:
    """Healthcare data analyst using Claude"""
    
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """You are an expert healthcare data analyst specializing in HEDIS metrics, 
clinical quality, provider performance, and gaps in care. You have access to a comprehensive healthcare database.

Your role is to:
1. Answer questions about healthcare metrics and performance
2. Identify trends and patterns in healthcare data
3. Provide actionable recommendations to improve quality and efficiency
4. Explain HEDIS metrics and clinical quality indicators
5. Suggest interventions based on data analysis

When analyzing data:
- Be specific with percentages and numbers
- Identify root causes of performance gaps
- Prioritize recommendations by impact
- Consider patient population demographics
- Reference benchmark standards when relevant

Format your responses clearly with:
- Key findings (what the data shows)
- Root cause analysis (why it's happening)
- Recommendations (what to do about it)
- Next steps (how to implement)
"""
    
    def format_database_context(self) -> str:
        """Get relevant metrics from database for context"""
        try:
            # Get key metrics
            metrics_query = """
            SELECT 
                'Total Patients' as metric, COUNT(*) as value
            FROM patients
            UNION ALL
            SELECT 'Active Providers', COUNT(*) FROM providers
            UNION ALL
            SELECT 'Total Encounters', COUNT(*) FROM encounters
            UNION ALL
            SELECT 'HEDIS Measures Met', COUNT(*) FROM hedis_metrics WHERE status = 'Met'
            """
            
            df_metrics = get_query_as_dataframe(metrics_query)
            context = "Current Database Snapshot:\n"
            for _, row in df_metrics.iterrows():
                context += f"- {row[0]}: {row[1]}\n"
            
            return context
        except:
            return "Database context unavailable"
    
    def analyze_metrics(self, user_message: str) -> dict:
        """Analyze healthcare metrics using Claude"""
        
        # Add database context
        db_context = self.format_database_context()
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": f"{db_context}\n\nUser Question: {user_message}"
        })
        
        try:
            # Call Claude API
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system=self.system_prompt,
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Extract suggestions if present
            suggestions = self._extract_suggestions(assistant_message)
            
            return {
                "response": assistant_message,
                "suggestions": suggestions,
                "model": response.model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Claude API error: {str(e)}")
    
    def _extract_suggestions(self, text: str) -> List[str]:
        """Extract actionable suggestions from response"""
        suggestions = []
        lines = text.split('\n')
        
        in_suggestions = False
        for line in lines:
            if 'recommendation' in line.lower() or 'suggest' in line.lower():
                in_suggestions = True
            if in_suggestions and line.strip().startswith('-'):
                suggestions.append(line.strip('- '))
            if in_suggestions and len(suggestions) >= 3:
                break
        
        return suggestions[:3] if suggestions else []

# Initialize analyzer
analyzer = HealthcareAnalystChat()

# ==================== Routes ====================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Healthcare Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "gaps_in_care": "/metrics/gaps-in-care",
            "hedis_metrics": "/metrics/hedis",
            "provider_performance": "/metrics/provider-performance",
            "clinical_quality": "/metrics/clinical-quality",
            "chat": "/chat/analyze"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ==================== Gaps in Care Endpoints ====================

@app.get("/metrics/gaps-in-care")
async def get_gaps_in_care(
    limit: int = Query(100, ge=1, le=1000),
    priority: Optional[str] = Query(None, regex="^(High|Medium|Low)$")
):
    """Get Gaps in Care metrics"""
    try:
        query = "SELECT * FROM gaps_in_care WHERE 1=1"
        params = []
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        query += " LIMIT ?"
        params.append(limit)
        
        results = execute_query(query, tuple(params))
        
        gaps = [dict(row) for row in results]
        
        return {
            "total_gaps": len(gaps),
            "gaps": gaps,
            "priority_distribution": get_priority_distribution()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/gaps-in-care/summary")
async def get_gaps_summary():
    """Get Gaps in Care summary statistics"""
    try:
        query = """
        SELECT 
            COUNT(*) as total_gaps,
            SUM(CASE WHEN is_gap = 1 THEN 1 ELSE 0 END) as open_gaps,
            SUM(CASE WHEN priority = 'High' THEN 1 ELSE 0 END) as high_priority,
            AVG(days_overdue) as avg_days_overdue
        FROM gaps_in_care
        WHERE is_gap = 1
        """
        
        result = execute_query(query)[0]
        
        return {
            "total_gaps": result[0],
            "open_gaps": result[1],
            "high_priority_gaps": result[2],
            "average_days_overdue": float(result[3]) if result[3] else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_priority_distribution():
    """Get priority distribution for gaps"""
    try:
        query = """
        SELECT priority, COUNT(*) as count
        FROM gaps_in_care
        GROUP BY priority
        """
        results = execute_query(query)
        return {row[0]: row[1] for row in results}
    except:
        return {}

# ==================== HEDIS Metrics Endpoints ====================

@app.get("/metrics/hedis")
async def get_hedis_metrics(
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = Query(None, regex="^(Met|Not Met)$")
):
    """Get HEDIS metrics"""
    try:
        query = "SELECT * FROM hedis_metrics WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " LIMIT ?"
        params.append(limit)
        
        results = execute_query(query, tuple(params))
        
        return {
            "total_measures": len(results),
            "metrics": [dict(row) for row in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/hedis/summary")
async def get_hedis_summary():
    """Get HEDIS metrics summary"""
    try:
        query = """
        SELECT 
            COUNT(*) as total_measures,
            SUM(CASE WHEN status = 'Met' THEN 1 ELSE 0 END) as measures_met,
            AVG(performance_rate) as avg_performance,
            AVG(target_rate) as avg_target
        FROM hedis_metrics
        """
        
        result = execute_query(query)[0]
        
        return {
            "total_measures": result[0],
            "measures_met": result[1],
            "compliance_rate": round((result[1] / result[0] * 100) if result[0] > 0 else 0, 2),
            "average_performance_rate": round(float(result[2]) if result[2] else 0, 2),
            "average_target_rate": round(float(result[3]) if result[3] else 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Provider Performance Endpoints ====================

@app.get("/metrics/provider-performance")
async def get_provider_performance(limit: int = Query(50, ge=1, le=500)):
    """Get provider performance metrics"""
    try:
        query = """
        SELECT 
            provider_id,
            provider_name,
            total_patients,
            patient_satisfaction_score,
            quality_score,
            patient_retention_rate,
            appointment_no_show_rate
        FROM provider_performance
        ORDER BY quality_score DESC
        LIMIT ?
        """
        
        results = execute_query(query, (limit,))
        
        return {
            "total_providers": len(results),
            "providers": [dict(row) for row in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/provider-performance/{provider_id}")
async def get_provider_detail(provider_id: str):
    """Get detailed provider performance"""
    try:
        query = "SELECT * FROM provider_performance WHERE provider_id = ?"
        results = execute_query(query, (provider_id,))
        
        if not results:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        return dict(results[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Clinical Quality Endpoints ====================

@app.get("/metrics/clinical-quality/summary")
async def get_clinical_quality_summary():
    """Get clinical quality summary"""
    try:
        query = """
        SELECT 
            COUNT(*) as total_records,
            SUM(CASE WHEN readmission_30day = 1 THEN 1 ELSE 0 END) as readmissions_30day,
            SUM(CASE WHEN hospital_acquired_infection = 1 THEN 1 ELSE 0 END) as infections,
            AVG(medication_adherence) as avg_medication_adherence,
            AVG(care_coordination_score) as avg_care_coordination,
            AVG(clinical_outcome_score) as avg_clinical_outcome
        FROM clinical_quality
        """
        
        result = execute_query(query)[0]
        
        return {
            "total_records": result[0],
            "readmission_rate_30day": round((result[1] / result[0] * 100) if result[0] > 0 else 0, 2),
            "hospital_acquired_infections": result[2],
            "average_medication_adherence": round(float(result[3]) if result[3] else 0, 2),
            "average_care_coordination_score": round(float(result[4]) if result[4] else 0, 1),
            "average_clinical_outcome_score": round(float(result[5]) if result[5] else 0, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== AI Chat Endpoints ====================

@app.post("/chat/analyze")
async def chat_analyze(message: ChatMessage) -> ChatResponse:
    """Analyze healthcare metrics using AI"""
    try:
        if not message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get analysis from Claude
        result = analyzer.analyze_metrics(message.message)
        
        return ChatResponse(
            response=result["response"],
            analysis=f"Analysis by {result['model']}",
            suggestions=result.get("suggestions", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/chat/clear-history")
async def clear_chat_history():
    """Clear chat conversation history"""
    global analyzer
    analyzer.conversation_history = []
    return {"message": "Chat history cleared"}

# ==================== Dashboard Overview ====================

@app.get("/dashboard/overview")
async def get_dashboard_overview():
    """Get comprehensive dashboard overview"""
    try:
        metrics = {
            "gaps_in_care": execute_query(
                "SELECT COUNT(*) as total, SUM(CASE WHEN is_gap=1 THEN 1 ELSE 0 END) as open FROM gaps_in_care"
            )[0],
            "hedis": execute_query(
                "SELECT COUNT(*) as total, SUM(CASE WHEN status='Met' THEN 1 ELSE 0 END) as met FROM hedis_metrics"
            )[0],
            "clinical_quality": execute_query(
                "SELECT COUNT(*) as total, SUM(CASE WHEN readmission_30day=1 THEN 1 ELSE 0 END) as readmissions FROM clinical_quality"
            )[0],
            "providers": execute_query("SELECT COUNT(*) as count FROM providers")[0][0]
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_gaps": metrics["gaps_in_care"][0],
            "open_gaps": metrics["gaps_in_care"][1],
            "hedis_measures": metrics["hedis"][0],
            "measures_met": metrics["hedis"][1],
            "quality_records": metrics["clinical_quality"][0],
            "readmissions_30day": metrics["clinical_quality"][1],
            "total_providers": metrics["providers"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)