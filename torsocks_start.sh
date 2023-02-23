# Start tor daemon in background
echo "Starting tor daemon..."
tor &

# Wait for tor to start
echo "Waiting for tor to start... (sleep 60)"
sleep 60

# Start bot
echo "Starting bot..."
torsocks python -m aeza_assistant run

# Check if previous command was successful
if [ $? -eq 0 ]; then
    echo "Bot exited successfully."
else
    echo "Bot exited with error. Trying again... (sleep 120)"
    sleep 120
    torsocks python -m aeza_assistant run
fi