#!venv/bin/python
import atexit
import time
import sys
import asyncio
import websockets
import json
import argparse
import math

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
        roll = ardupilot.attitude.roll + 0
        pitch = ardupilot.attitude.pitch + 0
        yaw = ardupilot.heading + 0
        print("lat: {}, lon: {}, roll: {}, pitch: {}, yaw: {}"
              .format(lat, lon, roll, pitch, yaw))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", default="/dev/ttyACM10",
                        help="Serial port connected to ardupilot")
    parser.add_argument("-hz", "--frequency", type=float,
                        default=10.0, help="Rate at which data is sent")
    parser.add_argument("-b", "--baud", default=57600,
                        type=int, help="Baud rate of serial connection")
    parser.add_argument("--debug", action="store_true",
                        help="Prints debug info to stdout")
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


async def async_main():
    args = get_args()
    print("Waiting for ardupilot connection on port {}...".format(args.port))
    ardupilot = dronekit.connect(args.port, wait_ready=True, baud=args.baud)
    print("Connection established to ardupilot!")

    def cleanup():
        print("Exiting!")
        ardupilot.close()
    atexit.register(cleanup)

    curr_time = time.perf_counter()
    last_data_send_times = {
        "gps": curr_time,
        "orientation": curr_time,
        "heading": curr_time
    }

    # From M8N documentation:
    # If unable to preform normal compass calibration "compass dance" for any reason,
    # set parameter COMPASS_ORIENT=6 (Yaw270) for proper compass orientation.
    ardupilot.parameters["COMPASS_ORIENT"] = 6

    print("Connecting to rover server...")
    while True:
        try:
            async with websockets.connect("ws://localhost:3001/ardupilot") as websocket:
                print("Done!")

                def gps_callback(self, _, frame):
                    curr_time = time.perf_counter()
                    if curr_time >= last_data_send_times["gps"] + 1./args.frequency:
                        if args.debug:
                            print("GPS Fix:", ardupilot.gps_0.fix_type, frame)
                        if ardupilot.gps_0.fix_type > 1:
                            last_data_send_times["gps"] = curr_time
                            asyncio.run(send_gps_message(websocket, frame.lat, frame.lon))

                def orientation_callback(self, _, attitude):
                    curr_time = time.perf_counter()
                    if curr_time >= last_data_send_times["orientation"] + 1./args.frequency:
                        if args.debug:
                            print(attitude)
                        else:
                            pitch_deg = attitude.pitch * 180 / math.pi
                            roll_deg = attitude.roll * 180 / math.pi
                            print(f"\33[2K\rroll={roll_deg: 4.0f}, pitch={pitch_deg: 4.0f}", end="")
                        last_data_send_times["orientation"] = curr_time
                        asyncio.run(send_orientation_message(
                            websocket, attitude.roll, attitude.pitch, attitude.yaw))

                ardupilot.add_attribute_listener("location.global_frame", gps_callback)
                ardupilot.add_attribute_listener("attitude", orientation_callback)

                try:
                    await asyncio.Future()
                except websockets.ConnectionClosed as e:
                    print(e)
                    ardupilot.remove_attribute_listener("location.global_frame", gps_callback)
                    ardupilot.remove_attribute_listener("attitude", orientation_callback)
                    print("Reconnecting to rover server...")
                    continue
        except (websockets.WebSocketException, OSError):
            await asyncio.sleep(3)
            pass


def main():
    debug_GPS_vars()


if __name__ == "__main__":
    asyncio.run(async_main())
    # main()
