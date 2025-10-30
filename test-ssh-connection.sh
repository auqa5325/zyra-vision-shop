#!/bin/bash

# Script to test SSH connectivity to EC2 instance
# Usage: ./test-ssh-connection.sh

HOST="ec2-3-110-143-60.ap-south-1.compute.amazonaws.com"
KEY="pda-mit.pem"
USER="ec2-user"

echo "Testing connectivity to $HOST..."
echo ""

# Test 1: DNS Resolution
echo "1. Testing DNS resolution..."
if host "$HOST" > /dev/null 2>&1; then
    echo "   ✓ DNS resolves: $(host $HOST | grep -oP 'has address \K[^\s]+')"
else
    echo "   ✗ DNS resolution failed"
    exit 1
fi

echo ""

# Test 2: Ping Test
echo "2. Testing ICMP connectivity (may timeout if ICMP is blocked, which is normal)..."
if ping -c 2 -W 2 "$HOST" > /dev/null 2>&1; then
    echo "   ✓ Ping successful"
else
    echo "   ⚠ Ping failed (this is often normal - ICMP may be blocked by security group)"
fi

echo ""

# Test 3: Port 22 Test
echo "3. Testing SSH port 22..."
if command -v nc > /dev/null 2>&1; then
    if nc -z -w 5 "$HOST" 22 > /dev/null 2>&1; then
        echo "   ✓ Port 22 is open"
    else
        echo "   ✗ Port 22 is not accessible (check security group rules)"
    fi
else
    echo "   ⚠ netcat (nc) not available, skipping port test"
fi

echo ""

# Test 4: SSH Connection Test
echo "4. Testing SSH connection..."
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no -i "$KEY" "$USER@$HOST" "echo 'SSH connection successful!'" 2>&1

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "   ✓ SSH connection successful!"
else
    echo ""
    echo "   ✗ SSH connection failed (exit code: $EXIT_CODE)"
    echo ""
    echo "   Troubleshooting steps:"
    echo "   1. Check AWS Console → EC2 → Instances → Your instance is 'running'"
    echo "   2. Check AWS Console → EC2 → Security Groups → Inbound rule for SSH (port 22) from your IP"
    echo "   3. Verify the key file permissions: chmod 400 $KEY"
    echo "   4. Check your current IP: curl -s ifconfig.me"
fi

