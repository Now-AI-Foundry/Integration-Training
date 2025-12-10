# ServiceNow Integration Training API

A practice API server for ServiceNow solution consultants to build and test custom REST integrations.

## Overview

This API provides realistic endpoints to practice:
- **API Key Authentication** - Learn to configure authentication headers in ServiceNow
- **GET Requests** - Retrieve and parse arrays of business records
- **POST Requests** - Send data to external systems
- **Error Handling** - Handle authentication failures and validation errors

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 3. Access API Documentation

Open your browser to:
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Docker Deployment

### Build and Run with Docker

**Build the Docker image**:
```bash
docker build -t servicenow-training-api .
```

**Run the container**:
```bash
docker run -d -p 8000:8000 --name training-api servicenow-training-api
```

**Stop the container**:
```bash
docker stop training-api
```

**Remove the container**:
```bash
docker rm training-api
```

### Docker Compose (Optional)

Create a `docker-compose.yml` file:
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
```

## API Key Authentication

All endpoints (except `/` and `/health`) require authentication. The API supports **two authentication methods**:

### Method 1: X-API-Key Header

**Header Name**: `X-API-Key`

```bash
curl -H "X-API-Key: training-key-001" http://localhost:8000/records
```

### Method 2: Authorization Bearer Token

**Header Format**: `Authorization: Bearer <token>`

```bash
curl -H "Authorization: Bearer training-key-001" http://localhost:8000/records
```

**Valid API Keys for Training**:
- `training-key-001`
- `training-key-002`
- `demo-api-key-123`

Both authentication methods accept the same keys and can be used interchangeably.

## Available Endpoints

### 1. GET /records

Returns an array of business records.

**Authentication** (choose one):
```
X-API-Key: training-key-001
```
OR
```
Authorization: Bearer training-key-001
```

**Response** (200 OK):
```json
[
  {
    "id": "REC001",
    "name": "Enterprise Software License",
    "category": "Software",
    "status": "Active",
    "value": 15000.0,
    "created_date": "2024-01-15",
    "owner": "IT Department",
    "description": "Annual enterprise software license renewal"
  }
]
```

### 2. GET /records/{record_id}

Retrieve a specific record by ID.

**Authentication** (choose one):
```
X-API-Key: training-key-001
```
OR
```
Authorization: Bearer training-key-001
```

**Example**: `GET /records/REC001`

**Response** (200 OK):
```json
{
  "id": "REC001",
  "name": "Enterprise Software License",
  "category": "Software",
  "status": "Active",
  "value": 15000.0,
  "created_date": "2024-01-15",
  "owner": "IT Department",
  "description": "Annual enterprise software license renewal"
}
```

### 3. POST /records

Create a new business record.

**Authentication** (choose one):
```
X-API-Key: training-key-001
Content-Type: application/json
```
OR
```
Authorization: Bearer training-key-001
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "New Project Initiative",
  "category": "Projects",
  "value": 50000.00,
  "owner": "Project Management Office",
  "description": "Q4 strategic project initiative"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Record 'New Project Initiative' created successfully",
  "record": {
    "id": "REC006",
    "name": "New Project Initiative",
    "category": "Projects",
    "status": "Pending",
    "value": 50000.0,
    "created_date": "2024-12-10",
    "owner": "Project Management Office",
    "description": "Q4 strategic project initiative"
  }
}
```

### 4. GET /health

Health check endpoint (no authentication required).

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-12-10T10:30:00",
  "total_records": 5
}
```

## ServiceNow Integration Guide

### Step 1: Create a REST Message

