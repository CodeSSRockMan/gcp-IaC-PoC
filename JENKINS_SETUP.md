# Jenkins Credentials Setup Guide

## 🔧 Required Jenkins Credentials

To run the Medical Appointments Infrastructure pipeline, you need to configure these credentials in Jenkins (`http://localhost:8080`):

### 1. **GCP Service Account Key** 📋
- **Credential ID:** `gcp-sa-key`
- **Type:** `Secret file`
- **File:** Your GCP service account JSON key file
- **Description:** `GCP Service Account for Terraform`

**To get your GCP Service Account JSON:**
```bash
# Create a service account
gcloud iam service-accounts create terraform-sa --display-name="Terraform Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding peaceful-oath-470112-e8 \
    --member="serviceAccount:terraform-sa@peaceful-oath-470112-e8.iam.gserviceaccount.com" \
    --role="roles/editor"

gcloud projects add-iam-policy-binding peaceful-oath-470112-e8 \
    --member="serviceAccount:terraform-sa@peaceful-oath-470112-e8.iam.gserviceaccount.com" \
    --role="roles/compute.admin"

gcloud projects add-iam-policy-binding peaceful-oath-470112-e8 \
    --member="serviceAccount:terraform-sa@peaceful-oath-470112-e8.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create and download the JSON key
gcloud iam service-accounts keys create ~/gcp-terraform-key.json \
    --iam-account=terraform-sa@peaceful-oath-470112-e8.iam.gserviceaccount.com
```

### 2. **SSH Public Key** 🔑
- **Credential ID:** `gcp-ssh-public-key`
- **Type:** `Secret text`
- **Secret:** Your Ed25519 public key content
- **Description:** `SSH Public Key for VM access`

**SSH Key Content:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH5/Fs0BhfbK6MqZMNgA8aVKf1GR9jKeP1rYRtNm8gUQ gcp-medical-appointments-pramosba@PRAMOSBA-M-030J
```

---

## 🚀 Jenkins Pipeline Configuration

### **Step 1: Create Pipeline Job**
1. Go to Jenkins Dashboard (`http://localhost:8080`)
2. Click **"New Item"**
3. Enter name: `medical-appointments-infrastructure`
4. Select **"Pipeline"**
5. Click **"OK"**

### **Step 2: Configure Pipeline**
1. In the **Pipeline** section:
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** Your repository URL
   - **Branch:** `*/main`
   - **Script Path:** `Jenkinsfile`

### **Step 3: Add Build Parameters**
The pipeline includes these parameters:
- **ACTION:** `plan` | `apply` | `destroy`
- **AUTO_APPROVE:** Checkbox for auto-approval
- **RUN_TESTS:** Checkbox to run connectivity tests

---

## 🎯 Pipeline Stages

### **🔄 Checkout**
- Checks out the source code from Git

### **⚙️ Setup** 
- Validates environment and tools
- Shows configuration summary

### **🚀 Terraform Init**
- Initializes Terraform with providers and modules

### **✅ Terraform Validate**
- Validates configuration syntax
- Checks formatting

### **📋 Terraform Plan**
- Creates execution plan
- Shows what will be deployed:
  - VM1 (Private): snet-private (10.0.128.0/17)
  - VM2 (Public): snet-public (10.0.0.0/17)
  - VPC: vnet-nebo (10.0.0.0/16)

### **🚀 Terraform Apply** *(Conditional)*
- Deploys infrastructure
- Requires manual approval (unless AUTO_APPROVE is checked)
- Shows approval requester

### **🗑️ Terraform Destroy** *(Conditional)*
- Destroys all infrastructure
- Requires explicit confirmation
- Only runs when ACTION = 'destroy'

### **📊 Get Outputs**
- Shows acceptance criteria validation
- Displays connection information
- Shows network topology

### **🧪 Connectivity Tests** *(Optional)*
- Runs automated connectivity tests
- Tests VM accessibility according to acceptance criteria

---

## 📋 How to Run

### **Plan Only (Safe)**
1. Go to your Jenkins job
2. Click **"Build with Parameters"**
3. Set **ACTION** = `plan`
4. Click **"Build"**

### **Deploy Infrastructure**
1. Click **"Build with Parameters"**
2. Set **ACTION** = `apply`
3. Optionally check **AUTO_APPROVE** (not recommended for production)
4. Check **RUN_TESTS** if you want connectivity validation
5. Click **"Build"**
6. Approve when prompted

### **Destroy Infrastructure**
1. Click **"Build with Parameters"**
2. Set **ACTION** = `destroy`
3. Click **"Build"**
4. Confirm destruction when prompted

---

## ✅ Expected Results

After successful deployment, you'll see:

```
🎯 ACCEPTANCE CRITERIA VALIDATION:
✅ VM1 deployed to subnet snet-private is NOT accessible from public hosts
✅ VM2 deployed to subnet snet-public IS accessible from public hosts  
✅ VM2 is able to connect to VM1 (internal VPC communication)

🔗 Connection Information:
- VM2 External IP: <public-ip>
- VM1 Internal IP: <private-ip>
- SSH to VM2: ssh -i ~/.ssh/gcp_medical_appointments_ed25519 ubuntu@<vm2-ip>
- SSH to VM1 via VM2: ssh -J ubuntu@<vm2-ip> ubuntu@<vm1-ip>
```

## 🔧 Troubleshooting

### **Common Issues:**

1. **GCP Authentication Error**
   - Verify `gcp-sa-key` credential exists
   - Check service account permissions

2. **SSH Key Issues**
   - Verify `gcp-ssh-public-key` credential exists
   - Ensure SSH key format is correct

3. **Terraform State Issues**
   - Check if resources already exist
   - Verify project ID and region

4. **Permission Denied**
   - Ensure service account has required IAM roles
   - Check billing account access

## 📞 Support

If you encounter issues:
1. Check Jenkins build logs
2. Verify all credentials are properly configured
3. Ensure GCP project has necessary APIs enabled:
   - Compute Engine API
   - Cloud Resource Manager API
   - IAM API
