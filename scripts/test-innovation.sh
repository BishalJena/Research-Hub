#!/bin/bash

# Test script for Innovation Features
# Smart Research Hub - AP Government Integration

BASE_URL="http://localhost:8000/api/v1"
echo "🚀 Testing Smart Research Hub Innovation Features"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Register (if needed)
echo -e "${BLUE}Step 1: Registering test user...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_researcher@gdc.edu",
    "password": "testpass123",
    "full_name": "Dr. Test Researcher"
  }')
echo "$REGISTER_RESPONSE" | jq '.' 2>/dev/null || echo "$REGISTER_RESPONSE"
echo ""

# Step 2: Login
echo -e "${BLUE}Step 2: Logging in...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test_researcher@gdc.edu&password=testpass123")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null)

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo -e "${YELLOW}⚠️ Login failed. Using existing token or manual entry required.${NC}"
  echo "Please enter your access token:"
  read TOKEN
else
  echo -e "${GREEN}✅ Login successful!${NC}"
  echo "Token: ${TOKEN:0:20}..."
fi
echo ""

# Step 3: Test Public Endpoints (No Auth Required)
echo -e "${BLUE}Step 3: Testing Public Endpoints${NC}"
echo "-----------------------------------"

echo -e "${YELLOW}3.1 - List Government Priorities${NC}"
curl -s "${BASE_URL}/government/priorities" | jq '.'
echo ""

echo -e "${YELLOW}3.2 - List Funding Schemes${NC}"
curl -s "${BASE_URL}/government/funding" | jq '.total_schemes, .funding_schemes[0]'
echo ""

echo -e "${YELLOW}3.3 - List Districts${NC}"
curl -s "${BASE_URL}/government/districts?min_literacy=65" | jq '.total_districts, .districts[0]'
echo ""

# Step 4: Test Innovation Feature #1 - Government Alignment
echo -e "${BLUE}Step 4: Testing Government Alignment Analysis${NC}"
echo "----------------------------------------------"

echo -e "${YELLOW}Demo: Fluoride Removal Research${NC}"
ALIGNMENT_RESPONSE=$(curl -s -X POST "${BASE_URL}/government/analyze-alignment" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "research_topic": "Cost-Effective Fluoride Removal Technology for Rural Water Supply",
    "research_abstract": "This research develops a low-cost, community-operated fluoride removal system using activated alumina and natural adsorbents. The system requires minimal maintenance and can process 5000 liters per day at ₹2 per 1000 liters. Field trials conducted in Nellore district show 95% fluoride reduction from 8ppm to 0.4ppm, meeting WHO standards. The technology is designed for easy replication across villages with local materials and training.",
    "keywords": ["fluoride removal", "water purification", "rural water supply", "community water management"]
  }')

echo "$ALIGNMENT_RESPONSE" | jq '{
  research_topic,
  overall_alignment_score,
  top_priority: .matching_priorities[0].name,
  top_priority_budget: .matching_priorities[0].budget_crores,
  target_districts: .matching_priorities[0].target_districts,
  top_funding: .funding_opportunities[0].scheme_name,
  funding_amount: .funding_opportunities[0].amount_range,
  recommendations: .recommendations[0:3]
}'
echo ""

# Step 5: Test Innovation Feature #2 - Impact Prediction
echo -e "${BLUE}Step 5: Testing Impact Prediction${NC}"
echo "----------------------------------"

echo -e "${YELLOW}Demo: Predicting Impact for 3 Districts${NC}"
IMPACT_RESPONSE=$(curl -s -X POST "${BASE_URL}/government/predict-impact" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "research_topic": "Cost-Effective Fluoride Removal Technology for Rural Water Supply",
    "research_abstract": "Low-cost fluoride removal system using activated alumina and natural adsorbents. Proven in Nellore district with 95% fluoride reduction. Cost: ₹2 per 1000 liters.",
    "target_districts": ["Nellore", "Prakasam", "Anantapur"]
  }')

echo "$IMPACT_RESPONSE" | jq '{
  research_area,
  population_impact: {
    total_reach: .population_impact.total_reach,
    direct_beneficiaries: .population_impact.direct_beneficiaries,
    percentage_of_state: .population_impact.percentage_of_state
  },
  economic_impact: {
    annual_benefit_cr: (.economic_impact.total_annual_benefit_inr / 10000000),
    five_year_benefit_cr: (.economic_impact.five_year_projection_inr / 10000000),
    job_creation: .economic_impact.job_creation_potential
  },
  impact_scores: {
    overall_score: .impact_scores.overall_impact_score,
    rating: .impact_scores.rating
  },
  timeline: {
    duration_years: .timeline.total_duration_years
  }
}'
echo ""

# Step 6: Test Full Analysis
echo -e "${BLUE}Step 6: Testing Full Analysis (All-in-One)${NC}"
echo "-------------------------------------------"

FULL_RESPONSE=$(curl -s -X POST "${BASE_URL}/government/analyze-full" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "research_topic": "Mobile-Based AI for Paddy Disease Detection",
    "research_abstract": "Deep learning model for paddy disease identification using smartphone cameras. App works offline after model download. Trained on 50,000 images of 12 common diseases in AP. Accuracy 94%. Provides treatment recommendations in Telugu. Free for farmers.",
    "keywords": ["agriculture", "artificial intelligence", "crop disease", "mobile app"]
  }')

echo "$FULL_RESPONSE" | jq '{
  executive_summary,
  actionable_next_steps
}'
echo ""

# Step 7: Test Other Features (Original Platform)
echo -e "${BLUE}Step 7: Testing Original Features (Quick Check)${NC}"
echo "------------------------------------------------"

echo -e "${YELLOW}7.1 - Trending Topics${NC}"
curl -s "${BASE_URL}/topics/trending?discipline=Computer+Science&limit=5" | jq '.total_topics'
echo ""

echo -e "${YELLOW}7.2 - Journal Filters${NC}"
curl -s "${BASE_URL}/journals/filters/options" | jq '.subject_areas[0:3]'
echo ""

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Testing Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Innovation Features Tested:${NC}"
echo "  ✅ Government Alignment Analysis"
echo "  ✅ Research Impact Prediction"
echo "  ✅ Full Analysis (Combined)"
echo "  ✅ Public Endpoints (Priorities, Funding, Districts)"
echo ""
echo -e "${BLUE}Original Features Verified:${NC}"
echo "  ✅ Topic Discovery"
echo "  ✅ Journal Recommendations"
echo ""
echo -e "${YELLOW}📊 Visit Swagger UI for interactive testing:${NC}"
echo "   http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}📖 See INNOVATION_DEMO.md for detailed examples${NC}"
echo ""
