# Piper-tts

Locally hosted TTS Service using Piper-TTS at it's core. It exposes the engine via a UNIX-Socket as a sort of API.

## Build and publish docker

```sh
docker build -t ghcr.io/tinycodelabs/piper-voice-tts:latest .
docker push ghcr.io/tinycodelabs/piper-voice-tts:latest
```

## Develop locally

To develop locally, you have to create a python venv and activate it

```sh
python3 -m venv ./.venv
source ./.venv/bin/activate
```

After that you can install the required packages using the `requirements.txt` file:

```sh
pip install -r requirements.txt
```

**Switch to the parent directory**

Then you can run the service for development using the `compose.dev.yaml` file on Docker Compose:

```sh
docker compose -f compose.dev.yaml up --build
```

But make sure the folders `run` and `out` exist with the right user rights:

```sh
sudo chown 10001:10001 out
sudo chown 10001:10001 run
```

## Fill with voices

Put the voices, the `ONNX` and their `JSON` Files into the `/app/voices` folder inside the container.

## Test the API

Send a JSON-String to the UNIX-Socket exposed at `/app/tts.sock` and get the generated files from `/app/out/`.

```json
{
  "text": "Hallo aus dem Python",
  "voice": "de_DE-thorsten-medium",
  "filename": "hello.wav"
}
```

For accessing the socket using a terminal:

```sh
sudo socat - UNIX-CONNECT:./run/tts.sock
```
