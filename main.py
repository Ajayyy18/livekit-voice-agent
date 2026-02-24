#!/usr/bin/env python3
"""
LiveKit Voice Agent - Clean Echo Implementation
Simple, clear echo with minimal processing
"""

import asyncio
import os
import time
import numpy as np
from dotenv import load_dotenv
from livekit import rtc
from livekit.api import AccessToken, VideoGrants

load_dotenv()

class EchoVoiceAgent:
    def __init__(self):
        self.api_key = os.getenv("LIVEKIT_API_KEY")
        self.api_secret = os.getenv("LIVEKIT_API_SECRET")
        self.server_url = os.getenv("LIVEKIT_SERVER_URL")
        self.room_name = os.getenv("ROOM_NAME", "Voice-agent")
        self.agent_name = os.getenv("VOICE_AGENT_NAME", "Echo Agent")
        
        if not all([self.api_key, self.api_secret, self.server_url]):
            raise ValueError("Missing environment variables")
        
        # Audio state
        self.speech_buffer = []
        self.is_collecting = False
        self.playback_task = None
        self.last_speech_time = time.time()
        
        # Simple, clear parameters
        self.SILENCE_THRESHOLD = 1.0   # seconds
        self.ECHO_DELAY = 0.5          # seconds
        self.ENERGY_THRESHOLD = 500    # speech detection

    def generate_token(self):
        token = AccessToken(self.api_key, self.api_secret)
        token.with_grants(
            VideoGrants(
                room_join=True,
                room=self.room_name,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True
            )
        )
        token.with_identity(self.agent_name)
        token.with_name(self.agent_name)
        return token.to_jwt()

    async def connect(self):
        print("🔗 Connecting to LiveKit...")
        
        self.room = rtc.Room()
        
        @self.room.on("participant_connected")
        def on_participant_connected(participant):
            print(f"✅ Participant connected: {participant.identity}")
        
        @self.room.on("track_subscribed")
        def on_track_subscribed(track, publication, participant):
            print(f"🎵 Track subscribed: {track.kind} from {participant.identity}")
            if participant.identity == self.agent_name:
                print(f"⚠️ Ignoring agent's own track")
                return
            
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                print(f"🎤 Starting audio echo for {participant.identity}")
                asyncio.create_task(self.handle_audio(track))
        
        await self.room.connect(self.server_url, self.generate_token())
        print(f"✅ Connected to room: {self.room_name}")
        
        self.audio_source = rtc.AudioSource(48000, 1)
        self.audio_track = rtc.LocalAudioTrack.create_audio_track(
            "echo-track", self.audio_source
        )
        await self.room.local_participant.publish_track(self.audio_track)
        print(f"🎤 Published audio track: {self.audio_track.name}")
        
        print("🎤 Echo Agent Ready...")
        
        asyncio.create_task(self.speech_monitor_loop())
        asyncio.create_task(self.silence_loop())

    async def handle_audio(self, track):
        stream = rtc.AudioStream(track)
        
        async for event in stream:
            frame = event.frame
            
            # Simple energy detection
            pcm = np.frombuffer(frame.data, dtype=np.int16)
            energy = np.abs(pcm).mean()
            
            if energy > self.ENERGY_THRESHOLD:
                # Interrupt any ongoing playback
                if self.playback_task and not self.playback_task.done():
                    self.playback_task.cancel()
                    print("⏹️ Playback interrupted")
                
                # Add to buffer
                self.speech_buffer.append(frame)
                self.is_collecting = True
                self.last_speech_time = time.time()
                print(f"🎤 Received speech | Buffer: {len(self.speech_buffer)}")

    async def speech_monitor_loop(self):
        while True:
            await asyncio.sleep(0.1)
            
            if self.is_collecting and len(self.speech_buffer) > 0:
                silence_duration = time.time() - self.last_speech_time
                
                if silence_duration > self.SILENCE_THRESHOLD:
                    print(f"🛑 Speech ended | Buffer: {len(self.speech_buffer)}")
                    
                    frames_to_play = self.speech_buffer.copy()
                    self.speech_buffer.clear()
                    self.is_collecting = False
                    
                    # Wait for echo delay
                    await asyncio.sleep(self.ECHO_DELAY)
                    
                    if frames_to_play:
                        print(f"📢 Playing {len(frames_to_play)} frames")
                        self.playback_task = asyncio.create_task(
                            self.play_buffer(frames_to_play)
                        )

    async def play_buffer(self, frames):
        try:
            for frame in frames:
                await self.audio_source.capture_frame(frame)
            print("✅ Playback finished")
        except asyncio.CancelledError:
            print("⏹️ Playback cancelled")

    async def silence_loop(self):
        while True:
            await asyncio.sleep(2)
            
            if not self.is_collecting and time.time() - self.last_speech_time > 20:
                print("🔔 20 seconds silence → reminder")
                await self.play_reminder()
                self.last_speech_time = time.time()

    async def play_reminder(self):
        sample_rate = 48000
        duration = 0.5
        frequency = 440
        
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        tone = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
        
        frame = rtc.AudioFrame(
            data=tone.tobytes(),
            sample_rate=sample_rate,
            num_channels=1,
            samples_per_channel=len(tone),
        )
        
        await self.audio_source.capture_frame(frame)

    async def run(self):
        await self.connect()
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    agent = EchoVoiceAgent()
    asyncio.run(agent.run())
