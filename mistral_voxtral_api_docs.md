Audio input capabilities enable models to chat and understand audio directly, this can be used for both chat use cases via audio or for optimal transcription purposes.

![audio_graph](https://docs.mistral.ai/img/audio.png)

### Models with Audio Capabilities[](https://docs.mistral.ai/capabilities/audio/#models-with-audio-capabilities "Direct link to Models with Audio Capabilities")

Audio capable models:

-   **Voxtral Small** (`voxtral-small-latest`) with audio input for [chat](https://docs.mistral.ai/capabilities/audio/#chat-with-audio) use cases.
-   **Voxtral Mini** (`voxtral-mini-latest`) with audio input for [chat](https://docs.mistral.ai/capabilities/audio/#chat-with-audio) use cases
-   And **Voxtral Mini Transcribe** (`voxtral-mini-latest` via `audio/transcriptions`), with an efficient [transcription](https://docs.mistral.ai/capabilities/audio/#transcription) only service.

## Chat with Audio[](https://docs.mistral.ai/capabilities/audio/#chat-with-audio "Direct link to Chat with Audio")

Our Voxtral models are capable of being used for chat use cases with our chat completions endpoint.

### Passing an Audio File[](https://docs.mistral.ai/capabilities/audio/#passing-an-audio-file "Direct link to Passing an Audio File")

To pass a local audio file, you can encode it in base64 and pass it as a string.

-   python
-   typescript
-   curl

```
curl --location https://api.mistral.ai/v1/chat/completions \  --header "Authorization: Bearer $MISTRAL_API_KEY" \  --header "Content-Type: application/json" \  --data '{    "model": "voxtral-mini-latest",    "messages": [      {        "role": "user",        "content": [          {            "type": "input_audio",            "input_audio": "<audio_base64>",          },          {            "type": "text",            "text": "What'\''s in this file?"          }        ]      }    ]  }'
```

### Passing an Audio URL[](https://docs.mistral.ai/capabilities/audio/#passing-an-audio-url "Direct link to Passing an Audio URL")

You can also provide an url of a file.

-   python
-   typescript
-   curl

```
curl --location https://api.mistral.ai/v1/chat/completions \  --header "Authorization: Bearer $MISTRAL_API_KEY" \  --header "Content-Type: application/json" \  --data '{    "model": "voxtral-mini-2507",    "messages": [      {        "role": "user",        "content": [          {            "type": "input_audio",            "input_audio": "https://download.samplelib.com/mp3/sample-15s.mp3"          },          {            "type": "text",            "text": "What'\''s in this file?"          }        ]      }    ]  }'
```

### Passing an Uploaded Audio File[](https://docs.mistral.ai/capabilities/audio/#passing-an-uploaded-audio-file "Direct link to Passing an Uploaded Audio File")

Alternatively, you can upload a local file to our cloud and then use a signed URL for the task.

-   python
-   typescript
-   curl

**Upload the Audio File**

```
curl --location https://api.mistral.ai/v1/files \  --header "Authorization: Bearer $MISTRAL_API_KEY" \  --form purpose="audio" \  --form file="@local_audio.mp3"
```

**Get the Signed URL**

```
curl --location "https://api.mistral.ai/v1/files/$id/url?expiry=24" \    --header "Accept: application/json" \    --header "Authorization: Bearer $MISTRAL_API_KEY"
```

**Send Completion Request**

```
curl --location https://api.mistral.ai/v1/chat/completions \  --header "Authorization: Bearer $MISTRAL_API_KEY" \  --header "Content-Type: application/json" \  --data '{    "model": "voxtral-mini-2507",    "messages": [      {        "role": "user",        "content": [          {            "type": "input_audio",            "input_audio": "<signed_url>"          },          {            "type": "text",            "text": "What'\''s in this file?"          }        ]      }    ]  }'
```

**Samples**

## Transcription[](https://docs.mistral.ai/capabilities/audio/#transcription "Direct link to Transcription")

Transcription provides an optimized endpoint for transcription purposes and currently supports `voxtral-mini-latest`, which runs **Voxtral Mini Transcribe**.

**Parameters**  
We provide different settings and parameters for transcription, such as:

-   `timestamp_granularities`: This allows you to set timestamps to track not only "what" was said but also "when". You can find more about timestamps [here](https://docs.mistral.ai/capabilities/audio/#transcription-with-timestamps).
-   `language`: Our transcription service also works as a language detection service. However, you can manually set the language of the transcription for better accuracy if the language of the audio is already known.

### Passing an Audio File[](https://docs.mistral.ai/capabilities/audio/#passing-an-audio-file-1 "Direct link to Passing an Audio File")

Among the different methods to pass the audio, you can directly provide a path to a file to upload and transcribe it as follows:

-   python
-   typescript
-   curl

```
curl --location 'https://api.mistral.ai/v1/audio/transcriptions' \  --header "x-api-key: $MISTRAL_API_KEY" \  --form 'file=@"/path/to/file/audio.mp3"' \  --form 'model="voxtral-mini-2507"' \
```

**With Language defined**

```
curl --location 'https://api.mistral.ai/v1/audio/transcriptions' \  --header "x-api-key: $MISTRAL_API_KEY" \  --form 'file=@"/path/to/file/audio.mp3"' \  --form 'model="voxtral-mini-2507"' \  --form 'language="en"'
```

### Passing an Audio URL[](https://docs.mistral.ai/capabilities/audio/#passing-an-audio-url-1 "Direct link to Passing an Audio URL")

Similarly, you can provide an url of an audio file.

-   python
-   typescript
-   curl

```
curl --location 'https://api.mistral.ai/v1/audio/transcriptions' \  --header "x-api-key: $MISTRAL_API_KEY" \  --form 'file_url="https://docs.mistral.ai/audio/obama.mp3"' \  --form 'model="voxtral-mini-2507"'
```

**With Language defined**

```
curl --location 'https://api.mistral.ai/v1/audio/transcriptions' \  --header "x-api-key: $MISTRAL_API_KEY" \  --form 'file_url="https://docs.mistral.ai/audio/obama.mp3"' \  --form 'model="voxtral-mini-2507"' \  --form 'language="en"'
```

### Passing an Uploaded Audio File[](https://docs.mistral.ai/capabilities/audio/#passing-an-uploaded-audio-file-1 "Direct link to Passing an Uploaded Audio File")

Alternatively, you can first upload the file to our cloud service and then pass the signed URL instead.

-   python
-   typescript
-   curl

**Upload the Audio File**

```
curl --location https://api.mistral.ai/v1/files \  --header "Authorization: Bearer $MISTRAL_API_KEY" \  --form purpose="audio" \  --form file="@local_audio.mp3"
```

**Get the Signed URL**

```
curl --location "https://api.mistral.ai/v1/files/$id/url?expiry=24" \    --header "Accept: application/json" \    --header "Authorization: Bearer $MISTRAL_API_KEY"
```

**Send Transcription Request**

```
curl --location 'https://api.mistral.ai/v1/audio/transcriptions' \    --header "x-api-key: $MISTRAL_API_KEY" \    --form 'file_url="<signed_url>"' \    --form 'model="voxtral-mini-2507"'
```

**Send Transcription Request with Language defined**

```
curl --location 'https://api.mistral.ai/v1/audio/transcriptions' \    --header "x-api-key: $MISTRAL_API_KEY" \    --form 'file_url="<signed_url>"' \    --form 'model="voxtral-mini-2507"' \    --form 'language="en"'
```

**JSON Output** **Samples**

## Transcription with Timestamps[](https://docs.mistral.ai/capabilities/audio/#transcription-with-timestamps "Direct link to Transcription with Timestamps")

You can request timestamps for the transcription by passing the `timestamp_granularities` parameter, currently supporting `segment`.  
It will return the start and end time of each segment in the audio file.

-   python
-   typescript
-   curl

```
curl --location 'https://api.mistral.ai/v1/audio/transcriptions' \--header "x-api-key: $MISTRAL_API_KEY" \--form 'file_url="https://docs.mistral.ai/audio/obama.mp3"' \--form 'model="voxtral-mini-latest"'--form 'timestamp_granularities="segment"'
```

**JSON Output**

## FAQ[](https://docs.mistral.ai/capabilities/audio/#faq "Direct link to FAQ")

-   **What's the maximum audio length?**
    
    The maximum length will depend on the endpoint used, currently the limits are as follows:
    
    -   ≈20 minutes for [Chat with Audio](https://docs.mistral.ai/capabilities/audio/#chat-with-audio) for both models.
    -   ≈15 minutes for [Transcription](https://docs.mistral.ai/capabilities/audio/#transcription), longer transcriptions will be available soon.

tip

Here are some tips if you need to handle longer audio files:

-   **Divide the audio into smaller segments:** Transcribe each segment individually. However, be aware that this might lead to a loss of context, difficulties in splitting the audio at natural pauses (such as mid-sentence), and the need to combine the transcriptions afterward.
-   **Increase the playback speed:** Send the file at a faster pace by speeding up the audio. Keep in mind that this can reduce audio quality and require adjusting the transcription timestamps to align with the original audio file.