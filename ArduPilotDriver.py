import time
import sys
import asyncio
import websockets
import json
import argparse

# This if is required because dronekit is not up to date for python 3.10
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)
import dronekit

def debug_GPS_vars():
    args = get_args()
    print("Waiting for connection to {}...".format(args.port))
    ardupilot = dronekit.connect(args.port, wait_ready=True, baud=args.baud)
    print("Connection established to {}!".format(args.port))

    while True:
        time.sleep(1)
        lat = ardupilot.location.global_frame.lat
        lon = ardupilot.location.global_frame.lon
        roll = ardupilot.attitude.roll
        pitch = ardupilot.attitude.pitch
        yaw = ardupilot.heading
        print("lat: {}, lon: {}, roll: {}, pitch: {}, yaw: {}"
              .format(lat, lon, roll, pitch, yaw))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("port", help="Serial port connected to ardupilot")
    parser.add_argument("-hz", "--frequency", type=float, default=0.2, help="Rate at which data is sent")
    parser.add_argument("-b", "--baud", default=57600, type=int, help="Baud rate of serial connection")
    parser.add_argument("--debug", action="store_true", help="Prints debug info to stdout")
    return parser.parse_args()

async def send_gps_message(websocket, lat, lon):
    msg = {
        "type": "gps",
        "lat": lat,
        "lon": lon
    }
    await websocket.send(json.dumps(msg))

async def send_orientation_message(websocket, roll, pitch, yaw):
    msg = {
        "type": "orientation",
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw
    }
    await websocket.send(json.dumps(msg))

async def send_heading_message(websocket, heading):
    msg = {
        "type": "heading",
        "heading": heading
    }
    await websocket.send(json.dumps(msg))

async def async_main():
    args = get_args()
    print("Waiting for ardupilot connection on port {}...".format(args.port))
    ardupilot = dronekit.connect(args.port, wait_ready=True, baud=args.baud)
    print("Connection established to ardupilot!")

    # From M8N documentation:
    # If unable to preform normal compass calibration "compass dance" for any reason,
    # set parameter COMPASS_ORIENT=6 (Yaw270) for proper compass orientation.
    ardupilot.parameters["COMPASS_ORIENT"] = 6

    async for websocket in websockets.connect("ws://localhost:3001/ardupilot"):
        try:
            while True:
                lat = ardupilot.location.global_frame.lat
                lon = ardupilot.location.global_frame.lon
                roll = ardupilot.attitude.roll
                pitch = ardupilot.attitude.pitch
                yaw = ardupilot.attitude.yaw
                heading = ardupilot.heading

                if args.debug:
                    print(f"lat={lat:.5f}, lon={lon:.5f}, roll={roll:.2f}, pitch={pitch:.2f}, yaw={yaw:.2f}, heading={heading:.2f}")

                await send_gps_message(websocket, lat, lon)
                await send_orientation_message(websocket, roll, pitch, yaw)
                await send_heading_message(websocket, heading)

                await asyncio.sleep(1./args.frequency)
        except websockets.ConnectionClosed:
            continue

def main():
    debug_GPS_vars()

if __name__ == "__main__":
    #asyncio.run(async_main())
    main()
