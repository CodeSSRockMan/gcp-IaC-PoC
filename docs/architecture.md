# Service Architecture

## Communication Flow

```text
Internet → Entry Service (Load Balancer/Jumphost)
              ↓
          API Service (Controller)
              ↓
          Compute Service (Worker)
              ↓
        Storage/Firestore
```

## Service Roles

### Entry Service
- **Function**: Gateway, load balancer, jumphost
- **Features**: Web interface, shell access, request routing
- **Security**: Only public-facing service
- **Image**: Python with Flask/FastAPI

### API Service  
- **Function**: Controller and request validator
- **Features**: Request logging, authorization, resource management
- **Security**: Validates requests from Entry, controls Compute access
- **Image**: Python with business logic

### Compute Service
- **Function**: Workload execution
- **Features**: Data processing, HTML generation, database operations  
- **Security**: Only accessible via API service
- **Image**: Python with compute libraries

## Network Isolation
- Each service in separate VPC
- Firewall rules restrict communication
- Only API service can access storage/database
