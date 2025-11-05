"""
AP Government Priority Service - Maps research to government priorities
"""
from typing import List, Dict, Optional
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class APGovernmentService:
    """Service for analyzing AP government research priorities and funding"""

    def __init__(self):
        # In production, this would scrape real government websites
        # For now, we'll use curated data based on actual AP priorities
        self.government_priorities = self._load_government_priorities()
        self.funding_schemes = self._load_funding_schemes()
        self.district_data = self._load_district_data()
        self.sdg_mapping = self._load_sdg_mapping()

    async def analyze_research_alignment(
        self,
        research_topic: str,
        research_abstract: str,
        keywords: List[str] = None
    ) -> Dict:
        """
        Analyze how research aligns with AP government priorities

        Args:
            research_topic: Research topic/title
            research_abstract: Research abstract
            keywords: Research keywords

        Returns:
            Dictionary with alignment analysis
        """
        logger.info(f"Analyzing alignment for: {research_topic}")

        # Combine text for analysis
        full_text = f"{research_topic} {research_abstract}"
        if keywords:
            full_text += " " + " ".join(keywords)
        full_text = full_text.lower()

        # Find matching priorities
        matching_priorities = []
        for priority in self.government_priorities:
            match_score = self._calculate_priority_match(full_text, priority)
            if match_score > 0.3:  # Threshold
                matching_priorities.append({
                    **priority,
                    'match_score': match_score
                })

        # Sort by match score
        matching_priorities.sort(key=lambda x: x['match_score'], reverse=True)

        # Find relevant funding
        relevant_funding = self._find_relevant_funding(full_text, matching_priorities)

        # Calculate impact potential
        impact_areas = self._identify_impact_areas(full_text, matching_priorities)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            matching_priorities,
            relevant_funding,
            impact_areas
        )

        result = {
            'research_topic': research_topic,
            'overall_alignment_score': self._calculate_overall_alignment(matching_priorities),
            'matching_priorities': matching_priorities[:5],  # Top 5
            'funding_opportunities': relevant_funding,
            'impact_areas': impact_areas,
            'recommendations': recommendations,
            'sdg_alignment': self._map_to_sdgs(full_text),
            'success_factors': self._calculate_success_factors(matching_priorities, relevant_funding)
        }

        logger.info(f"Alignment score: {result['alignment_score']}")
        return result

    def _calculate_priority_match(self, research_text: str, priority: Dict) -> float:
        """Calculate how well research matches a priority"""
        score = 0.0

        # Check keywords
        for keyword in priority['keywords']:
            if keyword.lower() in research_text:
                score += 0.2

        # Check description
        priority_text = priority['description'].lower()
        common_words = set(research_text.split()) & set(priority_text.split())
        if len(common_words) > 5:
            score += 0.3

        # Check focus areas
        for area in priority.get('focus_areas', []):
            if area.lower() in research_text:
                score += 0.15

        return min(score, 1.0)

    def _find_relevant_funding(
        self,
        research_text: str,
        priorities: List[Dict]
    ) -> List[Dict]:
        """Find relevant funding schemes"""
        relevant = []

        for scheme in self.funding_schemes:
            # Match based on keywords
            match_score = 0.0
            for keyword in scheme['keywords']:
                if keyword.lower() in research_text:
                    match_score += 0.2

            # Boost if matches priority
            for priority in priorities[:3]:
                if priority['department'] == scheme['department']:
                    match_score += 0.3

            if match_score > 0.4:
                relevant.append({
                    **scheme,
                    'relevance_score': min(match_score, 1.0)
                })

        relevant.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant[:5]

    def _identify_impact_areas(
        self,
        research_text: str,
        priorities: List[Dict]
    ) -> Dict:
        """Identify districts and populations that could benefit"""
        impact_areas = {
            'districts': [],
            'beneficiaries': [],
            'sectors': []
        }

        # Identify relevant districts based on priority
        for priority in priorities[:3]:
            if 'target_districts' in priority:
                impact_areas['districts'].extend(priority['target_districts'])

        # Remove duplicates
        impact_areas['districts'] = list(set(impact_areas['districts']))

        # Identify beneficiary groups
        beneficiary_keywords = {
            'farmer': 'Small and Marginal Farmers',
            'agriculture': 'Agricultural Community',
            'student': 'Students',
            'women': 'Women',
            'rural': 'Rural Population',
            'water': 'Water-stressed Communities',
            'health': 'Healthcare Beneficiaries',
            'education': 'Educational Institutions'
        }

        for keyword, beneficiary in beneficiary_keywords.items():
            if keyword in research_text:
                impact_areas['beneficiaries'].append(beneficiary)

        # Identify sectors
        sector_keywords = {
            'agriculture': 'Agriculture',
            'water': 'Water Resources',
            'education': 'Education',
            'health': 'Healthcare',
            'energy': 'Renewable Energy',
            'environment': 'Environment',
            'technology': 'Technology',
            'infrastructure': 'Infrastructure'
        }

        for keyword, sector in sector_keywords.items():
            if keyword in research_text:
                impact_areas['sectors'].append(sector)

        return impact_areas

    def _generate_recommendations(
        self,
        priorities: List[Dict],
        funding: List[Dict],
        impact_areas: Dict
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if priorities:
            top_priority = priorities[0]
            recommendations.append(
                f"Align research with {top_priority['department']}'s {top_priority['name']} initiative"
            )

        if funding:
            top_funding = funding[0]
            recommendations.append(
                f"Apply for {top_funding['name']} (₹{top_funding['amount_range']})"
            )

        if impact_areas['districts']:
            recommendations.append(
                f"Conduct field studies in {', '.join(impact_areas['districts'][:3])} districts"
            )

        if len(priorities) > 1:
            recommendations.append(
                f"Consider collaboration with {priorities[1]['department']} for broader impact"
            )

        recommendations.append(
            "Integrate real-time data from AP government portals (data.ap.gov.in)"
        )

        recommendations.append(
            "Partner with relevant GDCs in target districts for implementation"
        )

        return recommendations

    def _calculate_overall_alignment(self, priorities: List[Dict]) -> float:
        """Calculate overall alignment score"""
        if not priorities:
            return 0.0

        # Weighted average of top 3 matches
        top_scores = [p['match_score'] for p in priorities[:3]]
        weights = [0.5, 0.3, 0.2]

        score = sum(s * w for s, w in zip(top_scores, weights[:len(top_scores)]))
        return round(score * 100, 1)  # Convert to percentage

    def _map_to_sdgs(self, research_text: str) -> List[Dict]:
        """Map research to UN Sustainable Development Goals"""
        sdg_mappings = [
            {
                'number': 1,
                'name': 'No Poverty',
                'keywords': ['poverty', 'income', 'livelihood', 'employment']
            },
            {
                'number': 2,
                'name': 'Zero Hunger',
                'keywords': ['food', 'agriculture', 'nutrition', 'farming', 'crop']
            },
            {
                'number': 3,
                'name': 'Good Health and Well-being',
                'keywords': ['health', 'disease', 'medical', 'healthcare', 'medicine']
            },
            {
                'number': 4,
                'name': 'Quality Education',
                'keywords': ['education', 'learning', 'school', 'student', 'teaching']
            },
            {
                'number': 6,
                'name': 'Clean Water and Sanitation',
                'keywords': ['water', 'sanitation', 'irrigation', 'groundwater', 'fluoride']
            },
            {
                'number': 7,
                'name': 'Affordable and Clean Energy',
                'keywords': ['energy', 'solar', 'renewable', 'electricity', 'power']
            },
            {
                'number': 13,
                'name': 'Climate Action',
                'keywords': ['climate', 'carbon', 'emission', 'environment', 'sustainability']
            }
        ]

        aligned_sdgs = []
        for sdg in sdg_mappings:
            match_count = sum(1 for keyword in sdg['keywords'] if keyword in research_text)
            if match_count > 0:
                aligned_sdgs.append({
                    'sdg_number': sdg['number'],
                    'sdg_name': sdg['name'],
                    'relevance': min(match_count / len(sdg['keywords']), 1.0)
                })

        aligned_sdgs.sort(key=lambda x: x['relevance'], reverse=True)
        return aligned_sdgs[:3]

    def _calculate_success_factors(
        self,
        priorities: List[Dict],
        funding: List[Dict]
    ) -> List[Dict]:
        """Calculate success factors for the research"""
        factors = []

        if priorities:
            factors.append({
                'factor': 'Government Priority Alignment',
                'status': 'High' if priorities[0]['match_score'] > 0.7 else 'Medium',
                'icon': '✓'
            })

        if funding:
            factors.append({
                'factor': 'Funding Availability',
                'status': 'Available',
                'icon': '✓'
            })

        factors.append({
            'factor': 'Policy Impact Potential',
            'status': 'High' if len(priorities) > 2 else 'Medium',
            'icon': '✓' if len(priorities) > 2 else '○'
        })

        factors.append({
            'factor': 'Implementation Feasibility',
            'status': 'High',
            'icon': '✓'
        })

        return factors

    def _load_government_priorities(self) -> List[Dict]:
        """
        Load AP government priorities
        Based on actual AP government focus areas and budget 2024-25
        """
        return [
            {
                'name': 'Jagananna Thodu - Financial Support',
                'department': 'Rural Development',
                'description': 'Financial assistance to small vendors and entrepreneurs',
                'budget': '₹3,000 Cr',
                'priority': 'High',
                'keywords': ['livelihood', 'income', 'entrepreneurship', 'vendors', 'microfinance'],
                'focus_areas': ['Rural Employment', 'Self-employment', 'Economic Growth'],
                'target_districts': ['All Districts'],
                'website': 'https://navasakam.ap.gov.in'
            },
            {
                'name': 'Rythu Bharosa - Agricultural Support',
                'department': 'Agriculture',
                'description': 'Direct financial assistance to farmers',
                'budget': '₹18,000 Cr',
                'priority': 'Very High',
                'keywords': ['agriculture', 'farmer', 'crop', 'irrigation', 'farming'],
                'focus_areas': ['Agricultural Productivity', 'Farmer Income', 'Crop Insurance'],
                'target_districts': ['Krishna', 'Guntur', 'West Godavari', 'East Godavari'],
                'website': 'https://ap.gov.in'
            },
            {
                'name': 'Fluoride-Free Water Mission',
                'department': 'Water Resources',
                'description': 'Providing fluoride-free drinking water to affected areas',
                'budget': '₹500 Cr',
                'priority': 'High',
                'keywords': ['water', 'fluoride', 'drinking water', 'purification', 'groundwater'],
                'focus_areas': ['Public Health', 'Water Quality', 'Rural Water Supply'],
                'target_districts': ['Nellore', 'Prakasam', 'Anantapur'],
                'website': 'https://apwater.ap.gov.in'
            },
            {
                'name': 'Solar Power Adoption',
                'department': 'Renewable Energy',
                'description': 'Promoting solar energy in agriculture and rural areas',
                'budget': '₹1,200 Cr',
                'priority': 'High',
                'keywords': ['solar', 'energy', 'renewable', 'electricity', 'power', 'irrigation'],
                'focus_areas': ['Rural Electrification', 'Agricultural Energy', 'Climate Action'],
                'target_districts': ['Anantapur', 'Kurnool', 'Kadapa'],
                'website': 'https://apepdcl.in'
            },
            {
                'name': 'Digital Literacy Mission',
                'department': 'IT & Education',
                'description': 'Improving digital skills and computer literacy',
                'budget': '₹300 Cr',
                'priority': 'Medium',
                'keywords': ['digital', 'technology', 'computer', 'education', 'skill', 'training'],
                'focus_areas': ['Digital Education', 'Skill Development', 'Youth Employment'],
                'target_districts': ['All Districts'],
                'website': 'https://aphe.ap.gov.in'
            },
            {
                'name': 'Amma Vodi - Education Support',
                'department': 'Education',
                'description': 'Financial assistance for mothers to send children to school',
                'budget': '₹8,000 Cr',
                'priority': 'Very High',
                'keywords': ['education', 'school', 'children', 'learning', 'student', 'dropout'],
                'focus_areas': ['School Enrollment', 'Dropout Prevention', 'Girl Education'],
                'target_districts': ['All Districts'],
                'website': 'https://navasakam.ap.gov.in'
            },
            {
                'name': 'YSR Jalakala Scheme',
                'department': 'Water Resources & Agriculture',
                'description': 'Watershed development and water conservation',
                'budget': '₹2,000 Cr',
                'priority': 'High',
                'keywords': ['water conservation', 'watershed', 'rainwater', 'irrigation', 'groundwater'],
                'focus_areas': ['Water Conservation', 'Drought Mitigation', 'Sustainable Agriculture'],
                'target_districts': ['Rayalaseema districts', 'Prakasam'],
                'website': 'https://apwater.ap.gov.in'
            },
            {
                'name': 'AP Innovation Council',
                'department': 'IT & Innovation',
                'description': 'Supporting innovation, startups, and research',
                'budget': '₹100 Cr',
                'priority': 'Medium',
                'keywords': ['innovation', 'research', 'technology', 'startup', 'ict', 'ai', 'ml'],
                'focus_areas': ['Innovation', 'Research Support', 'Technology Adoption'],
                'target_districts': ['All Districts'],
                'website': 'https://innovation.ap.gov.in'
            }
        ]

    def _load_funding_schemes(self) -> List[Dict]:
        """Load available funding schemes"""
        return [
            {
                'name': 'AP State Innovation Cell Grant',
                'department': 'IT & Innovation',
                'amount_range': '₹5-10 lakhs',
                'eligibility': 'Faculty from GDCs and Universities',
                'application_cycle': 'Quarterly',
                'keywords': ['innovation', 'technology', 'research', 'prototype'],
                'website': 'https://innovation.ap.gov.in'
            },
            {
                'name': 'DST-SERB (Central)',
                'department': 'Department of Science & Technology',
                'amount_range': '₹15-40 lakhs',
                'eligibility': 'PhD holders, Faculty',
                'application_cycle': 'Continuous',
                'keywords': ['science', 'research', 'engineering', 'technology'],
                'website': 'https://www.serbonline.in'
            },
            {
                'name': 'AICTE Research Grant',
                'department': 'AICTE',
                'amount_range': '₹10-25 lakhs',
                'eligibility': 'Engineering college faculty',
                'application_cycle': 'Annual',
                'keywords': ['engineering', 'technology', 'innovation'],
                'website': 'https://www.aicte-india.org'
            },
            {
                'name': 'CSIR Research Grant',
                'department': 'CSIR',
                'amount_range': '₹20-50 lakhs',
                'eligibility': 'Scientists and researchers',
                'application_cycle': 'Biannual',
                'keywords': ['science', 'research', 'laboratory'],
                'website': 'https://www.csir.res.in'
            },
            {
                'name': 'AP Agriculture Department Grant',
                'department': 'Agriculture',
                'amount_range': '₹3-8 lakhs',
                'eligibility': 'Agricultural researchers',
                'application_cycle': 'Annual',
                'keywords': ['agriculture', 'farming', 'crop', 'irrigation'],
                'website': 'https://ap.gov.in'
            }
        ]

    def _load_district_data(self) -> Dict:
        """Load AP district demographic data"""
        return {
            'Anantapur': {
                'population': 4081148,
                'rural_population': 2956498,
                'literacy_rate': 64.28,
                'major_issues': ['Water scarcity', 'Drought', 'Migration'],
                'agriculture_dependent': 0.68
            },
            'Guntur': {
                'population': 4887813,
                'rural_population': 3267913,
                'literacy_rate': 67.40,
                'major_issues': ['Water quality', 'Agricultural modernization'],
                'agriculture_dependent': 0.62
            },
            'Nellore': {
                'population': 2966082,
                'rural_population': 2091582,
                'literacy_rate': 68.90,
                'major_issues': ['Fluoride in water', 'Coastal erosion'],
                'agriculture_dependent': 0.58
            },
            'Prakasam': {
                'population': 3392764,
                'rural_population': 2732764,
                'literacy_rate': 63.08,
                'major_issues': ['Fluoride contamination', 'Groundwater depletion'],
                'agriculture_dependent': 0.71
            }
        }

    def _load_sdg_mapping(self) -> List[Dict]:
        """Load UN Sustainable Development Goals mapping"""
        return [
            {
                'number': 1,
                'name': 'No Poverty',
                'description': 'End poverty in all its forms everywhere',
                'keywords': ['poverty', 'income', 'livelihood', 'employment']
            },
            {
                'number': 2,
                'name': 'Zero Hunger',
                'description': 'End hunger, achieve food security and improved nutrition',
                'keywords': ['food', 'agriculture', 'nutrition', 'farming', 'crop']
            },
            {
                'number': 3,
                'name': 'Good Health and Well-being',
                'description': 'Ensure healthy lives and promote well-being for all',
                'keywords': ['health', 'disease', 'medical', 'healthcare', 'medicine']
            },
            {
                'number': 4,
                'name': 'Quality Education',
                'description': 'Ensure inclusive and equitable quality education',
                'keywords': ['education', 'learning', 'school', 'student', 'teaching']
            },
            {
                'number': 6,
                'name': 'Clean Water and Sanitation',
                'description': 'Ensure availability and sustainable management of water',
                'keywords': ['water', 'sanitation', 'irrigation', 'groundwater', 'fluoride']
            },
            {
                'number': 7,
                'name': 'Affordable and Clean Energy',
                'description': 'Ensure access to affordable, reliable, sustainable energy',
                'keywords': ['energy', 'solar', 'renewable', 'electricity', 'power']
            },
            {
                'number': 13,
                'name': 'Climate Action',
                'description': 'Take urgent action to combat climate change',
                'keywords': ['climate', 'carbon', 'emission', 'environment', 'sustainability']
            }
        ]
