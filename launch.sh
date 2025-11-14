cd "$(dirname "$0")"

if !(tmux info &> /dev/null) && tmux has-session -t ardupilot &> /dev/null; then
    echo "Ardupilot session already exists, killing it and restarting!"
    tmux kill-session -t ardupilot
fi
echo "Starting new Ardupilot session"
sudo --validate
tmux new -s ardupilot -d
echo "Created new session, sending command"
tmux send -t ardupilot "./ArduPilotDriver.py$(printf \\r)"
echo "Command sent"
