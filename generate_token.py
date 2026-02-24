#!/usr/bin/env python3
"""
Generate LiveKit access tokens
"""

import os
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

# Load environment variables
load_dotenv()

def generate_token(room_name: str, participant_name: str) -> str:
    """
    Generate a LiveKit access token for a participant
    
    Args:
        room_name: Name of the LiveKit room
        participant_name: Name of the participant
        
    Returns:
        JWT token string
    """
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in .env file")
    
    token = AccessToken(api_key, api_secret)
    token.with_grants(VideoGrants(
        room_join=True,
        room=room_name,
        can_publish=True,
        can_subscribe=True
    ))
    token.with_name(participant_name)
    token.with_identity(participant_name)
    
    return token.to_jwt()

if __name__ == "__main__":
    # Example usage
    room = "Voice-agent"
    participant = "test-user"
    
    try:
        token = generate_token(room, participant)
        
        print("=" * 60)
        print("🔗 LIVEKIT CONNECTION DETAILS")
        print("=" * 60)
        print()
        print("🌐 Playground URL:")
        print("https://agents-playground.livekit.io")
        print()
        print("🎯 Connection Information:")
        print(f"   Server URL: wss://voice-agent-dyjpkybz.livekit.cloud")
        print(f"   Room Name: {room}")
        print(f"   Agent Name: Echo Agent")
        print()
        print("🎫 Fresh Token:")
        print(f"   {token}")
        print()
        print("=" * 60)
        print("✅ Ready to connect! Copy the token and use in playground.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error generating token: {e}")
