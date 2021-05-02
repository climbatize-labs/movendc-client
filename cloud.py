import asyncio
import base64
import util
from mlog import mlog
import temperature

async def broadcast(state):
    msg = util.serialize("broadcast", {"msg" : "freshmeat"})
    await state["ws"].send(msg)

def login_msg(user, password, device):
    return util.serialize("login", {
        "user"   : user,
        "pass"   : password,
        "device" : device
    })

async def login_reply(state, payload):
    if "error" in payload and payload["error"] == "ok":
        state["logged"] = True
    else:
        mlog.debug("Login failed")
        state["closed"] = True

async def camera_reinit(state, payload):
    state["camera"].reinit()

async def camera_request_send(state, src, dst, encoded, objects,
                              ts, error, snapshots, tmp, dbg):
    msg = util.serialize("camera_request_done", {"src"       : src,
                                                 "dst"       : dst,
                                                 "image"     : encoded,
                                                 "objects"   : objects,
                                                 "timestamp" : ts,
                                                 "error"     : error,
                                                 "snapshots" : snapshots,
                                                 "temp"      : tmp})
    mlog.debug(dbg % len(msg))
    await state["ws"].send(msg)

async def camera_request(state, payload):
    tmp = temperature.get(state["cfg"]["philipshue"])
    if "src" in payload and "dst" in payload:
        imagefile, objects, ts, snapshots = state["monitor"].get_latest(payload["snapshot"])
        if imagefile == "":
            await camera_request_send(state, payload["src"], payload["dst"], "", 0,
                                      0, 1, snapshots, tmp, "No snapshot found: %s bytes")
            return
        ib      = util.fread(imagefile, "rb")
        encoded = base64.b64encode(ib).decode('ascii')
        await camera_request_send(state, payload["src"], payload["dst"], encoded,
                                  objects, ts, 0, snapshots, tmp, "Snapshot sent: %s bytes")
