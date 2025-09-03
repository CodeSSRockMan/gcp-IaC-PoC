# Services Documentation

## Service Implementation

Each service is a Python Flask application that implements OpenStack-equivalent functionality:

### Entry Service (`entry-service.py`)
- **Port**: 8080
- **Role**: Gateway/jumphost with web interface
- **Features**: Command execution, API proxying, load balancing
- **Dependencies**: Flask, requests

### API Service (`api-service.py`)  
- **Port**: 8080
- **Role**: Controller and request validator
- **Features**: Request logging, authorization, compute service management
- **Dependencies**: Flask, requests

### Compute Service (`compute-service.py`)
- **Port**: 8080  
- **Role**: Worker for actual operations
- **Features**: Command execution, storage/database operations, content generation
- **Dependencies**: Flask, google-cloud-firestore, google-cloud-storage

## Container Deployment

Each service runs in Cloud Run with environment variables:
- `API_ENDPOINT`: URL of API service
- `COMPUTE_ENDPOINT`: URL of compute service  
- `STORAGE_BUCKET`: Cloud Storage bucket name

## Security Model

- Entry service: Public internet access
- API service: Only accessible from entry service
- Compute service: Only accessible from API service
- All requests validated via `X-Forwarded-From` headers
