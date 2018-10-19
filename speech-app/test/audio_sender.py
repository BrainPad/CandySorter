#!/usr/bin/env python


"""Based on Google Cloud Speech API sample application using the streaming API.

Example usage:
    python audio_sender.py resources/audio.raw
"""

# [START import_libraries]
import argparse
import io
import sys
import json

import asyncio
import websockets # pip install websockets


# [START def_transcribe_streaming]
async def transcribe_streaming(stream_file):
    """Streams raw data of the given audio file."""
    # [START migration_streaming_request]
    stream = []

    for file in ['audio2.raw']:
        with io.open(file, 'rb') as audio_file:
            stream.append(audio_file.read())

    async with websockets.connect('ws://localhost:8765') as websocket:
        await websocket.send('{"sample_rate":16000, "interim_results":true}')
        for content in stream:
            await websocket.send(content)

        async for message in websocket:
            data = json.loads(message)
            if data['is_final']:
                print(data['transcript'])
                break
            else:
                sys.stdout.write(data['transcript'] + '\r')
                sys.stdout.flush()
                await asyncio.sleep(0.05)

# [END def_transcribe_streaming]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('stream', help='File to stream to the API')
    args = parser.parse_args()

    asyncio.get_event_loop().run_until_complete(transcribe_streaming(args.stream))
