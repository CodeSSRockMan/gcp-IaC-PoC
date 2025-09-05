# 🚀 Python App Deployment Guide

## Auto-scaling Infrastructure Overview

Your GCP infrastructure provides **automatic scaling** with the following capabilities:

### **Auto-scaling Features**
- **Scale to Zero**: Services automatically scale down to 0 instances when not in use (save costs)
- **Scale Up**: Automatically creates up to 10 instances based on traffic demand
- **Load Balancing**: GCP automatically distributes traffic across instances
- **Cost Efficient**: Pay only for actual CPU/memory usage, not idle time

### **Performance Specs per Instance**
- **CPU**: 1 vCPU per instance
- **Memory**: 512MB per instance
- **Concurrency**: Up to 100 concurrent requests per instance
- **Cold Start**: ~1-3 seconds for new instances to start

## 🎯 Deployment Options

### **Option 1: Direct Integration (Recommended)**

Add your Python code directly to `services/compute-service.py`:

```python
@app.route('/your-app-route')
def your_custom_app():
    """Your Python application logic"""
    # Example: Connect to database
    if gcp_available and db:
        data = db.collection('your_data').get()
    
    # Example: Process data
    result = process_your_data(data)
    
    # Return response
    return jsonify({'status': 'success', 'data': result})

def process_your_data(data):
    """Your custom processing logic"""
    # Add your business logic here
    return {"processed": True, "count": len(data)}
```

**Benefits:**
- ✅ Direct access to GCP resources (Firestore, Storage)
- ✅ Fastest performance (no proxy overhead)
- ✅ Full control over the environment

### **Option 2: External App Proxy**

Link to your existing Python app running elsewhere:

1. **Configure via Web Interface:**
   - Go to: `https://your-compute-service-url/load-app-form`
   - Enter your app URL: `https://your-external-app.com`
   - Click "Configure App"

2. **Configure via API:**
   ```bash
   curl -X POST "https://your-compute-service-url/load-app" \
     -H "Content-Type: application/json" \
     -d '{"app_url": "https://your-external-app.com", "type": "proxy"}'
   ```

3. **Access your external app:**
   - Direct: `https://your-compute-service-url/external-app`
   - Via Gateway: `https://your-entry-service-url/app/external-app`

**Benefits:**
- ✅ Keep existing app unchanged
- ✅ Easy to test and migrate
- ✅ Multiple app support

### **Option 3: Multiple Apps on Different Routes**

Host multiple Python applications on the same infrastructure:

```python
# Enable additional apps in compute-service.py
REGISTERED_APPS = {
    'my-app': {'enabled': True},           # /my-app
    'data-analytics': {'enabled': True},   # /analytics  
    'api-service': {'enabled': True}       # /api-v2
}

@app.route('/analytics')
def analytics_app():
    """Data analytics application"""
    # Your analytics code here
    return render_analytics_dashboard()

@app.route('/api-v2/<path:endpoint>')
def api_v2(endpoint):
    """API service application"""
    # Your API logic here
    return handle_api_request(endpoint)
```

## 🔧 Auto-scaling Configuration

### **Scaling Triggers**
The infrastructure automatically scales based on:
- **CPU Usage**: >80% utilization triggers new instances
- **Memory Usage**: >80% utilization triggers new instances  
- **Request Queue**: >10 pending requests triggers new instances
- **Response Time**: >1000ms average triggers new instances

### **Scaling Behavior**
```yaml
# Current Configuration (in terraform/modules/cloud_run/main.tf)
Min Instances: 0     # Scale to zero when idle
Max Instances: 10    # Up to 10 instances during high load
Concurrency: 100     # 100 requests per instance max
CPU: 1000m          # 1 vCPU per instance
Memory: 512Mi       # 512MB per instance
```

### **Modify Scaling (Optional)**
To change scaling limits, edit `terraform/modules/cloud_run/main.tf`:

```hcl
annotations = {
  "autoscaling.knative.dev/minScale" = "1"    # Keep 1 instance warm
  "autoscaling.knative.dev/maxScale" = "20"   # Allow up to 20 instances
}
```

## 📊 Monitoring Auto-scaling

### **Real-time Monitoring**
- **Service Status**: `https://your-entry-service-url/status`
- **Health Checks**: `https://your-compute-service-url/health`
- **Statistics**: `https://your-compute-service-url/stats`

### **GCP Console Monitoring**
1. Go to [GCP Console](https://console.cloud.google.com)
2. Navigate to **Cloud Run**
3. Select your service
4. View **Metrics** tab for:
   - Instance count over time
   - Request volume
   - CPU/Memory usage
   - Response times

### **Scaling Events Log**
Check scaling events in GCP Console > Logging:
```
resource.type="cloud_run_revision"
resource.labels.service_name="compute-service"
"scaled"
```

## 🚀 Deployment Steps

### **1. Deploy Infrastructure**
```bash
# Deploy with Jenkins
# OR manual deployment:
cd terraform
terraform init
terraform apply
```

### **2. Configure Services**
```bash
# Run Ansible configuration
ansible-playbook ansible/setup.yml -i ansible/inventory
```

### **3. Deploy Your App**
Choose your deployment option:

**Direct Integration:**
```bash
# Edit services/compute-service.py
# Add your routes and logic
# Redeploy with Jenkins or:
terraform apply  # This will update the Cloud Run service
```

**External App:**
```bash
# Use the web interface or API to configure
curl -X POST "https://your-compute-service-url/load-app" \
  -H "Content-Type: application/json" \
  -d '{"app_url": "https://your-app.com", "type": "proxy"}'
```

### **4. Access Your Application**
- **Main Gateway**: `https://your-entry-service-url`
- **Direct Access**: `https://your-compute-service-url`
- **App Management**: `https://your-compute-service-url/apps`
- **Your Custom App**: `https://your-compute-service-url/my-app`

## 💰 Cost Optimization

### **Free Tier Usage**
Your configuration is optimized for Google Cloud's free tier:
- **Cloud Run**: 2 million requests/month FREE
- **CPU Time**: 400,000 GB-seconds/month FREE
- **Memory**: 800,000 GB-seconds/month FREE
- **Auto-scaling to zero**: No charges when idle

### **Estimated Costs**
With moderate usage (1000 requests/day):
- **Monthly Cost**: ~$0-2 (likely FREE)
- **Scale-to-zero savings**: ~90% cost reduction
- **Budget Alert**: Set at $10/month with automatic monitoring

## 🎯 Best Practices

### **Performance**
- Keep **cold start times low** by minimizing dependencies
- Use **connection pooling** for database connections
- Implement **health checks** for faster scaling decisions

### **Cost Management**
- Let services **scale to zero** during low usage
- Monitor usage via **GCP Console**
- Use **budget alerts** to track costs

### **Development**
- Test locally first with `./test-local.sh`
- Use **staging environment** before production
- Monitor **scaling behavior** during load testing

## 🔗 Quick Links

- **App Management**: `/apps`
- **Configure External App**: `/load-app-form`
- **System Status**: `/status`
- **API Documentation**: `/api/docs`
- **Health Monitoring**: `/health`

Your auto-scaling Python infrastructure is ready! 🚀
