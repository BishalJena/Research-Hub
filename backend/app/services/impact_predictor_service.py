"""
Research Impact Predictor Service
Predicts real-world impact of research on AP districts and population
"""
from typing import List, Dict, Optional
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ImpactPredictorService:
    """Service for predicting real-world impact of research"""

    def __init__(self):
        # District-level detailed data for AP
        self.district_data = self._load_district_data()

        # Research area to impact metrics mapping
        self.impact_metrics = {
            "agriculture": {
                "primary_beneficiaries": "farmers",
                "economic_multiplier": 2.5,
                "implementation_months": 18,
                "key_indicators": ["crop yield", "farmer income", "soil health"]
            },
            "water": {
                "primary_beneficiaries": "rural households",
                "economic_multiplier": 3.0,
                "implementation_months": 24,
                "key_indicators": ["water quality", "health outcomes", "accessibility"]
            },
            "energy": {
                "primary_beneficiaries": "households",
                "economic_multiplier": 2.8,
                "implementation_months": 12,
                "key_indicators": ["energy cost", "carbon reduction", "reliability"]
            },
            "education": {
                "primary_beneficiaries": "students",
                "economic_multiplier": 4.0,
                "implementation_months": 36,
                "key_indicators": ["literacy rate", "employment", "income mobility"]
            },
            "health": {
                "primary_beneficiaries": "population",
                "economic_multiplier": 5.0,
                "implementation_months": 24,
                "key_indicators": ["disease prevalence", "mortality rate", "healthcare access"]
            },
            "infrastructure": {
                "primary_beneficiaries": "urban population",
                "economic_multiplier": 3.5,
                "implementation_months": 36,
                "key_indicators": ["connectivity", "economic activity", "quality of life"]
            }
        }

    async def predict_impact(
        self,
        research_topic: str,
        research_abstract: str,
        target_districts: List[str] = None,
        research_priorities: List[Dict] = None
    ) -> Dict:
        """
        Predict real-world impact of research

        Args:
            research_topic: Research topic/title
            research_abstract: Research abstract
            target_districts: Optional list of target districts
            research_priorities: Matching government priorities from AP service

        Returns:
            Impact prediction with population reach, economic benefits, timeline
        """
        logger.info(f"Predicting impact for: {research_topic}")

        # Determine research area
        research_area = self._classify_research_area(
            research_topic + " " + research_abstract
        )

        # If no target districts specified, infer from priorities
        if not target_districts and research_priorities:
            target_districts = self._extract_target_districts(research_priorities)

        # If still no districts, use all districts
        if not target_districts:
            target_districts = list(self.district_data.keys())

        # Calculate population impact
        population_impact = self._calculate_population_impact(
            target_districts, research_area
        )

        # Estimate economic benefits
        economic_impact = self._estimate_economic_benefits(
            population_impact, research_area, research_priorities
        )

        # Predict implementation timeline
        timeline = self._predict_timeline(research_area, target_districts)

        # Identify research gaps
        gaps = self._identify_gaps(research_topic, research_abstract, research_area)

        # Suggest collaborations
        collaborations = self._suggest_collaborations(
            research_area, target_districts, research_priorities
        )

        # Calculate impact scores
        impact_scores = self._calculate_impact_scores(
            population_impact,
            economic_impact,
            timeline,
            research_area
        )

        return {
            "research_area": research_area,
            "target_districts": target_districts,
            "population_impact": population_impact,
            "economic_impact": economic_impact,
            "timeline": timeline,
            "impact_scores": impact_scores,
            "research_gaps": gaps,
            "collaboration_opportunities": collaborations,
            "scalability_analysis": self._analyze_scalability(
                research_area, target_districts
            )
        }

    def _classify_research_area(self, text: str) -> str:
        """Classify research into primary area"""
        text_lower = text.lower()

        area_keywords = {
            "agriculture": ["crop", "farm", "agriculture", "soil", "irrigation",
                          "pest", "yield", "cultivation", "fertilizer"],
            "water": ["water", "fluoride", "drinking", "groundwater", "purification",
                     "contamination", "hydration", "aquifer"],
            "energy": ["solar", "energy", "power", "renewable", "electricity",
                      "battery", "grid", "wind", "biomass"],
            "education": ["education", "learning", "student", "teaching", "literacy",
                         "school", "college", "curriculum", "pedagogy"],
            "health": ["health", "medical", "disease", "hospital", "treatment",
                      "diagnosis", "patient", "clinical", "medicine"],
            "infrastructure": ["infrastructure", "road", "transport", "connectivity",
                             "urban", "construction", "housing"]
        }

        scores = {}
        for area, keywords in area_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[area] = score

        # Return area with highest score
        if scores:
            return max(scores, key=scores.get)
        return "multidisciplinary"

    def _extract_target_districts(self, priorities: List[Dict]) -> List[str]:
        """Extract target districts from matching priorities"""
        districts = set()
        for priority in priorities:
            if 'target_districts' in priority:
                districts.update(priority['target_districts'])
        return list(districts)

    def _calculate_population_impact(
        self,
        districts: List[str],
        research_area: str
    ) -> Dict:
        """Calculate population that would be impacted"""
        total_population = 0
        direct_beneficiaries = 0
        indirect_beneficiaries = 0

        district_breakdown = []

        for district in districts:
            if district in self.district_data:
                data = self.district_data[district]
                dist_pop = data['population']
                total_population += dist_pop

                # Calculate direct beneficiaries based on research area
                if research_area == "agriculture":
                    direct = int(dist_pop * data['rural_percentage'] * 0.40)  # 40% farmers
                elif research_area == "water":
                    direct = int(dist_pop * data['rural_percentage'])  # All rural
                elif research_area == "energy":
                    direct = int(dist_pop * 0.70)  # 70% households
                elif research_area == "education":
                    direct = int(dist_pop * 0.25)  # 25% student age
                elif research_area == "health":
                    direct = dist_pop  # Everyone
                else:
                    direct = int(dist_pop * 0.50)

                indirect = int(direct * 2.5)  # Indirect beneficiaries

                direct_beneficiaries += direct
                indirect_beneficiaries += indirect

                district_breakdown.append({
                    "district": district,
                    "population": dist_pop,
                    "direct_beneficiaries": direct,
                    "indirect_beneficiaries": indirect,
                    "literacy_rate": data['literacy_rate'],
                    "rural_percentage": data['rural_percentage']
                })

        return {
            "total_population": total_population,
            "direct_beneficiaries": direct_beneficiaries,
            "indirect_beneficiaries": indirect_beneficiaries,
            "total_reach": direct_beneficiaries + indirect_beneficiaries,
            "percentage_of_state": round(
                (total_population / 53000000) * 100, 2  # AP population ~53M
            ),
            "district_breakdown": district_breakdown
        }

    def _estimate_economic_benefits(
        self,
        population_impact: Dict,
        research_area: str,
        priorities: List[Dict] = None
    ) -> Dict:
        """Estimate economic benefits of implementation"""
        direct_beneficiaries = population_impact['direct_beneficiaries']

        # Get multiplier for research area
        multiplier = self.impact_metrics.get(
            research_area, {}
        ).get('economic_multiplier', 2.0)

        # Average benefit per person per year (in INR)
        # Based on research area
        per_capita_benefit = {
            "agriculture": 15000,  # ₹15k per farmer per year
            "water": 5000,         # ₹5k health/productivity savings
            "energy": 8000,        # ₹8k energy cost savings
            "education": 25000,    # ₹25k income increase over time
            "health": 12000,       # ₹12k healthcare cost reduction
            "infrastructure": 10000  # ₹10k productivity gain
        }.get(research_area, 8000)

        # Direct economic benefit
        annual_direct_benefit = direct_beneficiaries * per_capita_benefit

        # Apply multiplier for indirect effects
        total_annual_benefit = annual_direct_benefit * multiplier

        # 5-year projection
        five_year_benefit = total_annual_benefit * 5

        # Calculate GDP impact (AP GDP ~₹11 lakh crore)
        gdp_impact_percentage = (total_annual_benefit / 1100000000000) * 100

        # Estimate government budget savings
        budget_savings = self._estimate_budget_savings(
            research_area, direct_beneficiaries, priorities
        )

        return {
            "per_capita_annual_benefit": per_capita_benefit,
            "annual_direct_benefit_inr": annual_direct_benefit,
            "economic_multiplier": multiplier,
            "total_annual_benefit_inr": total_annual_benefit,
            "five_year_projection_inr": five_year_benefit,
            "gdp_impact_percentage": round(gdp_impact_percentage, 4),
            "budget_savings": budget_savings,
            "job_creation_potential": int(direct_beneficiaries * 0.05),  # 5% jobs
            "currency": "INR"
        }

    def _estimate_budget_savings(
        self,
        research_area: str,
        beneficiaries: int,
        priorities: List[Dict] = None
    ) -> Dict:
        """Estimate government budget savings"""
        # Current cost per beneficiary for different sectors
        current_costs = {
            "agriculture": 2000,  # Subsidy/support per farmer
            "water": 3000,        # Water provision cost
            "energy": 4000,       # Energy subsidy
            "education": 15000,   # Per student cost
            "health": 8000,       # Per capita healthcare
            "infrastructure": 5000
        }

        current_cost = current_costs.get(research_area, 3000)
        efficiency_gain = 0.20  # 20% efficiency gain from research

        annual_savings = beneficiaries * current_cost * efficiency_gain

        return {
            "annual_budget_savings_inr": annual_savings,
            "efficiency_gain_percentage": efficiency_gain * 100,
            "five_year_savings_inr": annual_savings * 5
        }

    def _predict_timeline(
        self,
        research_area: str,
        districts: List[str]
    ) -> Dict:
        """Predict implementation timeline"""
        base_months = self.impact_metrics.get(
            research_area, {}
        ).get('implementation_months', 24)

        # Adjust based on number of districts
        district_factor = 1 + (len(districts) - 1) * 0.1  # 10% per additional district
        total_months = int(base_months * district_factor)

        phases = [
            {
                "phase": "Research Validation",
                "duration_months": int(total_months * 0.15),
                "activities": [
                    "Peer review and validation",
                    "Field testing in pilot locations",
                    "Stakeholder consultation"
                ]
            },
            {
                "phase": "Pilot Implementation",
                "duration_months": int(total_months * 0.25),
                "activities": [
                    "Select 2-3 pilot districts",
                    "Train local teams",
                    "Implement and monitor",
                    "Collect feedback and metrics"
                ]
            },
            {
                "phase": "Scale-Up",
                "duration_months": int(total_months * 0.40),
                "activities": [
                    "Expand to all target districts",
                    "Infrastructure development",
                    "Capacity building",
                    "Continuous monitoring"
                ]
            },
            {
                "phase": "Stabilization",
                "duration_months": int(total_months * 0.20),
                "activities": [
                    "Optimize operations",
                    "Impact assessment",
                    "Sustainability planning",
                    "Knowledge transfer"
                ]
            }
        ]

        return {
            "total_duration_months": total_months,
            "total_duration_years": round(total_months / 12, 1),
            "phases": phases,
            "quick_wins_months": int(total_months * 0.25),
            "full_impact_months": total_months
        }

    def _identify_gaps(
        self,
        topic: str,
        abstract: str,
        research_area: str
    ) -> List[Dict]:
        """Identify gaps in current research"""
        text = (topic + " " + abstract).lower()

        # Common gaps by research area
        potential_gaps = {
            "agriculture": [
                {
                    "gap": "Local climate adaptation",
                    "description": "Research may not account for AP's specific climate zones",
                    "severity": "high"
                },
                {
                    "gap": "Farmer adoption barriers",
                    "description": "Implementation challenges with smallholder farmers",
                    "severity": "medium"
                },
                {
                    "gap": "Supply chain integration",
                    "description": "Connection to markets and storage facilities",
                    "severity": "medium"
                }
            ],
            "water": [
                {
                    "gap": "Geological variations",
                    "description": "Different districts have different water table levels",
                    "severity": "high"
                },
                {
                    "gap": "Community management",
                    "description": "Sustainable operation and maintenance models",
                    "severity": "high"
                },
                {
                    "gap": "Cost-effectiveness",
                    "description": "Scalability to rural areas with limited budgets",
                    "severity": "medium"
                }
            ],
            "energy": [
                {
                    "gap": "Grid integration",
                    "description": "Connection to existing power infrastructure",
                    "severity": "medium"
                },
                {
                    "gap": "Maintenance ecosystem",
                    "description": "Local capacity for repair and maintenance",
                    "severity": "high"
                },
                {
                    "gap": "Financing models",
                    "description": "Affordable financing for rural households",
                    "severity": "high"
                }
            ],
            "education": [
                {
                    "gap": "Teacher training",
                    "description": "Capacity building for government college faculty",
                    "severity": "high"
                },
                {
                    "gap": "Multilingual support",
                    "description": "Content in Telugu and other local languages",
                    "severity": "medium"
                },
                {
                    "gap": "Infrastructure requirements",
                    "description": "Digital infrastructure in rural colleges",
                    "severity": "high"
                }
            ],
            "health": [
                {
                    "gap": "Last-mile delivery",
                    "description": "Reaching remote and tribal areas",
                    "severity": "high"
                },
                {
                    "gap": "Behavioral change",
                    "description": "Community awareness and adoption",
                    "severity": "medium"
                },
                {
                    "gap": "Integration with ASHA workers",
                    "description": "Leveraging existing health workforce",
                    "severity": "medium"
                }
            ]
        }

        gaps = potential_gaps.get(research_area, [])

        # Filter gaps based on whether they're mentioned in the research
        identified_gaps = []
        for gap in gaps:
            gap_keywords = gap['gap'].lower().split()
            mentioned = any(keyword in text for keyword in gap_keywords)

            if not mentioned:
                identified_gaps.append({
                    **gap,
                    "recommendation": f"Address {gap['gap'].lower()} in research design"
                })

        return identified_gaps

    def _suggest_collaborations(
        self,
        research_area: str,
        districts: List[str],
        priorities: List[Dict] = None
    ) -> List[Dict]:
        """Suggest collaboration opportunities"""
        collaborations = []

        # Government departments
        dept_mapping = {
            "agriculture": [
                {
                    "organization": "AP Agriculture Department",
                    "type": "government",
                    "role": "Policy implementation and farmer outreach",
                    "contact": "agriculture.ap.gov.in"
                },
                {
                    "organization": "ANGRAU (Acharya N.G. Ranga Agricultural University)",
                    "type": "academic",
                    "role": "Research validation and extension services",
                    "contact": "angrau.ac.in"
                }
            ],
            "water": [
                {
                    "organization": "AP Water Resources Department",
                    "type": "government",
                    "role": "Infrastructure and policy support",
                    "contact": "apwater.ap.gov.in"
                },
                {
                    "organization": "Ground Water Department, AP",
                    "type": "government",
                    "role": "Technical expertise and monitoring",
                    "contact": "apgroundwater.ap.gov.in"
                }
            ],
            "energy": [
                {
                    "organization": "AP State Energy Efficiency Development Corporation",
                    "type": "government",
                    "role": "Renewable energy implementation",
                    "contact": "nredcap.in"
                },
                {
                    "organization": "DISCOM (AP Power Distribution Companies)",
                    "type": "utility",
                    "role": "Grid integration and distribution",
                    "contact": "apdiscoms.ap.gov.in"
                }
            ],
            "education": [
                {
                    "organization": "AP Higher Education Department",
                    "type": "government",
                    "role": "Policy adoption and funding",
                    "contact": "aphe.ap.gov.in"
                },
                {
                    "organization": "AP State Council of Higher Education (APSCHE)",
                    "type": "regulatory",
                    "role": "Curriculum integration and accreditation",
                    "contact": "apsche.org"
                }
            ],
            "health": [
                {
                    "organization": "AP Health & Medical Services Department",
                    "type": "government",
                    "role": "Healthcare delivery and implementation",
                    "contact": "hmfw.ap.gov.in"
                },
                {
                    "organization": "NTR University of Health Sciences",
                    "type": "academic",
                    "role": "Medical research and training",
                    "contact": "ntruhs.ap.nic.in"
                }
            ]
        }

        collaborations.extend(dept_mapping.get(research_area, []))

        # District-level collaborations
        for district in districts[:3]:  # Top 3 districts
            collaborations.append({
                "organization": f"{district} District Collector Office",
                "type": "local_government",
                "role": "Local implementation and monitoring",
                "contact": f"District administration - {district}"
            })

        # NGOs and international organizations
        if research_area in ["agriculture", "water", "health"]:
            collaborations.append({
                "organization": "World Bank / ADB",
                "type": "international",
                "role": "Funding and technical expertise",
                "contact": "International development banks"
            })

        # Industry partners
        if research_area in ["energy", "infrastructure"]:
            collaborations.append({
                "organization": "Private Sector Companies",
                "type": "industry",
                "role": "Technology transfer and scalability",
                "contact": "Industry associations in AP"
            })

        return collaborations

    def _calculate_impact_scores(
        self,
        population_impact: Dict,
        economic_impact: Dict,
        timeline: Dict,
        research_area: str
    ) -> Dict:
        """Calculate various impact scores"""
        # Population reach score (0-100)
        reach_score = min(
            (population_impact['total_reach'] / 10000000) * 100,  # 10M max
            100
        )

        # Economic impact score (0-100)
        economic_score = min(
            (economic_impact['total_annual_benefit_inr'] / 1000000000) * 100,  # ₹1B max
            100
        )

        # Feasibility score based on timeline (0-100)
        # Shorter timeline = higher feasibility
        feasibility_score = max(
            100 - (timeline['total_duration_months'] / 60 * 100),  # 60 months max
            20  # Min 20
        )

        # Sustainability score (based on research area)
        sustainability_scores = {
            "agriculture": 85,
            "water": 90,
            "energy": 80,
            "education": 95,
            "health": 90,
            "infrastructure": 75
        }
        sustainability_score = sustainability_scores.get(research_area, 70)

        # Overall impact score (weighted average)
        overall_score = (
            reach_score * 0.30 +
            economic_score * 0.30 +
            feasibility_score * 0.20 +
            sustainability_score * 0.20
        )

        return {
            "population_reach_score": round(reach_score, 2),
            "economic_impact_score": round(economic_score, 2),
            "feasibility_score": round(feasibility_score, 2),
            "sustainability_score": round(sustainability_score, 2),
            "overall_impact_score": round(overall_score, 2),
            "rating": self._get_rating(overall_score)
        }

    def _get_rating(self, score: float) -> str:
        """Convert score to rating"""
        if score >= 80:
            return "Transformative Impact"
        elif score >= 60:
            return "High Impact"
        elif score >= 40:
            return "Moderate Impact"
        else:
            return "Limited Impact"

    def _analyze_scalability(
        self,
        research_area: str,
        districts: List[str]
    ) -> Dict:
        """Analyze scalability potential"""
        # Factors affecting scalability
        factors = {
            "agriculture": {
                "infrastructure_dependency": "medium",
                "skill_requirement": "medium",
                "capital_intensity": "medium",
                "scalability_potential": "high"
            },
            "water": {
                "infrastructure_dependency": "high",
                "skill_requirement": "low",
                "capital_intensity": "high",
                "scalability_potential": "medium"
            },
            "energy": {
                "infrastructure_dependency": "high",
                "skill_requirement": "medium",
                "capital_intensity": "high",
                "scalability_potential": "high"
            },
            "education": {
                "infrastructure_dependency": "medium",
                "skill_requirement": "high",
                "capital_intensity": "low",
                "scalability_potential": "very high"
            },
            "health": {
                "infrastructure_dependency": "medium",
                "skill_requirement": "high",
                "capital_intensity": "medium",
                "scalability_potential": "high"
            }
        }

        analysis = factors.get(research_area, {
            "infrastructure_dependency": "medium",
            "skill_requirement": "medium",
            "capital_intensity": "medium",
            "scalability_potential": "medium"
        })

        # Add district-specific insights
        analysis['current_coverage'] = len(districts)
        analysis['expansion_potential_districts'] = 26 - len(districts)  # AP has 26 districts
        analysis['estimated_scaling_cost_per_district'] = self._estimate_district_cost(research_area)

        return analysis

    def _estimate_district_cost(self, research_area: str) -> int:
        """Estimate cost to scale to one additional district"""
        base_costs = {
            "agriculture": 5000000,    # ₹50L per district
            "water": 20000000,         # ₹2Cr per district
            "energy": 15000000,        # ₹1.5Cr per district
            "education": 3000000,      # ₹30L per district
            "health": 10000000,        # ₹1Cr per district
            "infrastructure": 50000000  # ₹5Cr per district
        }
        return base_costs.get(research_area, 10000000)

    def _load_district_data(self) -> Dict:
        """Load detailed district data for AP"""
        return {
            "Visakhapatnam": {
                "population": 4290000,
                "literacy_rate": 67.7,
                "rural_percentage": 0.42,
                "major_issues": ["urban pollution", "coastal erosion", "industrial waste"],
                "economic_activity": "industrial, port, tourism"
            },
            "East Godavari": {
                "population": 5154000,
                "literacy_rate": 64.1,
                "rural_percentage": 0.71,
                "major_issues": ["flooding", "agriculture", "coconut cultivation"],
                "economic_activity": "agriculture, aquaculture"
            },
            "West Godavari": {
                "population": 3936000,
                "literacy_rate": 68.5,
                "rural_percentage": 0.68,
                "major_issues": ["irrigation", "aquaculture", "coastal issues"],
                "economic_activity": "agriculture, aquaculture"
            },
            "Krishna": {
                "population": 4517000,
                "literacy_rate": 73.7,
                "rural_percentage": 0.52,
                "major_issues": ["water management", "urban growth", "agriculture"],
                "economic_activity": "agriculture, urban services"
            },
            "Guntur": {
                "population": 4887000,
                "literacy_rate": 67.4,
                "rural_percentage": 0.58,
                "major_issues": ["water scarcity", "cotton farming", "tobacco"],
                "economic_activity": "agriculture, trade"
            },
            "Prakasam": {
                "population": 3392000,
                "literacy_rate": 63.1,
                "rural_percentage": 0.73,
                "major_issues": ["fluoride in water", "drought", "migration"],
                "economic_activity": "agriculture, limestone"
            },
            "Nellore": {
                "population": 2963000,
                "literacy_rate": 68.9,
                "rural_percentage": 0.66,
                "major_issues": ["fluoride", "cyclones", "aquaculture"],
                "economic_activity": "agriculture, aquaculture, industry"
            },
            "Chittoor": {
                "population": 4174000,
                "literacy_rate": 71.5,
                "rural_percentage": 0.72,
                "major_issues": ["water scarcity", "mango cultivation", "migration"],
                "economic_activity": "agriculture, horticulture"
            },
            "Kadapa": {
                "population": 2884000,
                "literacy_rate": 68.0,
                "rural_percentage": 0.71,
                "major_issues": ["drought", "mining", "water scarcity"],
                "economic_activity": "mining, agriculture"
            },
            "Anantapur": {
                "population": 4081000,
                "literacy_rate": 64.3,
                "rural_percentage": 0.78,
                "major_issues": ["severe drought", "groundwater depletion", "migration"],
                "economic_activity": "agriculture (rainfed), mining"
            },
            "Kurnool": {
                "population": 4053000,
                "literacy_rate": 59.6,
                "rural_percentage": 0.71,
                "major_issues": ["water scarcity", "drought", "agriculture"],
                "economic_activity": "agriculture, cement"
            },
            "Srikakulam": {
                "population": 2703000,
                "literacy_rate": 61.7,
                "rural_percentage": 0.85,
                "major_issues": ["poverty", "tribal development", "cashew"],
                "economic_activity": "agriculture, cashew"
            },
            "Vizianagaram": {
                "population": 2344000,
                "literacy_rate": 58.9,
                "rural_percentage": 0.82,
                "major_issues": ["tribal welfare", "education", "connectivity"],
                "economic_activity": "agriculture, small industries"
            }
        }
