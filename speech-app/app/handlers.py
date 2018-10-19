import asyncio
import json

from google.cloud.speech_v1p1beta1 import types
from app.utils import loop_through_responses, audio_generator


async def consumer_handler(websocket, audio_buffer):
    try:
        async for message in websocket:
            audio_buffer.put(message)
    except asyncio.CancelledError:
        # Task requested to terminate, just return
        return

    except Exception as e:
        # TODO: Log exception
        return


async def producer_handler(websocket, response_buffer):
    try:
        while True:
            response = await response_buffer.get()
            await websocket.send(json.dumps(response))
            response_buffer.task_done()

            if response['event'] == "end_of_speech":
                return

    except asyncio.CancelledError:
        # Task requested to terminate, just return
        return

    except Exception as e:
        # TODO: Log exception
        return


def gcp_handler(audio_buffer, response_buffer, client, config):
    # Create requests generator using the audio generator, adapted from transcribe-streaming sample
    requests = (types.StreamingRecognizeRequest(audio_content=content) for content in audio_generator(audio_buffer))
    responses = client.streaming_recognize(config, requests)

    loop_through_responses(responses, response_buffer)