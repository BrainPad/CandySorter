#!/usr/bin/python
# -*- coding: utf-8 -*-

import queue

# GCP imports
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import SpeechClient
from google.cloud.speech_v1p1beta1 import types

from app.phrases import PhraseGenerator


def get_client(lang='en-US', sample_rate=16000, interim_results=False,
               single_utterance=True, phrase_key=""):
    """
    Helper to return client and config
    """
    client = SpeechClient()
    config = types.StreamingRecognitionConfig(
        config=types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=lang,
            # Enhanced models are only available to projects that
            # opt in for audio data collection.
            use_enhanced=True,
            # A model must be specified to use enhanced model.
            model="command_and_search",
            speech_contexts=[types.SpeechContext(
                phrases=PhraseGenerator.get_phrases("app/config.json", phrase_key),
            )]
        ),
        interim_results=interim_results,
        single_utterance=single_utterance
    )
    print(str(config))
    return client, config


def loop_through_responses(responses, result_buffer):
    # Go through the responses returned from the streaming client.
    for response in responses:

        # TODO: Check to see if result is error or end of utterance
        if not len(response.results):  # Should test for single utterance in a better way
            # No results, so error or end of utterance

            result_buffer.put({
                'event': 'end_of_speech',
                'transcript': ''
            })

            # Wait for all messages put into the results buffer to be processed
            result_buffer.join()
            return

        else:
            # We'll only use the first result, as this usually contains the result as it is building up
            result = response.results[0]

            # Put the result into the result buffer
            result_buffer.put({
                'event': 'result',
                'transcript': result.alternatives[0].transcript
            })

            # Wait for all messages put into the results buffer to be processed
            result_buffer.join()


def audio_generator(buffer):
    while True:
        """
        A generator that fetches the input audio data from the buffer.
        Copied from google-cloud samples for speech: transcribe_streaming_mic with some alterations
        """
        # Use a blocking get() to ensure there's at least one chunk of
        # data, and stop iteration if the chunk is None, indicating the
        # end of the audio stream.
        chunk = buffer.get()
        if chunk is None:
            return
        data = [chunk]

        # Now consume whatever other data's still buffered.
        while True:
            try:
                chunk = buffer.get(block=False)
                if chunk is None:
                    return
                data.append(chunk)
            except queue.Empty:
                break
        yield b''.join(data)
