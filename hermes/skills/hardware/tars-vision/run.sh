# run.sh
#!/bin/bash
# Unix shell script to launch TARS Vision skill components on Linux/macOS
# Ensure you have a Python virtual environment activated before running.

# Activate virtual environment if present
if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
  echo "Virtual environment activated."
fi

# Start Face Server (Flask) in background
echo "Starting Face Server..."
python -u assets/face_server.py &

# Start Vision Router (gesture capture) in background
echo "Starting Vision Router..."
python -u assets/vision_router.py &

echo "TARS Vision skill initialized."
