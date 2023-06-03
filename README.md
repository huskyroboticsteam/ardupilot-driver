# ardupilot-driver
Code for interacting with the ardupilot localization system

## Setup instructions

This assumes that python3 is installed on the system.

1. Clone this repo and `cd` into it.
2. `python3 -m venv venv`
3. If bash shell, `source venv/bin/activate`. If windows cmd, `venv\Scripts\activate.bat`.
4. `pip install -r requirements.txt`

## Running instructions

### Run in current terminal

```bash
source venv/bin/activate
python ArduPilotDriver.py
```

On unix shells (e.g. bash) you can simply do:
```bash
./ArduPilotDriver.py
```

### Run in new terminal

Make sure `tmux` is installed, if not then `sudo apt install tmux`. Then:

```bash
./launch.sh
```

## Ardupilot Protocol

### GPS
```
{
    "type": "gps",
    "lat": number,
    "lon": number
}
```

### Orientation
```
{
    "type": "orientation",
    "roll": number,
    "pitch": number,
    "yaw": number
}
```

### Heading
```
{
    "type": "heading",
    "heading": number
}
```
