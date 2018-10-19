#!/usr/bin/env python

import asyncio
import websockets

# GCP imports
from google.cloud.speech_v1p1beta1 import types

import queue
import janus
import json

from app.handlers import producer_handler, consumer_handler, gcp_handler
from app.utils import get_client


async def handler(websocket, path):
    """
    Main handler for the websocket connection. Reads the first message as this should be config information,
    and then hands the connection overt to a receiver and producer handlers for sending messages. The receive
    handlers will read and put messages into a queue. An independent thread reads the received
    audio data and relays this into the GCP API. It puts the responses received from GCP into a queue that
    is read by the send handler and returned to the client over the websocket connection.
    """

    # The first message from the browser should be json formatted config info
    config_data = await websocket.recv()
    config = json.loads(config_data)

    # Get config based on clients data
    api_client, api_config = get_client(**config)

    # Create a thread safe buffer for audio data
    audio_buffer = queue.Queue()

    # Get hold of asyncio event loop, needed for response queue and tasks
    loop = asyncio.get_event_loop()

    # Create a async/sync queue for responses
    response_queue = janus.Queue(loop=loop)

    # Create tasks for receiving, sending and processing the data
    # Send/receive will be using asyncio, while processing will be on it's own thread
    tasks = [
        loop.create_task(consumer_handler(websocket, audio_buffer)),            # Handle incoming messages
        loop.create_task(producer_handler(websocket, response_queue.async_q)),  # Handle sending responses back
        loop.run_in_executor(None, gcp_handler, audio_buffer,
                             response_queue.sync_q, api_client, api_config)     # Process gcp requests
    ]

    # Wait for one to complete. either the consumer completes because of loss of connection,
    # or the final result has been received from GCP
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
    )

    # Cancel the remaining task. This might not kill the thread?
    for task in pending:
        task.cancel()

    # Close the socket
    await websocket.close()


start_server = websockets.serve(handler, '', 80)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
