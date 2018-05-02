#!/bin/bash
ps -e --format "pid cmd" | grep sender.py | awk '{print $1}' | xargs kill
#ps -e --format "pid cmd" | grep code_to_sending.py | awk '{print $1}' | xargs kill
echo "Done"
