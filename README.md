# Python App on GCP - OpenStack-equivalent Infrastructure

A complete serverless infrastructure solution on Google Cloud Platform that mimics OpenStack functionality, designed to serve Python applications with auto-scaling, security, and cost control.

## 🚀 What This Creates

**Your Python Application** served through a three-tier architecture:
- **Entry Service** (Gateway) - Public access point and load balancer  
- **API Service** (Controller) - Request validation and routing
- **Compute Service** (App Server) - Your actual Python application

## 🏗️ Architecture Overview

```
User Request → Entry Service → API Service → Compute Service (Your Python App)
                    ↓              ↓              ↓
                Load Balancer  Controller    Auto-scaling App Server
                   (8082)        (8081)         (8080)
```

### OpenStack Equivalents
- **Nova** (Compute) → Cloud Run services with auto-scaling
- **Swift** (Storage) → Google Cloud Storage bucket  
- **Keystone** (Identity) → IAM and service accounts
- **Neutron** (Network) → VPC with security groups
- **Horizon** (Dashboard) → Built-in web interface

## 📦 Components

### Infrastructure (Terraform)
- **VPC** with firewall rules for service isolation
- **Cloud Run** services for compute with auto-scaling (0-10 instances)
- **Cloud Storage** bucket for file storage
- **Firestore** database for application data
- **Budget** alerts and cost controls ($10 limit)

### Automation (Jenkins)
- **Linting** pipeline for code validation
- **Creation** pipeline for infrastructure deployment  
- **Destruction** pipeline with backup capabilities
- **Health Check** pipeline for monitoring

### Configuration (Ansible)
- **Service deployment** and configuration
- **Health validation** and connectivity testing
- **Application setup** with GCP resource binding

## 🎯 Your Python Application

The **Compute Service** serves your Python application with:

### ✨ Features
- **Web Interface** - Modern, responsive UI
- **Data Management** - Firestore integration for persistent storage
- **File Upload** - Cloud Storage integration  
- **Shell Access** - Secure command-line interface
- **API Endpoints** - RESTful API for programmatic access
- **Real-time Monitoring** - Health checks and statistics

### 📊 Built-in Pages
- **Main App** (`/`) - Your application dashboard
- **Data Management** (`/data`) - View and add data entries
- **File Upload** (`/upload`) - Upload files to Cloud Storage
- **Shell Interface** (`/shell`) - Execute safe system commands
- **Statistics** (`/stats`) - Application metrics and system info
- **API Documentation** (`/api/docs`) - Interactive API reference

## 🚀 Quick Start

### 1. Deploy Infrastructure
```bash
# Run the Jenkins pipeline or manual Terraform
cd terraform
terraform init
terraform plan
terraform apply
```

### 2. Configure Services
```bash
# Run Ansible playbook to configure and connect services
ansible-playbook ansible/setup.yml -i ansible/inventory
```

### 3. Access Your Application
- **Main App**: `https://your-entry-service-url/app`
- **Gateway**: `https://your-entry-service-url`
- **System Status**: `https://your-entry-service-url/status`
- **App Management**: `https://your-compute-service-url/apps`
- **Custom Apps**: `https://your-compute-service-url/my-app`
- **External Apps**: `https://your-compute-service-url/external-app`

### 4. Deploy Your Own Python App

You have **multiple options** to deploy your Python application:

#### **Option A: Direct Integration**
Add your code directly to `services/compute-service.py`:
```python
@app.route('/my-feature')
def my_feature():
    # Your Python logic here
    return jsonify({'message': 'Hello from my app!'})
```

#### **Option B: External App Link**
Link to your existing Python app:
1. Go to: `https://your-compute-service-url/load-app-form`
2. Enter your app URL
3. Access via: `https://your-compute-service-url/external-app`

#### **Option C: Use the Configuration Script**
```bash
# Edit the URL in the script
./configure-external-app.sh
```

## 🧪 Local Development

Test the services locally before deploying:

```bash
# Install dependencies
pip install flask requests google-cloud-firestore google-cloud-storage

# Run local test
./test-local.sh

# Access locally at:
# http://localhost:8082/app  (Your Python app)
# http://localhost:8082      (Gateway interface)
```

## 🛠️ Customization

### Adding Your Own Python Code

The **Compute Service** (`services/compute-service.py`) contains your Python application. You can:

1. **Add new routes** for your application features
2. **Integrate databases** - Firestore is already configured
3. **Handle file uploads** - Cloud Storage integration included
4. **Create APIs** - RESTful endpoints are ready
5. **Custom UI** - HTML templates with modern styling

### Example: Adding a New Feature

```python
@app.route('/my-feature')
def my_feature():
    # Your custom Python logic here
    data = {'message': 'Hello from your Python app!'}
    
    # Store in Firestore
    if gcp_available and db:
        db.collection('my_data').add(data)
    
    # Return custom HTML or JSON
    return jsonify(data)
```

## 🔧 Service Configuration

### Auto-scaling
- **Cloud Run** automatically scales from 0 to 10 instances
- **No Terraform changes needed** - scaling is handled by GCP
- **Cost-effective** - pay only for actual usage

### Security
- **VPC isolation** - each service in its own network
- **Firewall rules** - restrict access between services
- **IAM controls** - service accounts with minimal permissions

### Monitoring
- **Built-in health checks** on all services
- **Real-time status dashboard**
- **Ansible validation** of service connectivity

## 💰 Cost Control

- **$10 budget** with alerts and automatic monitoring
- **Free tier optimization** - designed to stay within GCP free limits
- **Auto-scaling** - services scale to zero when not in use

## 📁 Project Structure

```
gcp-IaC-PoC/
├── terraform/          # Infrastructure as Code
│   ├── main.tf         # Main Terraform configuration
│   ├── modules/        # Reusable modules (VPC, Cloud Run, Firestore)
│   └── terraform.tfvars.template
├── ansible/            # Service configuration
│   ├── setup.yml       # Deploy and configure services
│   └── health-check.yml
├── jenkins/            # CI/CD pipelines
│   ├── create-pipeline.groovy
│   ├── destroy-pipeline.groovy
│   └── health-check-pipeline.groovy
├── services/           # Your Python application
│   ├── compute-service.py  # Your main Python app
│   ├── api-service.py      # Controller/router
│   ├── entry-service.py    # Gateway/load balancer
│   └── requirements.txt
└── docs/              # Documentation
```

## 🎯 Use Cases

Perfect for:
- **Python web applications** with auto-scaling needs
- **Microservices architecture** development
- **OpenStack migration** to cloud-native solutions
- **Learning GCP** with practical, real-world examples
- **Cost-controlled development** environments

## 📚 Documentation

- [Architecture Details](docs/architecture.md)
- [Terraform Configuration](docs/terraform.md)  
- [Jenkins Pipelines](docs/jenkins.md)
- [Service Details](docs/services.md)

## 🎉 Ready to Deploy!

Your Python application infrastructure is ready with:
- ✅ Auto-scaling compute services
- ✅ Secure VPC networking
- ✅ Integrated GCP storage and database
- ✅ Automated deployment and monitoring
- ✅ Cost controls and budget alerts
- ✅ Modern web interface
- ✅ Built-in development tools

**Get started**: Run the Jenkins pipelines or use Terraform directly, then access your Python app through the gateway URL!
