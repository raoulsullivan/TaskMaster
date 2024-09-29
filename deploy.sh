#!/bin/bash

# Default destination directory on the remote machine
DEST_DIR="/var/www/taskmaster"

# Function to display script usage
usage() {
    echo "Usage: $0 <username@remote_host>"
    echo "This script will transfer the contents of the current directory to $DEST_DIR on the remote machine."
    echo "Example: $0 user@192.168.2.2"
    exit 1
}

TEMP_DIR="~/temp_transfer"

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    usage
fi

# Assign the argument to the remote host variable
REMOTE_HOST="$1"

# Get the current working directory (the source directory)
SOURCE_DIR="$(pwd)"

echo "Creating temp directory $TEMP_DIR on remote host"
ssh "$REMOTE_HOST" << EOF
  mkdir $TEMP_DIR
EOF

# Use scp to transfer the contents of the current directory recursively and preserve file attributes
echo "Transferring $SOURCE_DIR to $REMOTE_HOST:$TEMP_DIR..."

scp -r "$SOURCE_DIR"/* "$REMOTE_HOST:$TEMP_DIR"

# Check if the transfer was successful
if [ $? -eq 0 ]; then
    echo "Directory transfer to temp directory completed successfully."
else
    echo "Error: Failed to transfer the directory to temp directory."
    exit 1
fi

# Use ssh to run sudo commands on the remote host to move the files and set permissions
echo "Moving files to $DEST_DIR and setting permissions on the remote host..."

ssh "$REMOTE_HOST" << EOF
  sudo mkdir -p $DEST_DIR
  sudo cp -r $TEMP_DIR/* $DEST_DIR
  sudo chown -R www-data:www-data $DEST_DIR
  sudo chmod -R 755 $DEST_DIR
  rm -r $TEMP_DIR
EOF

# Check if the move and permissions change were successful
if [ $? -eq 0 ]; then
    echo "Files moved to $DEST_DIR and permissions set successfully."
else
    echo "Error: Failed to move files or set permissions."
    exit 1
fi
