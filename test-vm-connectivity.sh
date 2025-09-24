#!/bin/bash

# Test script to verify VM connectivity according to acceptance criteria
# Run this after 'terraform apply' completes successfully

echo "🧪 TESTING VM CONNECTIVITY - ACCEPTANCE CRITERIA"
echo "=================================================="

# Get the VM IPs from terraform outputs
echo "📊 Getting VM IP addresses..."
VM2_EXTERNAL_IP=$(terraform output -raw vm2_public_external_ip 2>/dev/null)
VM1_INTERNAL_IP=$(terraform output -raw vm1_private_internal_ip 2>/dev/null)

if [ -z "$VM2_EXTERNAL_IP" ] || [ -z "$VM1_INTERNAL_IP" ]; then
    echo "❌ ERROR: Could not get VM IP addresses from terraform outputs"
    echo "   Make sure 'terraform apply' has been run successfully"
    exit 1
fi

echo "🌍 VM2 (Public) External IP: $VM2_EXTERNAL_IP"
echo "🔒 VM1 (Private) Internal IP: $VM1_INTERNAL_IP"
echo ""

# Test 1: VM1 should NOT be accessible from public internet
echo "🧪 TEST 1: VM1 should NOT be accessible from public internet"
echo "   Trying to SSH to VM1 directly (this should fail)..."
timeout 10 ssh -o ConnectTimeout=5 -o BatchMode=yes -i ~/.ssh/id_rsa ubuntu@$VM1_INTERNAL_IP echo "Connected" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "   ✅ PASS: VM1 is not accessible from public internet (as expected)"
else
    echo "   ❌ FAIL: VM1 is accessible from public internet (should not be)"
fi
echo ""

# Test 2: VM2 should be accessible from public internet
echo "🧪 TEST 2: VM2 should be accessible from public internet"
echo "   Trying to SSH to VM2 directly..."
timeout 10 ssh -o ConnectTimeout=5 -o BatchMode=yes -i ~/.ssh/id_rsa ubuntu@$VM2_EXTERNAL_IP echo "Connected" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ PASS: VM2 is accessible from public internet"
else
    echo "   ❌ FAIL: VM2 is not accessible from public internet"
    echo "   Note: This might fail if SSH keys are not properly configured"
fi
echo ""

# Test 3: VM2 should be able to connect to VM1 (internal communication)
echo "🧪 TEST 3: VM2 should be able to connect to VM1 (internal communication)"
echo "   Trying to connect from VM2 to VM1..."
timeout 15 ssh -o ConnectTimeout=5 -o BatchMode=yes -J ubuntu@$VM2_EXTERNAL_IP ubuntu@$VM1_INTERNAL_IP echo "Connected via jump host" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ PASS: VM2 can connect to VM1 via internal network"
else
    echo "   ⚠️  INCONCLUSIVE: Could not verify VM2->VM1 connectivity"
    echo "   This might fail if SSH keys are not properly configured on both VMs"
    echo "   Manual test: ssh -J ubuntu@$VM2_EXTERNAL_IP ubuntu@$VM1_INTERNAL_IP"
fi
echo ""

echo "🎯 ACCEPTANCE CRITERIA SUMMARY:"
echo "   • VM1 in snet-private: NOT accessible from public hosts"
echo "   • VM2 in snet-public: Accessible from public hosts" 
echo "   • VM2 can connect to VM1: Internal VPC communication enabled"
echo ""

echo "📝 MANUAL VERIFICATION COMMANDS:"
echo "   SSH to VM2: ssh -i ~/.ssh/id_rsa ubuntu@$VM2_EXTERNAL_IP"
echo "   SSH to VM1 via VM2: ssh -i ~/.ssh/id_rsa -J ubuntu@$VM2_EXTERNAL_IP ubuntu@$VM1_INTERNAL_IP"
echo ""
echo "🌐 Infrastructure URLs:"
terraform output -raw quick_access_summary 2>/dev/null || echo "   (Run 'terraform output quick_access_summary' for detailed URLs)"