1. Navigate to **System Web Services > Outbound > REST Message**
2. Click **New**
3. Fill in:
   - **Name**: Training API Integration
   - **Endpoint**: `http://localhost:8000`
   - **Authentication**: None (we'll use custom headers)

### Step 2: Configure HTTP Headers

In the REST Message form, add HTTP Headers.

**Option A: Using X-API-Key**

| Name | Value |
|------|-------|
| X-API-Key | training-key-001 |
| Content-Type | application/json |

**Option B: Using Bearer Token**

| Name | Value |
|------|-------|
| Authorization | Bearer training-key-001 |
| Content-Type | application/json |

Choose either Option A or Option B (both work identically).

### Step 3: Create GET Method

1. In the REST Message, create a new **HTTP Method**
2. Configure:
   - **Name**: Get All Records
   - **HTTP method**: GET
   - **Endpoint**: `${endpoint}/records`
3. **Test** the method

### Step 4: Create POST Method

1. Create another **HTTP Method**
2. Configure:
   - **Name**: Create Record
   - **HTTP method**: POST
   - **Endpoint**: `${endpoint}/records`
3. Add **Content** (request body):
```json
{
  "name": "Test Record from ServiceNow",
  "category": "Integration Test",
  "value": 1000.00,
  "owner": "ServiceNow Admin",
  "description": "Testing POST integration"
}
```
4. **Test** the method

### Step 5: Parse Response in Script

Use the REST Message in a script:

```javascript
try {
    var r = new sn_ws.RESTMessageV2('Training API Integration', 'Get All Records');
    var response = r.execute();
    var httpStatus = response.getStatusCode();

    if (httpStatus == 200) {
        var responseBody = response.getBody();
        var records = JSON.parse(responseBody);

        gs.info('Retrieved ' + records.length + ' records');

        // Process each record
        for (var i = 0; i < records.length; i++) {
            var record = records[i];
            gs.info('Record: ' + record.id + ' - ' + record.name);
        }
    } else {
        gs.error('HTTP Error: ' + httpStatus);
    }
} catch (ex) {
    gs.error('Error calling API: ' + ex.message);
}
```

## Practice Exercises

### Exercise 1: Basic GET Integration
- Create a REST Message in ServiceNow
- Configure API Key authentication
- Retrieve all records and log them

### Exercise 2: Filter and Transform
- Retrieve all records
- Filter for records with status "Active"
- Create a GlideRecord in a custom table for each active record

### Exercise 3: POST Integration
- Create a ServiceNow Catalog Item
- On submission, POST data to the training API
- Display the response to the user

### Exercise 4: Error Handling
- Test with an invalid API key
- Handle authentication errors gracefully
- Implement retry logic for failed requests

### Exercise 5: Scheduled Integration
- Create a Scheduled Job
- Periodically fetch records from the API
- Update a ServiceNow table with the latest data

## Testing Without ServiceNow

### Using cURL

**GET Request with X-API-Key**:
```bash
curl -H "X-API-Key: training-key-001" http://localhost:8000/records
```

**GET Request with Bearer Token**:
```bash
curl -H "Authorization: Bearer training-key-001" http://localhost:8000/records
```

**POST Request with X-API-Key**:
```bash
curl -X POST http://localhost:8000/records \
  -H "X-API-Key: training-key-001" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Record",
    "category": "Testing",
    "value": 500.00,
    "owner": "Test User",
    "description": "Testing POST endpoint"
  }'
```

**POST Request with Bearer Token**:
```bash
curl -X POST http://localhost:8000/records \
  -H "Authorization: Bearer training-key-001" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Record",
    "category": "Testing",
    "value": 500.00,
    "owner": "Test User",
    "description": "Testing POST endpoint"
  }'
```

### Using Python

**Example 1: Using X-API-Key Header**
```python
import requests

headers = {
    "X-API-Key": "training-key-001"
}

# GET request
response = requests.get("http://localhost:8000/records", headers=headers)
print(response.json())

# POST request
new_record = {
    "name": "Python Test",
    "category": "API Testing",
    "value": 750.00,
    "owner": "API Tester",
    "description": "Created via Python"
}

response = requests.post(
    "http://localhost:8000/records",
    headers=headers,
    json=new_record
)
print(response.json())
```

**Example 2: Using Bearer Token**
```python
import requests

headers = {
    "Authorization": "Bearer training-key-001"
}

# GET request
response = requests.get("http://localhost:8000/records", headers=headers)
print(response.json())

# POST request
new_record = {
    "name": "Python Bearer Test",
    "category": "API Testing",
    "value": 850.00,
    "owner": "API Tester",
    "description": "Created via Python with Bearer token"
}

response = requests.post(
    "http://localhost:8000/records",
    headers=headers,
    json=new_record
)
print(response.json())
```

## Common Issues & Solutions

### Issue: Connection Refused
**Solution**: Ensure the API server is running (`python main.py`)

### Issue: 401 Unauthorized
**Solution**: Check that X-API-Key header is correctly configured with a valid key

### Issue: 422 Validation Error
**Solution**: Verify POST request body includes all required fields (name, category, value, owner)

## Additional Features

- **Auto-generated Documentation**: FastAPI provides interactive docs at `/docs`
- **Request Validation**: Pydantic models validate all incoming data
- **Mock Data Persistence**: Data persists during server runtime (resets on restart)
- **Realistic Response Codes**: Practice handling 200, 201, 401, 404, 422 responses

## Next Steps

1. Explore the interactive API documentation at `/docs`
2. Test all endpoints with different API keys
3. Practice error scenarios (invalid keys, missing fields)
4. Build your ServiceNow integration following the guide above
5. Extend the API with additional endpoints for more practice

## Support

For FastAPI documentation: https://fastapi.tiangolo.com/
For ServiceNow REST integration: https://docs.servicenow.com/
