from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# Request schemas
class GovernmentAlignmentRequest(BaseModel):
    research_topic: str = Field(..., min_length=10, description="Research topic/title")
    research_abstract: str = Field(..., min_length=100, description="Research abstract")
    keywords: Optional[List[str]] = Field(default=None, description="Research keywords")


class ImpactPredictionRequest(BaseModel):
    research_topic: str = Field(..., min_length=10, description="Research topic/title")
    research_abstract: str = Field(..., min_length=100, description="Research abstract")
    target_districts: Optional[List[str]] = Field(default=None, description="Target districts")
    research_priorities: Optional[List[Dict]] = Field(
        default=None,
        description="Matching government priorities from alignment analysis"
    )


# Response schemas
class GovernmentPriority(BaseModel):
    name: str
    category: str
    description: str
    budget_crores: float
    target_beneficiaries: str
    target_districts: List[str]
    sdgs: List[int]
    match_score: float
    relevance_explanation: str


class FundingOpportunity(BaseModel):
    scheme_name: str
    organization: str
    amount_range: str
    eligibility: str
    application_process: str
    deadline: str
    relevance_score: float


class ImpactArea(BaseModel):
    area: str
    description: str
    estimated_beneficiaries: int
    key_districts: List[str]
    actionable_steps: List[str]


class SDGAlignment(BaseModel):
    sdg_number: int
    sdg_name: str
    alignment_score: float
    specific_targets: List[str]


class GovernmentAlignmentResponse(BaseModel):
    research_topic: str
    matching_priorities: List[GovernmentPriority]
    funding_opportunities: List[FundingOpportunity]
    impact_areas: List[ImpactArea]
    sdg_alignment: List[SDGAlignment]
    overall_alignment_score: float
    recommendations: List[str]


# Impact prediction response components
class PopulationImpact(BaseModel):
    total_population: int
    direct_beneficiaries: int
    indirect_beneficiaries: int
    total_reach: int
    percentage_of_state: float
    district_breakdown: List[Dict]


class EconomicImpact(BaseModel):
    per_capita_annual_benefit: int
    annual_direct_benefit_inr: int
    economic_multiplier: float
    total_annual_benefit_inr: int
    five_year_projection_inr: int
    gdp_impact_percentage: float
    budget_savings: Dict
    job_creation_potential: int
    currency: str


class Timeline(BaseModel):
    total_duration_months: int
    total_duration_years: float
    phases: List[Dict]
    quick_wins_months: int
    full_impact_months: int


class ImpactScores(BaseModel):
    population_reach_score: float
    economic_impact_score: float
    feasibility_score: float
    sustainability_score: float
    overall_impact_score: float
    rating: str


class ResearchGap(BaseModel):
    gap: str
    description: str
    severity: str
    recommendation: str


class Collaboration(BaseModel):
    organization: str
    type: str
    role: str
    contact: str


class ScalabilityAnalysis(BaseModel):
    infrastructure_dependency: str
    skill_requirement: str
    capital_intensity: str
    scalability_potential: str
    current_coverage: int
    expansion_potential_districts: int
    estimated_scaling_cost_per_district: int


class ImpactPredictionResponse(BaseModel):
    research_area: str
    target_districts: List[str]
    population_impact: PopulationImpact
    economic_impact: EconomicImpact
    timeline: Timeline
    impact_scores: ImpactScores
    research_gaps: List[ResearchGap]
    collaboration_opportunities: List[Collaboration]
    scalability_analysis: ScalabilityAnalysis


# List response schemas
class PriorityListResponse(BaseModel):
    total_priorities: int
    priorities: List[Dict]
    categories: List[str]
    total_budget_crores: float


class FundingListResponse(BaseModel):
    total_schemes: int
    funding_schemes: List[Dict]
    organizations: List[str]


# District info
class DistrictInfo(BaseModel):
    name: str
    population: int
    literacy_rate: float
    rural_percentage: float
    major_issues: List[str]
    economic_activity: str


class DistrictListResponse(BaseModel):
    total_districts: int
    districts: List[DistrictInfo]
