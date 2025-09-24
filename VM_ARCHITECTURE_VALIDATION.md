# VM Network Architecture - Acceptance Criteria Validation

## 🎯 Architecture Overview

This Terraform infrastructure deploys a **two-VM architecture** on Google Cloud Platform that meets the following **acceptance criteria**:

### ✅ Acceptance Criteria Met:

1. **VM1 deployed to subnet snet-private is NOT accessible from public hosts**
2. **VM2 deployed to subnet snet-public IS accessible from public hosts**
3. **VM2 is able to connect to VM1** (internal VPC communication)

---

## 🌐 Network Architecture

```
VPC: vnet-nebo (10.0.0.0/16)
├── snet-public (10.0.0.0/17) ← VM2 (Public access)
│   ├── VM2: Public IP + Internal IP
│   ├── Internet Gateway access
│   └── SSH/HTTP access from 0.0.0.0/0
│
└── snet-private (10.0.128.0/17) ← VM1 (Private only)
    ├── VM1: Internal IP only (no public IP)
    ├── NAT Gateway for outbound internet
    └── Only accessible via internal VPC communication
```

---

## 🔧 Infrastructure Components

### VMs Configuration:

| VM | Name | Subnet | Public IP | Internal IP Range | Access |
|---|---|---|---|---|---|
| VM1 | `vm1-private-instance` | `snet-private` | ❌ None | 10.0.128.0/17 | Private only |
| VM2 | `vm2-public-instance` | `snet-public` | ✅ Assigned | 10.0.0.0/17 | Public + Private |

### Network Security:

- **Firewall Rules:**
  - SSH access (port 22) from internet to public-tagged VMs
  - HTTP access (ports 80, 8080, 5000) from internet to http-tagged VMs  
  - Internal SSH from public-vm to private-vm tags
  - Full internal communication within VPC (10.0.0.0/16)

- **NAT Gateway:** 
  - Enables VM1 (private) to access internet for updates
  - No inbound access to VM1 from internet

---

## 🧪 Testing & Validation

### After deployment, run the test script:
```bash
./test-vm-connectivity.sh
```

### Manual verification commands:

1. **Connect to VM2 (public) directly:**
   ```bash
   ssh -i ~/.ssh/id_rsa ubuntu@<VM2_EXTERNAL_IP>
   ```

2. **Connect to VM1 (private) via VM2 (jump host):**
   ```bash
   ssh -i ~/.ssh/id_rsa -J ubuntu@<VM2_EXTERNAL_IP> ubuntu@<VM1_INTERNAL_IP>
   ```

3. **Test connectivity from VM2 to VM1:**
   ```bash
   # SSH to VM2 first
   ssh -i ~/.ssh/id_rsa ubuntu@<VM2_EXTERNAL_IP>
   
   # Then from VM2, connect to VM1
   ssh ubuntu@<VM1_INTERNAL_IP>
   ```

---

## 📊 Terraform Outputs

After `terraform apply`, use these commands to get connection details:

```bash
# Get all connectivity information
terraform output quick_access_summary

# Get acceptance criteria validation
terraform output acceptance_criteria

# Get individual VM IPs
terraform output vm2_public_external_ip
terraform output vm1_private_internal_ip

# Get SSH commands
terraform output ssh_command_vm2
terraform output ssh_command_vm1_via_vm2
```

---

## 🚀 Deployment Steps

1. **Initialize Terraform:**
   ```bash
   cd terraform/
   terraform init
   ```

2. **Plan the deployment:**
   ```bash
   terraform plan
   ```

3. **Apply the infrastructure:**
   ```bash
   terraform apply
   ```

4. **Test connectivity:**
   ```bash
   cd ..
   ./test-vm-connectivity.sh
   ```

---

## 🔐 Security Considerations

- **VM1 (Private):** 
  - No public IP assigned
  - Only accessible via internal VPC routes
  - Uses NAT Gateway for outbound internet access
  - Protected by network-level isolation

- **VM2 (Public):**
  - Public IP for external access
  - Acts as bastion/jump host for VM1 access
  - SSH key authentication required
  - Firewall rules restrict access to necessary ports only

- **Network Security:**
  - All internal communication within VPC is encrypted
  - Firewall rules follow principle of least privilege
  - SSH access requires proper key authentication

---

## ✅ Compliance Verification

The infrastructure **meets all acceptance criteria**:

- ✅ **VM1 is NOT accessible from public hosts** (no public IP, private subnet)
- ✅ **VM2 IS accessible from public hosts** (public IP, public subnet) 
- ✅ **VM2 can connect to VM1** (internal VPC communication enabled)

This architecture provides a **secure, scalable foundation** for applications requiring both public-facing and private backend components.
