# About
This folder contains a simple python applicaton that works as a relay to stream audio to Google Cloud Speech-to-Text API and return the recognized sentence. It is designed to work for single utterance. 

# Usage
This app is hosted in its own container in production, but can be used standalone. For production setup, see the setup/ readme. 

The first packet is expected to contain configuration data in the form og a json object. The supported options are

|Name | Legal Values|
|-----------------	|---------------------------------------	|
| lang            	| A BCP-47 language tag                 	|
| sample_rate     	| The sample rate of the audio streamed 	|
| interim_results 	| true or false               	|

## Installation
To run the app outisde of docker, ensure that you have python and pip installed, and activate a clean virtual environment. 

```
$ cd speech-app
$ pip install -r requirements.txt
```

## Credentials
To use this you need to have valid Google Cloud credentials, and have them available for the google api to find. Refer to the google Cloud documentation for how to ensure this. If this is not present the application will return a "END_OF_SPEECH" event already in the first response. 

# Technical
This app works by utilizing the websocket library, which is based on asyncio. By using async handlers, the audio data is read and the results returned on the same thread using async/wait constructions. The communication with the Cloud Speech-to-Text API is handeled on a dedicated thread. Messages are passed between the two threads using queues. The library janus is used to provide a queue with both async and synchronous methods. 
