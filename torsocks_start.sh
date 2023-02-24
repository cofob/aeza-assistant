# Start tor daemon in background
echo "Starting tor daemon..."
tor &

# Wait for tor to start
echo "Waiting for tor to start..."

# Endless loop, that checks if tor is running
while true; do
    # Check if tor is running (curl 8118 port)
    if curl -x socks5://localhost:9050 http://eth0.me 2>&1 | grep "Connection refused"; then
        # If not, wait 1 second and try again
        echo "Waiting for tor to start..."
        sleep 1
    else
        # If yes, break the loop
        echo "Tor is running!"
        break
    fi
done

python -m aeza_assistant run
