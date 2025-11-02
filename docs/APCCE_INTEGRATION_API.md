# 🔗 APCCE Integration API Specification

**Document Version**: 1.0
**Last Updated**: November 3, 2025
**Status**: Ready for Implementation

---

## 📋 Overview

This document specifies the API endpoints that **Smart Research Hub provides to APCCE** for seamless integration with the APCCE portal (https://apcce.gov.in).

**Integration Direction**:
- ✅ **Smart Research Hub PROVIDES APIs**
- ✅ **APCCE CONSUMES our APIs**
- ❌ We do NOT consume APIs from APCCE (they don't provide APIs)

---

## 🎯 Integration Objectives

1. **Single Sign-On (SSO)**: APCCE users can access Smart Research Hub without separate login
2. **Profile Synchronization**: Researcher profiles from APCCE automatically sync
3. **Embedded Access**: APCCE can embed Research Hub features in their portal
4. **API Access**: APCCE backend can call our APIs for research features

---

## 🔐 Authentication Mechanisms

### Option 1: API Key Authentication (Simplest)

APCCE gets a master API key to authenticate all requests.

```http
GET /api/v1/researchers/12345/papers
Authorization: Bearer apcce_api_key_xyz123abc456
```

**Pros**: Simple, easy to implement
**Cons**: Single key for all users, less secure

### Option 2: JWT Token-Based SSO (Recommended)

APCCE generates signed JWT tokens for each user and passes to our platform.

```javascript
// APCCE Portal generates JWT
const token = jwt.sign({
  user_id: "12345",
  email: "researcher@college.edu",
  name: "Dr. Researcher",
  institution: "Government Degree College, Vijayawada",
  role: "faculty"
}, SHARED_SECRET, { expiresIn: '1h' });

// Redirect to Research Hub with token
window.location = `https://research-hub.apcce.gov.in/sso?token=${token}`;
```

**Pros**: Secure, per-user authentication
**Cons**: Requires shared secret management

### Option 3: OAuth 2.0 Flow (Most Secure)

Standard OAuth flow where APCCE acts as the identity provider.

**Pros**: Industry standard, most secure
**Cons**: More complex to implement

**Recommendation**: **Option 2 (JWT SSO)** for PoC, migrate to OAuth later.

---

## 🔌 Integration Patterns

### Pattern 1: iframe Embedding (Recommended for PoC)

APCCE embeds Research Hub features directly in their portal.

```html
<!-- In APCCE Portal -->
<iframe
  src="https://research-hub.apcce.gov.in/embed/topic-discovery?token=JWT_TOKEN"
  width="100%"
  height="600px"
  frameborder="0">
</iframe>
```

**Embeddable Modules**:
- Topic Discovery: `/embed/topic-discovery`
- Literature Review: `/embed/literature-review`
- Plagiarism Check: `/embed/plagiarism-check`
- Journal Recommendations: `/embed/journal-recommendations`

### Pattern 2: Deep Linking

APCCE provides links to Research Hub with automatic authentication.

```html
<!-- In APCCE Portal -->
<a href="https://research-hub.apcce.gov.in/sso?token=JWT_TOKEN&redirect=/dashboard">
  Access Research Hub
</a>
```

### Pattern 3: API Integration

APCCE backend calls our REST APIs directly.

```python
# APCCE Backend
import requests

response = requests.post(
    "https://api.research-hub.apcce.gov.in/v1/papers/summarize",
    headers={"Authorization": "Bearer APCCE_API_KEY"},
    json={
        "user_id": "12345",
        "pdf_url": "https://storage.apcce.gov.in/papers/paper123.pdf"
    }
)
summary = response.json()
```

---

## 📡 API Endpoints for APCCE Integration

### Base URL
```
Production: https://api.research-hub.apcce.gov.in/v1
Staging: https://staging-api.research-hub.apcce.gov.in/v1
```

---

### 1. Authentication & SSO

#### POST /api/v1/auth/sso
Authenticate user via SSO token from APCCE.

**Request**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "provider": "apcce"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "access_token": "research_hub_token_xyz",
    "refresh_token": "refresh_xyz",
    "user": {
      "id": "rh_12345",
      "apcce_id": "12345",
      "name": "Dr. Researcher",
      "email": "researcher@college.edu",
      "institution": "Government Degree College, Vijayawada",
      "role": "faculty"
    }
  }
}
```

---

#### GET /api/v1/auth/validate
Validate an existing token.

**Request**:
```http
GET /api/v1/auth/validate
Authorization: Bearer research_hub_token_xyz
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "valid": true,
    "user_id": "rh_12345",
    "expires_at": "2025-11-03T15:30:00Z"
  }
}
```

---

### 2. User Profile Management

#### POST /api/v1/users/sync
Sync or create user profile from APCCE data.

**Request**:
```json
{
  "apcce_id": "12345",
  "email": "researcher@college.edu",
  "name": "Dr. Researcher",
  "institution": "Government Degree College, Vijayawada",
  "department": "Computer Science",
  "designation": "Assistant Professor",
  "research_interests": ["AI", "Machine Learning"]
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "user_id": "rh_12345",
    "synced_at": "2025-11-03T14:25:00Z",
    "created": false  // true if new user, false if updated
  }
}
```

---

#### GET /api/v1/users/{apcce_id}
Get user profile by APCCE ID.

**Response**:
```json
{
  "status": "success",
  "data": {
    "user_id": "rh_12345",
    "apcce_id": "12345",
    "name": "Dr. Researcher",
    "email": "researcher@college.edu",
    "institution": "Government Degree College, Vijayawada",
    "statistics": {
      "papers_uploaded": 15,
      "plagiarism_checks": 8,
      "journal_recommendations": 12
    }
  }
}
```

---

### 3. Research Features (for APCCE Backend Integration)

#### POST /api/v1/topics/discover
Get trending research topics for a user.

**Request**:
```json
{
  "apcce_id": "12345",
  "discipline": "Computer Science",
  "limit": 10
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "topics": [
      {
        "id": "topic_1",
        "title": "Large Language Models for Education",
        "description": "Application of LLMs in educational contexts",
        "relevance_score": 0.95,
        "trending_score": 0.88,
        "citation_velocity": 150,
        "recent_papers": 245
      }
      // ... more topics
    ]
  }
}
```

---

#### POST /api/v1/papers/upload
Upload a paper for analysis.

**Request** (multipart/form-data):
```
POST /api/v1/papers/upload
Authorization: Bearer APCCE_API_KEY
Content-Type: multipart/form-data

apcce_id: 12345
file: (binary PDF data)
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "paper_id": "paper_xyz",
    "filename": "research_paper.pdf",
    "status": "processing",
    "task_id": "task_abc123"
  }
}
```

---

#### POST /api/v1/papers/summarize
Summarize a paper (URL or upload).

**Request**:
```json
{
  "apcce_id": "12345",
  "paper_url": "https://storage.apcce.gov.in/papers/paper123.pdf"
  // OR
  // "paper_text": "Full text of the paper..."
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "paper_id": "paper_xyz",
    "summary": {
      "abstract": "This paper presents...",
      "key_findings": ["Finding 1", "Finding 2"],
      "methodology": "The authors used...",
      "conclusions": "The study concludes..."
    },
    "processing_time_ms": 450
  }
}
```

---

#### POST /api/v1/plagiarism/check
Check document for plagiarism.

**Request**:
```json
{
  "apcce_id": "12345",
  "text": "Text to check for plagiarism...",
  "language": "en"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "check_id": "check_xyz",
    "originality_score": 87.5,
    "total_matches": 3,
    "matches": [
      {
        "text": "Matched text segment",
        "source": "Source Paper Title",
        "source_url": "https://...",
        "similarity": 0.92,
        "type": "high_similarity"
      }
    ],
    "processing_time_ms": 1250
  }
}
```

---

#### POST /api/v1/journals/recommend
Get journal recommendations for a paper.

**Request**:
```json
{
  "apcce_id": "12345",
  "abstract": "Paper abstract...",
  "keywords": ["AI", "Education"],
  "preferences": {
    "open_access": true,
    "min_impact_factor": 2.0
  }
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "journal_id": "journal_1",
        "title": "IEEE Access",
        "publisher": "IEEE",
        "impact_factor": 3.47,
        "open_access": true,
        "fit_score": 0.92,
        "acceptance_probability": 0.65,
        "avg_time_to_publish_days": 60
      }
      // ... more journals
    ]
  }
}
```

---

### 4. Analytics & Reporting (for APCCE Dashboards)

#### GET /api/v1/analytics/institution/{institution_id}
Get analytics for an institution.

**Response**:
```json
{
  "status": "success",
  "data": {
    "institution_id": "gdc_vijayawada",
    "institution_name": "Government Degree College, Vijayawada",
    "statistics": {
      "total_users": 45,
      "active_users_30d": 32,
      "papers_analyzed": 127,
      "plagiarism_checks": 89,
      "journal_recommendations": 156
    },
    "top_research_areas": [
      {"area": "Computer Science", "count": 34},
      {"area": "Physics", "count": 28}
    ]
  }
}
```

---

#### GET /api/v1/analytics/user/{apcce_id}
Get analytics for a specific user.

**Response**:
```json
{
  "status": "success",
  "data": {
    "apcce_id": "12345",
    "activity_summary": {
      "papers_uploaded": 15,
      "plagiarism_checks": 8,
      "journal_recommendations": 12,
      "topics_explored": 25
    },
    "recent_activity": [
      {
        "action": "paper_upload",
        "timestamp": "2025-11-03T14:20:00Z",
        "details": "Uploaded 'AI in Education.pdf'"
      }
    ]
  }
}
```

---

### 5. Webhook Notifications (Optional)

APCCE can register webhook URLs to receive notifications.

#### POST /api/v1/webhooks/register
Register a webhook endpoint.

**Request**:
```json
{
  "url": "https://apcce.gov.in/api/webhooks/research-hub",
  "events": ["paper_processed", "plagiarism_check_complete"],
  "secret": "webhook_secret_xyz"
}
```

**Webhook Payload** (sent to APCCE):
```json
{
  "event": "plagiarism_check_complete",
  "timestamp": "2025-11-03T14:25:00Z",
  "data": {
    "apcce_id": "12345",
    "check_id": "check_xyz",
    "originality_score": 87.5
  },
  "signature": "hmac_signature_here"
}
```

---

## 🔒 Security Considerations

### 1. API Key Management
- APCCE receives a master API key
- Keys should be rotated every 90 days
- Rate limiting: 1000 requests/hour per key

### 2. JWT Token Security
- Shared secret should be 256-bit minimum
- Tokens expire after 1 hour
- Include signature verification

### 3. HTTPS Only
- All API calls must use HTTPS
- Reject HTTP requests

### 4. IP Whitelisting (Optional)
- Whitelist APCCE server IPs
- Reject requests from unknown sources

### 5. Request Validation
- Validate all input parameters
- Sanitize file uploads
- Check file size limits (10MB max)

---

## 📊 Rate Limits

| Endpoint | Rate Limit | Burst |
|----------|------------|-------|
| Authentication | 100/min | 200 |
| User Sync | 50/min | 100 |
| Topic Discovery | 30/min | 60 |
| Paper Upload | 10/min | 20 |
| Summarization | 20/min | 40 |
| Plagiarism Check | 10/min | 20 |
| Journal Recommendations | 30/min | 60 |
| Analytics | 100/min | 200 |

---

## 🧪 Testing & Sandbox

### Sandbox Environment
```
Base URL: https://sandbox-api.research-hub.apcce.gov.in/v1
API Key: sandbox_key_test123
```

### Test User
```json
{
  "apcce_id": "test_12345",
  "email": "test@example.com",
  "name": "Test Researcher"
}
```

### Sample cURL Commands

**Test SSO Authentication**:
```bash
curl -X POST https://sandbox-api.research-hub.apcce.gov.in/v1/auth/sso \
  -H "Content-Type: application/json" \
  -d '{
    "token": "TEST_JWT_TOKEN",
    "provider": "apcce"
  }'
```

**Test Topic Discovery**:
```bash
curl -X POST https://sandbox-api.research-hub.apcce.gov.in/v1/topics/discover \
  -H "Authorization: Bearer sandbox_key_test123" \
  -H "Content-Type: application/json" \
  -d '{
    "apcce_id": "test_12345",
    "discipline": "Computer Science",
    "limit": 5
  }'
```

---

## 📖 Integration Examples

### Example 1: APCCE Portal Button Integration

```html
<!-- In APCCE Portal -->
<button onclick="openResearchHub()">
  Analyze Research Paper
</button>

<script>
function openResearchHub() {
  // Generate JWT token on APCCE backend
  fetch('/api/generate-research-hub-token', {
    method: 'POST',
    body: JSON.stringify({
      user_id: currentUser.id
    })
  })
  .then(res => res.json())
  .then(data => {
    // Open Research Hub with SSO
    window.open(
      `https://research-hub.apcce.gov.in/sso?token=${data.token}&redirect=/plagiarism-check`,
      '_blank'
    );
  });
}
</script>
```

### Example 2: Embedded Module

```html
<!-- In APCCE Portal -->
<div class="research-hub-container">
  <h2>Topic Discovery</h2>
  <iframe
    id="research-hub-iframe"
    src=""
    style="width:100%; height:600px; border:none;">
  </iframe>
