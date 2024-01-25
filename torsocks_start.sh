# Start tor daemon in background
echo "Starting tor daemon..."
tor &

echo "Starting bot..."
python -m aeza_assistant run
