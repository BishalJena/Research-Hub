from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.government import (
    GovernmentAlignmentRequest,
    GovernmentAlignmentResponse,
    ImpactPredictionRequest,
    ImpactPredictionResponse,
    PriorityListResponse,
    FundingListResponse,
    DistrictListResponse,
    DistrictInfo
)
from app.services.ap_government_service import APGovernmentService
from app.services.impact_predictor_service import ImpactPredictorService

router = APIRouter()


@router.post("/analyze-alignment", response_model=GovernmentAlignmentResponse)
async def analyze_government_alignment(
    request: GovernmentAlignmentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze research alignment with AP Government priorities

    This endpoint analyzes how well a research topic/abstract aligns with:
    - Current AP Government priorities and schemes
    - Available funding opportunities
    - Potential impact areas in AP districts
    - UN Sustainable Development Goals (SDGs)

    Returns actionable recommendations for positioning research to maximize
    government support and real-world impact.

    **Innovation Feature**: Connects academic research directly to state-level
    priorities using real AP Government budget data and schemes.
    """
    service = APGovernmentService()

    try:
        result = await service.analyze_research_alignment(
            research_topic=request.research_topic,
            research_abstract=request.research_abstract,
            research_keywords=request.keywords or []
        )

        return GovernmentAlignmentResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing government alignment: {str(e)}"
        )


@router.post("/predict-impact", response_model=ImpactPredictionResponse)
async def predict_research_impact(
    request: ImpactPredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Predict real-world impact of research implementation

    Provides comprehensive impact analysis including:
    - Population reach (direct and indirect beneficiaries)
    - Economic benefits (₹ per year, GDP impact, job creation)
    - Implementation timeline with phases
    - Impact scores (reach, economic, feasibility, sustainability)
    - Research gaps and challenges
    - Collaboration opportunities with government departments
    - Scalability analysis across AP districts

    Uses real AP district data (population, literacy, rural %, major issues).

    **Innovation Feature**: Quantifies research impact using actual demographic
    and economic data from 26 AP districts.
    """
    service = ImpactPredictorService()

    try:
        result = await service.predict_impact(
            research_topic=request.research_topic,
            research_abstract=request.research_abstract,
            target_districts=request.target_districts,
            research_priorities=request.research_priorities
        )

        return ImpactPredictionResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting impact: {str(e)}"
        )


@router.get("/priorities", response_model=PriorityListResponse)
async def list_government_priorities(
    category: Optional[str] = None,
    min_budget: Optional[float] = None
):
    """
    List all AP Government priorities and schemes

    Query Parameters:
    - **category**: Filter by category (agriculture, water, energy, education, health, infrastructure)
    - **min_budget**: Minimum budget in crores

    Returns all government priorities from AP 2024-25 budget with:
    - Scheme details and budgets
    - Target beneficiaries and districts
    - SDG alignments

    No authentication required - public information.
    """
    service = APGovernmentService()

    priorities = service.government_priorities

    # Apply filters
    if category:
        priorities = [p for p in priorities if p['category'].lower() == category.lower()]

    if min_budget:
        priorities = [p for p in priorities if p['budget_crores'] >= min_budget]

    # Get unique categories
    categories = list(set(p['category'] for p in service.government_priorities))

    # Calculate total budget
    total_budget = sum(p['budget_crores'] for p in priorities)

    return PriorityListResponse(
        total_priorities=len(priorities),
        priorities=priorities,
        categories=categories,
        total_budget_crores=total_budget
    )


@router.get("/funding", response_model=FundingListResponse)
async def list_funding_schemes(
    organization: Optional[str] = None,
    min_amount: Optional[int] = None
):
    """
    List available funding schemes for researchers

    Query Parameters:
    - **organization**: Filter by funding organization
    - **min_amount**: Minimum funding amount in lakhs

    Returns funding opportunities including:
    - Government schemes (AP Innovation Cell, DST-SERB, AICTE, CSIR, etc.)
    - Eligibility criteria
    - Application process
    - Amount ranges

    No authentication required - public information.
    """
    service = APGovernmentService()

    schemes = service.funding_schemes.copy()

    # Apply filters
    if organization:
        schemes = [
            s for s in schemes
            if organization.lower() in s['organization'].lower()
        ]

    if min_amount:
        # Parse amount ranges and filter
        filtered = []
        for scheme in schemes:
            amount_str = scheme['amount_range']
            # Extract maximum amount (rough parsing)
            if 'lakh' in amount_str.lower():
                try:
                    # Extract numbers
                    import re
                    numbers = re.findall(r'\d+', amount_str)
                    if numbers:
                        max_amount = int(numbers[-1])  # Take last number as max
                        if max_amount >= min_amount:
                            filtered.append(scheme)
                except:
                    filtered.append(scheme)  # Include if can't parse
            else:
                filtered.append(scheme)  # Include if not in lakhs
        schemes = filtered

    # Get unique organizations
    organizations = list(set(s['organization'] for s in service.funding_schemes))

    return FundingListResponse(
        total_schemes=len(schemes),
        funding_schemes=schemes,
        organizations=organizations
    )


