import asyncio
import websockets
import function_pattern_matching as fpm
from schema import Schema

import cloud
from mlog import mlog
from module import Module
import util


class ModuleWSClient(Module):
    def __init__(self, state):
        super().__init__(state)
        self.ws = None

    def init_schema(self):
        self.schema = Schema({
            "name": "WSClient",
            "active": bool,
            "deps": list,
            "host": str,
            "user": str,
            "pass": str,
            "device": str,
            "ssl": bool,
        })

    async def ws_recv(self):
        commands = { "account_login_reply" : cloud.login_reply,
                     "camera_request"      : cloud.camera_request,
                     "camera_reinit"       : cloud.camera_reinit }
        while(self.state.closed == False):
            try:
                msg = await self.ws.recv()
                mlog.debug("Received: %d bytes" % len(msg))
            except websockets.exceptions.ConnectionClosedOK as e:
                mlog.debug(e)
                self.state.closed = True
                break
            except websockets.exceptions.ConnectionClosed as e:
                mlog.debug(e)
                self.state.closed = True
                break

    async def ws_login(self, data):
        if(self.state.closed == True):
            return
        msg = cloud.login_msg(data["user"], data["pass"], data["device"])
        mlog.debug("Attempt to login")
        await self.ws.send(msg)

    async def ws_start(self, data):
        a = "wss://" + data["host"] + "/websocket"
        protocol = "ws://" if not data["ssl"] else "wss://"
        ssl_context = None if not data["ssl"] else self.state.sslcontext
        uri = protocol + data["host"] + "/websocket"
        mlog.debug(f"WSClient: Connecting to {uri}")
        async with websockets.connect(
            uri,
            ssl=ssl_context
        ) as websocket:
            self.ws = websocket
            asyncio.ensure_future(self.ws_login(data))
            loop = asyncio.get_event_loop()
            await loop.create_task(self.ws_recv())

    @fpm.case
    @fpm.guard
    async def fire(self: fpm._, data: fpm._,  version: fpm.eq("1")):
        asyncio.ensure_future(self.ws_start(data))
