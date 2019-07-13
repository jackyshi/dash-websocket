# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 00:21:57 2019

@author: admin
"""

import asyncio
import nest_asyncio
import threading
import websockets
import pandas as pd
nest_asyncio.apply()

@asyncio.coroutine
def greet_every_two_seconds():
    while True:
        print('Hello World')
        yield from asyncio.sleep(2)

async def consumer_handler():
    async with websockets.connect(
            'ws://localhost:8001') as websocket:
        while True:
            message = await websocket.recv()
            print(pd.read_json(message, typ='series').to_frame().T)
            
def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    #loop.run_until_complete(greet_every_two_seconds())
    loop.run_until_complete(consumer_handler())


loop = asyncio.get_event_loop()

t = threading.Thread(target=loop_in_thread, args=(loop,))
t.start()