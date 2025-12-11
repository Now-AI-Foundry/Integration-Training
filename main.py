from fastapi import FastAPI, Header, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uvicorn

app = FastAPI(
    title="ServiceNow Integration Training API",
    description="Practice API for ServiceNow solution consultants to build custom integrations",
    version="1.2.0",
    servers=[
        {
            "url": "https://integration-training.sliplane.app",
            "description": "Production server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        }
    ]
)

# Valid API keys for authentication (in production, store these securely)
VALID_API_KEYS = {
    "training-key-001": "Training User 1",
    "training-key-002": "Training User 2",
    "demo-api-key-123": "Demo User"
}

# Mock data storage
mock_records = [
    {
        "id": "REC001",
        "name": "Enterprise Software License",
        "category": "Software",
        "status": "Active",
        "value": 15000.00,
        "created_date": "2024-01-15",
        "owner": "IT Department",
        "description": "Annual enterprise software license renewal"
    },
    {
        "id": "REC002",
        "name": "Cloud Infrastructure Services",
        "category": "Services",
        "status": "Active",
        "value": 8500.00,
        "created_date": "2024-02-20",
        "owner": "DevOps Team",
        "description": "Monthly cloud hosting and infrastructure services"
    },
    {
        "id": "REC003",
        "name": "Security Audit Q1",
        "category": "Compliance",
        "status": "Completed",
        "value": 12000.00,
        "created_date": "2024-03-10",
        "owner": "Security Team",
        "description": "Quarterly security audit and compliance review"
    },
    {
        "id": "REC004",
        "name": "Training Program 2024",
        "category": "Training",
        "status": "In Progress",
        "value": 5000.00,
        "created_date": "2024-04-05",
        "owner": "HR Department",
        "description": "Employee training and development program"
    },
    {
        "id": "REC005",
        "name": "Office Equipment Upgrade",
        "category": "Hardware",
        "status": "Pending",
        "value": 25000.00,
        "created_date": "2024-05-12",
        "owner": "Facilities",
        "description": "Office workstation and equipment upgrade project"
    }
]

# Pydantic models for request/response validation
class BusinessRecord(BaseModel):
    id: str
    name: str
    category: str
    status: str
    value: float
    created_date: str
    owner: str
    description: str

class CreateRecordRequest(BaseModel):
    name: str = Field(..., description="Name of the record")
    category: str = Field(..., description="Category of the record")
    value: float = Field(..., description="Monetary value")
    owner: str = Field(..., description="Owner or responsible party")
    description: Optional[str] = Field("", description="Detailed description")

class CreateRecordResponse(BaseModel):
    success: bool
    message: str
    record: BusinessRecord

class SummaryResponse(BaseModel):
    total_records: int
    total_value: float
    average_value: float
    status_breakdown: dict
    category_breakdown: dict
    most_valuable_record: BusinessRecord
    latest_record: BusinessRecord

# Authentication dependency
def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None)
):
    """
    Verify the API key provided in either:
    1. X-API-Key header, OR
    2. Authorization: Bearer <token> header

    ServiceNow consultants can use either authentication method.
    """
    api_key = None

    # Check X-API-Key header first
    if x_api_key:
        api_key = x_api_key
    # If not found, check Authorization Bearer token
    elif authorization:
        # Parse "Bearer <token>" format
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            api_key = parts[1]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format. Use 'Bearer <token>'"
            )

    # If no authentication provided
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide either X-API-Key header or Authorization: Bearer <token>"
        )

    # Validate the API key
    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key or Bearer token."
        )

    return VALID_API_KEYS[api_key]

@app.get("/")
def root():
    """Welcome endpoint with API information"""
    return {
        "message": "Welcome to ServiceNow Integration Training API",
        "documentation": "/docs",
        "endpoints": {
            "GET /records": "Retrieve all business records (returns array)",
            "GET /records/{record_id}": "Retrieve a specific record by ID",
            "GET /summary": "Retrieve summary statistics (returns single object)",
            "POST /records": "Create a new business record"
        },
        "authentication": "Include X-API-Key header OR Authorization: Bearer <token>",
        "valid_api_keys": list(VALID_API_KEYS.keys())
    }