</div>

<script>
// Get token from APCCE backend
fetch('/api/generate-research-hub-token', { method: 'POST' })
  .then(res => res.json())
  .then(data => {
    document.getElementById('research-hub-iframe').src =
      `https://research-hub.apcce.gov.in/embed/topic-discovery?token=${data.token}`;
  });
</script>
```

### Example 3: Backend API Integration

```python
# APCCE Backend (Python/Django)
import requests
from django.conf import settings

def check_plagiarism(user_id, paper_text):
    """Call Research Hub API to check plagiarism"""

    response = requests.post(
        f"{settings.RESEARCH_HUB_API}/v1/plagiarism/check",
        headers={
            "Authorization": f"Bearer {settings.RESEARCH_HUB_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "apcce_id": user_id,
            "text": paper_text,
            "language": "en"
        }
    )

    if response.status_code == 200:
        result = response.json()
        return result['data']
    else:
        raise Exception(f"API Error: {response.status_code}")

# Usage
result = check_plagiarism("12345", "Paper text here...")
print(f"Originality Score: {result['originality_score']}%")
```

---

## 🚀 Deployment & Handover

### What We Provide to APCCE

1. **Production API Endpoint**: `https://api.research-hub.apcce.gov.in/v1`
2. **Master API Key**: Securely shared via encrypted channel
3. **JWT Shared Secret**: For SSO token generation
4. **API Documentation**: This document + Swagger UI
5. **SDK/Client Libraries**: Python, JavaScript (optional)
6. **Technical Support**: During integration period

