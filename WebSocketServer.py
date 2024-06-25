#!/usr/bin/python3
# 主要功能：创建1个基本的websocket server, 符合asyncio 开发要求
import asyncio
import websockets
from datetime import datetime


async def handler(websocket):
    data = await websocket.recv()
    print(data)
    reply = f"Data received as \"{data}\".  time: {datetime.now()}"
    print(reply)
    await websocket.send(reply)
    print("Send reply")


async def main():
    async with websockets.serve(handler, "0.0.0.0", 1997):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
