cd "$(dirname "$0")"

if !(tmux info &> /dev/null) && tmux has-session -t ardupilot &> /dev/null; then
    echo "Ardupilot session already exists, killing it and restarting!"
    tmux kill-session -t ardupilot
fi
tmux new -s ardupilot -d
tmux send -t ardupilot "./ArduPilotDriver.py$(printf \\r)"
