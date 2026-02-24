# LiveKit Voice Agent - Option A (Echo)

A professional sentence-based echo agent that provides natural conversation flow with energy-based speech detection and immediate overlap prevention.

## Features

- **Sentence-based echo** - Buffers complete sentences before echoing
- **Energy-based speech detection** - Simple VAD for accurate speech/silence discrimination  
- **~1 second total delay** - 1.0s silence detection + 0.5s echo delay
- **No overlap prevention** - Immediate playback interruption when user speaks
- **20-second silence reminder** - Single 440Hz tone per silence period
- **Natural playback speed** - Dynamic frame duration preservation

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create `.env` file with your LiveKit credentials:
```env
# LiveKit Configuration
LIVEKIT_API_KEY=your_api_key_here
LIVEKIT_API_SECRET=your_api_secret_here
LIVEKIT_SERVER_URL=wss://your-server.livekit.cloud
VOICE_AGENT_NAME=Echo Agent
ROOM_NAME=Voice-agent
```

### 3. Run Agent
```bash
python main.py
```

### 4. Generate Token
```bash
python generate_token.py
```

### 5. Connect to Playground
1. Open: https://agents-playground.livekit.io
2. Select: "Manual" tab
3. Enter:
   - Server URL: `wss://voice-agent-dyjpkybz.livekit.cloud`
   - Room: `Voice-agent`
   - Token: [copy from generate_token.py output]
4. Click: "Connect"
5. Allow: Microphone permissions

## Architecture

### Audio Flow
```
User Speech → Energy Detection → Buffer → Silence Detection → Delay → Replay
     ↓              ↓              ↓              ↓        ↓
   Frame Level    >500           1.0s          0.5s     Natural Speed
```

### Core Components
- **EchoVoiceAgent** - Main agent class
- **handle_audio()** - Receives and processes audio frames
- **speech_monitor_loop()** - Detects speech end and triggers echo
- **play_buffer()** - Replays buffered audio with natural timing
- **silence_loop()** - Provides 20-second silence reminders

## SDK Used

- **LiveKit Python SDK** - `livekit` package
- **NumPy** - Audio processing and energy calculation
- **python-dotenv** - Environment variable management
- **asyncio** - Asynchronous task management
   ```bash
   python main.py
   ```

2. Connect to the same LiveKit room using a client application

3. Speak into your microphone - the agent will echo your audio back after 1 second

## Configuration

All configuration is done through environment variables in the `.env` file:

- `LIVEKIT_API_KEY`: Your LiveKit API key (required)
- `LIVEKIT_API_SECRET`: Your LiveKit API secret (required)
- `LIVEKIT_SERVER_URL`: Your LiveKit server WebSocket URL (required)
- `VOICE_AGENT_NAME`: Name of the echo agent (default: "Echo Agent")
- `ROOM_NAME`: Default room name (default: "echo-room")

## Testing

To test the echo functionality:

1. Set up your LiveKit server and update `.env` with your credentials
2. Run the echo agent: `python main.py`
3. Use a LiveKit client to join the same room
4. Speak - you should hear your voice echoed back after 1 second

## Implementation Details

The echo agent uses:

- **LiveKit RTC**: For real-time audio streaming and room management
- **AudioStream**: To capture incoming audio frames
- **AudioSource**: To publish echoed audio back to the room
- **AsyncIO**: For non-blocking audio processing and delay handling

## Next Steps (Option B)

To upgrade to Option B (STT → Response → TTS):

1. Add speech-to-text processing
2. Implement response generation logic
3. Add text-to-speech synthesis
4. Replace the echo logic with the STT→Response→TTS pipeline

## External Services

- **LiveKit Cloud** – Used for real-time audio streaming, room management, and WebRTC signaling.
  
No additional AI or speech-processing APIs were used for this implementation.

## Known Limitations

- Uses simple energy-based speech detection instead of advanced Voice Activity Detection (VAD).
- May not perform optimally in very noisy environments.
- Echo delay depends on silence threshold configuration.
- Not optimized for large-scale multi-user scenarios.
- Designed for demonstration and evaluation purposes.

## License

This project is licensed under the MIT License.
