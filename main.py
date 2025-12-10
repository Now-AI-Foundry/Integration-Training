from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uvicorn

app = FastAPI(
    title="ServiceNow Integration Training API",
    description="Practice API for ServiceNow solution consultants to build custom integrations",
    version="1.0.0"
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

# Authentication dependency
def verify_api_key(x_api_key: str = Header(..., description="API Key for authentication")):
    """
    Verify the API key provided in the X-API-Key header.
    ServiceNow consultants should configure this in their REST Message.
    """
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key. Please check your X-API-Key header."
        )
    return VALID_API_KEYS[x_api_key]

@app.get("/")
def root():
    """Welcome endpoint with API information"""
    return {
        "message": "Welcome to ServiceNow Integration Training API",
        "documentation": "/docs",
        "endpoints": {
            "GET /records": "Retrieve all business records",
            "GET /records/{record_id}": "Retrieve a specific record by ID",
            "POST /records": "Create a new business record"
        },
        "authentication": "Include X-API-Key header with your requests",
        "valid_api_keys": list(VALID_API_KEYS.keys())
    }

@app.get("/records", response_model=List[BusinessRecord])
def get_records(user: str = Header(..., alias="X-API-Key", description="API Key", include_in_schema=False)):
    """
    GET endpoint that returns an array of business records.

    **Authentication Required**: Include X-API-Key header

    **Example for ServiceNow REST Message:**
    - Endpoint: GET {endpoint}/records
    - HTTP Headers: X-API-Key: training-key-001
    """
    verify_api_key(user)
    return mock_records

@app.get("/records/{record_id}", response_model=BusinessRecord)
def get_record_by_id(
    record_id: str,
    user: str = Header(..., alias="X-API-Key", description="API Key", include_in_schema=False)
):
    """
    GET endpoint to retrieve a specific record by ID.

    **Authentication Required**: Include X-API-Key header
    """
    verify_api_key(user)

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
    user: str = Header(..., alias="X-API-Key", description="API Key", include_in_schema=False)
):
    """
    POST endpoint to create a new business record.

    **Authentication Required**: Include X-API-Key header

    **Example for ServiceNow REST Message:**
    - Endpoint: POST {endpoint}/records
    - HTTP Headers:
        - X-API-Key: training-key-001
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
    verify_api_key(user)

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
