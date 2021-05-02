import asyncio, base64, websockets, json, ssl, sys

import cloud, util
from mlog import mlog
from monitor import monitor
from capture import capture

from state import State
import config
from module import (
    ModuleWSClient,
    ModuleImage,
    ModulePhilipshue,
)

async def cam_worker(state):
    while(state["closed"] == False):
        if(state["logged"] != True):
            await asyncio.sleep(1)
            continue
        ok, imagefile, objects, timestamp = state["camera"].fetch()
        if(imagefile != None and len(imagefile) > 0):
            mlog.debug("Broadcast objects: %d" % objects)
            state["monitor"].update(imagefile, objects, timestamp)
            await cloud.broadcast(state)
        await asyncio.sleep(1)

async def login(state, cfg):
    if(state["closed"] == True):
        return
    msg = cloud.login_msg(cfg["user"], cfg["pass"], cfg["device"])
    mlog.debug("Attempt to login")
    await state["ws"].send(msg)

async def ws_recv(state):
    commands = { "account_login_reply" : cloud.login_reply,
                 "camera_request"      : cloud.camera_request,
                 "camera_reinit"       : cloud.camera_reinit }
    while(state["closed"] == False):
        try:
            msg = await state["ws"].recv()
            mlog.debug("Received: %d bytes" % len(msg))
            command, payload = util.deserialize(msg)
            if(command in commands): await commands[command](state, payload)
        except websockets.exceptions.ConnectionClosed as e:
            mlog.error("Connection error: " + e)
            state["closed"] = True
            break
        except:
            mlog.warning("Received unsupported message ")
    mlog.debug("Leaving..")

async def run(camera, loop):
    try:
        state = { "closed"  : False,
                  "camera"  : camera,
                  "logged"  : False,
                  "monitor" : monitor(cfg["camera"]),
                  "ssl"     : ssl.SSLContext(),
                  "cfg"     : cfg }
        state["ssl"].verify_mode = ssl.CERT_NONE
        state["camera"].setparams({
            "node" : cfg["camera"],
            "processing" : cfg["processing"]
        })

        async with websockets.connect(
            "wss://" + cfg["host"] + "/websocket",
            ssl=state["ssl"]
        ) as websocket:
            state["ws"] = websocket
            task2 = loop.create_task(ws_recv(state))
            task3 = loop.create_task(login(state, cfg))

            task1 = loop.create_task(cam_worker(state))
            await task1
            await task2
            await task3
    except OSError as e:
        raise("Exception: ", e)

async def state_init():
    state = State()
    await state.init("")

def main():
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(state_init())
    loop.run_forever()

main()
