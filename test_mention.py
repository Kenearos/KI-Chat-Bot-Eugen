#!/usr/bin/env python3
"""
Test script to check if mention detection works
"""
from utils import MentionDetector

# Test with your bot name
detector = MentionDetector(bot_name="Kenearos")

print("Testing Mention Detection for bot: Kenearos")
print("=" * 60)
print(f"Generated nicknames: {detector.nicknames}")
print()

# Test messages
test_messages = [
    "@Kenearos Hi",
    "Kenearos: wie gehts dir?",
    "Kene was meinst du?",
    "Hey Kenearos!",
    "kenearos test",
    "KENEAROS TEST",
    "Hi wie gehts",
    "Hallo",
    "test message without bot",
]

for msg in test_messages:
    is_mentioned = detector.is_mentioned(msg)
    is_greeting = detector.is_ambiguous_greeting(msg)
    content = detector.extract_content(msg) if is_mentioned else "N/A"

    print(f"Message: '{msg}'")
    print(f"  Mentioned: {is_mentioned}")
    print(f"  Ambiguous greeting: {is_greeting}")
    print(f"  Extracted content: '{content}'")
    print()