@router.get("/districts", response_model=DistrictListResponse)
async def list_districts(
    min_population: Optional[int] = None,
    min_literacy: Optional[float] = None,
    major_issue: Optional[str] = None
):
    """
    Get AP district information

    Query Parameters:
    - **min_population**: Minimum population
    - **min_literacy**: Minimum literacy rate (percentage)
    - **major_issue**: Filter by major issue (e.g., "drought", "water", "education")

    Returns district-level data including:
    - Population and literacy rates
    - Rural/urban distribution
    - Major issues
    - Economic activities

    Useful for identifying target districts for research implementation.

    No authentication required - public information.
    """
    service = ImpactPredictorService()

    districts_data = service.district_data

    # Convert to list of district info
    districts = [
        {
            "name": name,
            **data
        }
        for name, data in districts_data.items()
    ]

    # Apply filters
    if min_population:
        districts = [d for d in districts if d['population'] >= min_population]

    if min_literacy:
        districts = [d for d in districts if d['literacy_rate'] >= min_literacy]

    if major_issue:
        districts = [
            d for d in districts
            if any(major_issue.lower() in issue.lower() for issue in d['major_issues'])
        ]

    return DistrictListResponse(
        total_districts=len(districts),
        districts=[DistrictInfo(**d) for d in districts]
    )


@router.get("/priorities/{priority_name}")
async def get_priority_details(priority_name: str):
    """
    Get detailed information about a specific government priority

    Returns complete details including budget, target districts, beneficiaries,
    SDG alignment, and implementation status.
    """
    service = APGovernmentService()

    # Find priority by name (case-insensitive partial match)
    priority = None
    for p in service.government_priorities:
        if priority_name.lower() in p['name'].lower():
            priority = p
            break

    if not priority:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Priority '{priority_name}' not found"
        )

    return priority


@router.get("/funding/{scheme_name}")
async def get_funding_details(scheme_name: str):
    """
    Get detailed information about a specific funding scheme

    Returns complete details including eligibility, application process,
    deadlines, and contact information.
    """
    service = APGovernmentService()

    # Find scheme by name (case-insensitive partial match)
    scheme = None
    for s in service.funding_schemes:
        if scheme_name.lower() in s['scheme_name'].lower():
            scheme = s
            break

    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funding scheme '{scheme_name}' not found"
        )

    return scheme


@router.get("/sdgs")
async def list_sdgs():
    """
    List all UN Sustainable Development Goals (SDGs)

    Returns the 17 SDGs with descriptions and how they relate to AP priorities.
    """
    service = APGovernmentService()

    return {
        "total_sdgs": len(service.sdg_mapping),
        "sdgs": service.sdg_mapping
    }


@router.post("/analyze-full")
async def full_analysis(
    request: GovernmentAlignmentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Comprehensive analysis combining alignment and impact prediction

    **All-in-one endpoint** that provides:
    1. Government alignment analysis
    2. Impact prediction with district-level data
    3. Funding recommendations
    4. Collaboration opportunities
    5. Implementation roadmap

    Use this for complete research positioning analysis.
    """
    gov_service = APGovernmentService()
    impact_service = ImpactPredictorService()

    try:
        # Step 1: Analyze government alignment
        alignment = await gov_service.analyze_research_alignment(
            research_topic=request.research_topic,
            research_abstract=request.research_abstract,
            research_keywords=request.keywords or []
        )

        # Step 2: Extract target districts from alignment
        target_districts = []
        for priority in alignment['matching_priorities']:
            target_districts.extend(priority.get('target_districts', []))
        target_districts = list(set(target_districts))  # Unique districts

        # Step 3: Predict impact
        impact = await impact_service.predict_impact(
            research_topic=request.research_topic,
            research_abstract=request.research_abstract,
            target_districts=target_districts if target_districts else None,
            research_priorities=alignment['matching_priorities']
        )

        # Combine results
        return {
            "research_topic": request.research_topic,
            "government_alignment": alignment,
            "impact_prediction": impact,
            "executive_summary": {
                "overall_alignment_score": alignment['overall_alignment_score'],
                "overall_impact_score": impact['impact_scores']['overall_impact_score'],
                "impact_rating": impact['impact_scores']['rating'],
                "total_beneficiaries": impact['population_impact']['total_reach'],
                "economic_benefit_5yr_cr": round(
                    impact['economic_impact']['five_year_projection_inr'] / 10000000, 2
                ),
                "implementation_years": impact['timeline']['total_duration_years'],
                "top_priority": alignment['matching_priorities'][0]['name'] if alignment['matching_priorities'] else None,
                "top_funding": alignment['funding_opportunities'][0]['scheme_name'] if alignment['funding_opportunities'] else None,
                "target_districts_count": len(target_districts)
            },
            "actionable_next_steps": [
                f"Apply for {alignment['funding_opportunities'][0]['scheme_name']}" if alignment['funding_opportunities'] else "Explore funding opportunities",
                f"Partner with {impact['collaboration_opportunities'][0]['organization']}" if impact['collaboration_opportunities'] else "Identify collaboration partners",
                f"Address key gap: {impact['research_gaps'][0]['gap']}" if impact['research_gaps'] else "Refine research design",
                f"Target implementation in {len(target_districts)} priority districts",
                "Prepare pilot proposal for government approval"
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in full analysis: {str(e)}"
        )
