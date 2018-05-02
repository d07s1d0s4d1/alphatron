ps -e --format "pid cmd" | grep manage.py | awk '{print $1}' | xargs kill
echo "Done"