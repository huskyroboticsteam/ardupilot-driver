from math import pi
import time
import sys
import asyncio
import websockets
import json

# Removing this include breaks dronekit include... IDK
# Should just run in pipenv with python3.8 or something
from pymavlink import mavutil
# This if is required because dronekit is not up to date for python 3.10
# Should just run in pipenv with python3.8 or something
if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    setattr(collections, "MutableMapping", collections.abc.MutableMapping)
import dronekit

import argparse

def debugGPSVars():
    (port, baud, _) = getArgs()
    print("Waiting for connection to {}...".format(port))
    pixhawk = dronekit.connect(port, wait_ready=True, baud=baud)
    print("Connection established to {}!".format(port))

    while True:
        time.sleep(1)
        lat = pixhawk.location.global_frame.lat
        lon = pixhawk.location.global_frame.lon
        roll  = pixhawk.attitude.roll;
        pitch  = pixhawk.attitude.pitch;
        yaw  = pixhawk.heading;
        # Local declination

        print("lat: {}, lon: {}, roll: {}, pitch: {}, yaw: {}"
              .format(lat, lon, roll, pitch, yaw))

# Returns (port, baud)
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True, help="Current connection port to Pixhawk")
    parser.add_argument("--baud", required=False, default=57600, help="Current connection port to Pixhawk")
    parser.add_argument("--debug", required=False, help="Prints lat, lon, roll, pitch, yaw, heading to stdout.")
    args = parser.parse_args()
    return (args.port, args.baud, args.debug)

async def sendGPS(websocket, port, baud):
    print("Waiting for connection to {}...".format(port))
    pixhawk = dronekit.connect(port, wait_ready=True, baud=baud)
    print("Connection established to {}!".format(port))

    # From M8N documentation:
    # If unable to preform normal compass calibration "compass dance" for any reason,
    # set parameter COMPASS_ORIENT=6 (Yaw270) for proper compass orientation.
    pixhawk.parameters["COMPASS_ORIENT"] = 6;

    # TODO: Add a handler for a terminate message or something to kill this
    while True:
        # TODO: Decide whether to keep or remove this sleep
        time.sleep(1)
        lat = pixhawk.location.global_frame.lat
        lon = pixhawk.location.global_frame.lon
        roll  = pixhawk.attitude.roll;
        pitch  = pixhawk.attitude.pitch;
        # Yaw and heading should be equivalent
        yaw  = pixhawk.attitude.yaw;
        heading = pixhawk.heading;
        asyncio.create_task(createGPSMessage(websocket, lat, lon))
        asyncio.create_task(createIMUMessage(websocket, roll, pitch, yaw))
        asyncio.create_task(createHeadingMessage(websocket, heading))

async def createGPSMessage(websocket, lat, lon):
    msg = json.loads('{}')
    msg["lat"] = lat;
    msg["lon"] = lon;
    await websocket.send(json.dumps(msg))

async def createIMUMessage(websocket, roll, pitch, yaw):
    msg = json.loads('{}')
    msg["roll"] = roll;
    msg["pitch"] = pitch;
    msg["yaw"] = yaw;
    await websocket.send(json.dumps(msg))

async def createHeadingMessage(websocket, heading):
    msg = json.loads('{}')
    msg["heading"] = heading;
    await websocket.send(json.dumps(msg))

async def handler(websocket):
    (port, baud, _) = getArgs()
    asyncio.create_task(sendGPS(websocket, port, baud))

async def async_main():
    async with websockets.serve(handler, "", 3001):
        await asyncio.Future()

def main():
    debugGPSVars()

if __name__ == "__main__":
    asyncio.run(async_main())
    #main()
