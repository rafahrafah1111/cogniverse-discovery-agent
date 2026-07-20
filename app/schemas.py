from pydantic import BaseModel, Field
from typing import List, Optional

class RoleInfo(BaseModel):
    role_title: Optional[str] = Field(default=None, description="Current role in the sales function")

class DepartmentKPIs(BaseModel):
    tracked_kpis: List[str] = Field(default_factory=list, description="KPIs tracked by the department")
    top_priorities: List[str] = Field(default_factory=list, description="Top ranked KPIs")
    reporting_method: Optional[str] = Field(default=None, description="How KPIs are reported to leadership")
    weekly_reporting_hours: Optional[str] = Field(default=None, description="Time spent weekly on KPI reporting")

class WorkflowPainPoint(BaseModel):
    process_name: Optional[str] = Field(default=None, description="Process taking the most time or causing difficulty")
    frequency: Optional[str] = Field(default=None, description="How often the process occurs")
    time_consumed: Optional[str] = Field(default=None, description="Weekly time consumed")
    systems_used: List[str] = Field(default_factory=list, description="Systems or sources holding data")
    business_impact: List[str] = Field(default_factory=list, description="Areas of business impact")
    workarounds: List[str] = Field(default_factory=list, description="Current workarounds used")

class DiscoverySessionState(BaseModel):
    role_info: RoleInfo = Field(default_factory=RoleInfo)
    kpis: DepartmentKPIs = Field(default_factory=DepartmentKPIs)
    primary_workflow: WorkflowPainPoint = Field(default_factory=WorkflowPainPoint)
    completed_topics: List[str] = Field(default_factory=list)
    current_topic: str = Field(default="About You")