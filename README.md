# piper-voice-api

API to use the Piper-tts python model, wrapped inside NodeJS API

## Run

To run the service, use the `compose.yaml` docker compose file and run using `docker compose up`

For development, you can use the `compose.dev.yaml` file. More info in `piper-tts/README.md`.

## API-Doc

The API is quite simplistic.

### Gernerate audio file

For generating an audio file, make a `POST` request to the `/tts` endpoint, with the `text` and `voice` attribute as JSON-Body:

```json
{
  "text": "Hallo aus der maschine",
  "voice": "de_DE-thorsten-medium"
}
```

The server will respond with an `id` within the JSON-Response:

```json
{
  "id": "1726fe40-10bc-4944-83a6-fc85097c9d1f"
}
```

With that, the audio generation process is started.

### see status of generation

To check the status of the generation process, make a `GET` request to `/tts/{id}`, where `id` is your audio id. (`/tts/1726fe40-10bc-4944-83a6-fc85097c9d1f`).

The server will then respond with the Status of the generation:

```json
{
  "id": "a8056646-11d3-4f82-8ab2-58e911027abb",
  "status": "done"
}
```

The status can either be `processing`, `done` or `error`. If the job is not found, `{"error":"Job not found"}` is returned.

### recieve the audio

To recieve the audio, once it is done, make a `GET` request to `/tts/{id}/audio` where `id` is your audio id. (`/tts/1726fe40-10bc-4944-83a6-fc85097c9d1f/audio`).

The server should respond with a wav file of your audio.