@app.get("/records", response_model=List[BusinessRecord])
def get_records(user: str = Depends(verify_api_key)):
    """
    GET endpoint that returns an array of business records.

    **Authentication Required**: Use one of these methods:
    - X-API-Key header: `X-API-Key: training-key-001`
    - Authorization Bearer: `Authorization: Bearer training-key-001`

    **Example for ServiceNow REST Message:**
    - Endpoint: GET {endpoint}/records
    - HTTP Headers: X-API-Key: training-key-001
      OR Authorization: Bearer training-key-001
    """
    return mock_records

@app.get("/records/{record_id}", response_model=BusinessRecord)
def get_record_by_id(
    record_id: str,
    user: str = Depends(verify_api_key)
):
    """
    GET endpoint to retrieve a specific record by ID.

    **Authentication Required**: Use X-API-Key header or Authorization: Bearer <token>
    """
    for record in mock_records:
        if record["id"] == record_id:
            return record

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Record with ID '{record_id}' not found"
    )

@app.post("/records", response_model=CreateRecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    record: CreateRecordRequest,
    user: str = Depends(verify_api_key)
):
    """
    POST endpoint to create a new business record.

    **Authentication Required**: Use X-API-Key header or Authorization: Bearer <token>

    **Example for ServiceNow REST Message:**
    - Endpoint: POST {endpoint}/records
    - HTTP Headers:
        - X-API-Key: training-key-001 (OR Authorization: Bearer training-key-001)
        - Content-Type: application/json
    - Request Body:
    ```json
    {
        "name": "New Project",
        "category": "Projects",
        "value": 10000.00,
        "owner": "Project Team",
        "description": "New project description"
    }
    ```
    """

    # Generate new ID
    new_id = f"REC{str(len(mock_records) + 1).zfill(3)}"

    # Create new record
    new_record = {
        "id": new_id,
        "name": record.name,
        "category": record.category,
        "status": "Pending",  # Default status for new records
        "value": record.value,
        "created_date": datetime.now().strftime("%Y-%m-%d"),
        "owner": record.owner,
        "description": record.description or ""
    }

    # Add to mock storage
    mock_records.append(new_record)

    return {
        "success": True,
        "message": f"Record '{new_record['name']}' created successfully",
        "record": new_record
    }

@app.get("/summary", response_model=SummaryResponse)
def get_summary(user: str = Depends(verify_api_key)):
    """
    GET endpoint that returns a single summary object with statistics.

    **Authentication Required**: Use X-API-Key header or Authorization: Bearer <token>

    **Example for ServiceNow REST Message:**
    - Endpoint: GET {endpoint}/summary
    - HTTP Headers: X-API-Key: training-key-001
      OR Authorization: Bearer training-key-001

    **Use Case**: Display dashboard metrics or summary statistics in ServiceNow
    """
    # Calculate statistics
    total_records = len(mock_records)
    total_value = sum(record["value"] for record in mock_records)
    average_value = total_value / total_records if total_records > 0 else 0

    # Status breakdown
    status_breakdown = {}
    for record in mock_records:
        status = record["status"]
        status_breakdown[status] = status_breakdown.get(status, 0) + 1

    # Category breakdown
    category_breakdown = {}
    for record in mock_records:
        category = record["category"]
        category_breakdown[category] = category_breakdown.get(category, 0) + 1

    # Most valuable record
    most_valuable = max(mock_records, key=lambda x: x["value"]) if mock_records else None

    # Latest record (by date, then by ID as tiebreaker)
    latest = max(mock_records, key=lambda x: (x["created_date"], x["id"])) if mock_records else None

    return {
        "total_records": total_records,
        "total_value": total_value,
        "average_value": round(average_value, 2),
        "status_breakdown": status_breakdown,
        "category_breakdown": category_breakdown,
        "most_valuable_record": most_valuable,
        "latest_record": latest
    }

@app.get("/health")
def health_check():
    """Health check endpoint (no authentication required)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_records": len(mock_records)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
