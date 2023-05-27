# ardupilot-driver
Code for interacting with the ardupilot localization system

## Setup instructions

This assumes that python3 is installed on the system, and `python` refers to that.

1. Clone this repo and `cd` into it.
2. `python -m venv venv`
3. If bash shell, `source venv/bin/activate`. If windows cmd, `venv\Scripts\activate.bat`.
4. `pip install -r requirements.txt`

# Messages

gps_message
```
{
    "type": "gps",
    "lat": number,
    "lon": number
}
```

orientation_message
```
{
    "type": "orientation",
    "roll": number,
    "pitch": number,
    "yaw": number
}
```

heading_message
```
{
    "type": "heading",
    "heading": number
}
```
