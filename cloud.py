import asyncio
import base64
import util
from mlog import mlog

async def broadcast(state):
    msg = util.serialize("broadcast", {"msg" : "freshmeat"})
    await state["ws"].send(msg)

def login_msg(user, password, device):
    return util.serialize("account_login", {"user"   : user,
                                            "pass"   : password,
                                            "device" : device})

async def login_reply(state, payload):
    if "error" in payload and payload["error"] == "ok":
        state["logged"] = True

async def camera_request_send(state, src, dst, encoded, objects,
                              ts, error, dbg):
    msg = util.serialize("camera_request_done", {"src"       : src,
                                                 "dst"       : dst,
                                                 "image"     : encoded,
                                                 "objects"   : objects,
                                                 "timestamp" : ts,
                                                 "error"     : error})
    mlog.debug(dbg)
    await state["ws"].send(msg)

async def camera_request(state, payload):
    if "src" in payload and "dst" in payload:
        imagefile, objects, ts = state["monitor"].get_latest()
        if imagefile == "":
            await camera_request_send(state, payload["src"], payload["dst"], "", 0,
                                      0, 1, "No snapshot found")
            return
        ib      = util.fread(imagefile, "rb")
        encoded = base64.b64encode(ib).decode('ascii')
        await camera_request_send(state, payload["src"], payload["dst"], encoded,
                                  objects, ts, 0, "Snapshot sent")
