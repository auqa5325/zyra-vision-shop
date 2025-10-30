#!/bin/bash

# Script to fix ENOSPC error by increasing file watcher limit
echo "Fixing file watcher limit..."

# Check current limit
echo "Current file watcher limit:"
cat /proc/sys/fs/inotify/max_user_watches

# Increase the limit temporarily
echo "Increasing file watcher limit to 524288..."
echo 524288 | sudo tee /proc/sys/fs/inotify/max_user_watches

# Verify the change
echo "New file watcher limit:"
cat /proc/sys/fs/inotify/max_user_watches

# Make it permanent by adding to sysctl.conf
echo "Making the change permanent..."
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf

echo "File watcher limit increased successfully!"
echo "You may need to restart your development server."
