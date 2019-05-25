#!/bin/bash

finish() {
    # Fix ownership of output files
    user_id=$(stat -c '%u:%g' /data)
    chown -R ${user_id} /data
}

echo "Running python server"

python3 -m http.server 9000