### What We Need from APCCE

1. **User Data Format**: Confirmed JSON structure for user profiles
2. **Webhook Endpoints** (if using webhooks): URLs to send notifications
3. **IP Addresses**: For IP whitelisting (optional)
4. **Testing Timeline**: Dates for sandbox testing
5. **Go-Live Date**: Production launch date

---

## 📞 Support & Contact

**Technical Integration Support**:
- Email: integration@research-hub.apcce.gov.in
- Slack Channel: #apcce-integration
- Response Time: < 4 hours during business hours

**Emergency Contact**:
- Phone: +91-XXXX-XXXXXX
- Available: 9 AM - 6 PM IST

---

## 📝 Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 3, 2025 | Initial specification |

---

## ✅ Implementation Checklist

### For Research Hub Team
- [ ] Implement SSO endpoint (`/api/v1/auth/sso`)
- [ ] Implement user sync endpoint
- [ ] Set up API key authentication
- [ ] Configure rate limiting
- [ ] Deploy sandbox environment
- [ ] Generate API documentation (Swagger)
- [ ] Create test accounts
- [ ] Prepare handover documentation

### For APCCE Team
- [ ] Review API specification
- [ ] Decide on integration pattern (iframe/API/both)
- [ ] Set up JWT token generation (if using SSO)
- [ ] Configure API key storage
- [ ] Test sandbox endpoints
- [ ] Develop integration code
- [ ] User acceptance testing
- [ ] Production deployment

---

**Status**: Ready for APCCE integration team review
**Next Steps**: Schedule integration kickoff meeting

