#!/usr/bin/env python3
"""Debug test for conversation state detector."""

import subprocess
from content_based_detector import ContentBasedDetector

detector = ContentBasedDetector()

# Test case
user_input = "今天天氣怎麼樣？"
session_history = [
    "你好，今天天氣怎麼樣？",
    "我在香港，今天有點冷"
]

print("=" * 80)
print("Debug Test: Continuation")
print("=" * 80)
print()
print(f"User input: {user_input}")
print()
print("Session history:")
for i, msg in enumerate(session_history):
    print(f"  {i+1}. {msg}")
print()

# Calculate similarity manually
last_msg = session_history[-1]
cmd = [
    'ollama', 'run', 'qwen2.5:1.5b',
    f"""Calculate semantic similarity (0-1) between these two messages:

User: {user_input}
Last message: {last_msg}

Just return the similarity score as a number between 0 and 1, no other text."""
]

result = subprocess.run(cmd, input=user_input, capture_output=True, text=True, timeout=10)
similarity = float(result.stdout.strip())

print(f"Similarity: {similarity}")
print(f"Similarity >= 0.65? {similarity >= 0.65}")
print(f"Similarity >= 0.45? {similarity >= 0.45}")
print()

# Check topics
print("Topics:")
for i, msg in enumerate(session_history):
    topic = detector._extract_topic(msg)
    print(f"  Message {i+1} topic: {topic}")
print()

# Check context shift
has_context_shift = detector._detect_context_shift(session_history)
print(f"Context shift detected: {has_context_shift}")
print()

# Run full detection
final_result = detector.detect(user_input, session_history)
print()
print("Final detection result:")
print(f"  Conversation state: {final_result['conversationState']}")
print(f"  Similarity: {final_result.get('similarityToPrevious', 0.0)}")
print(f"  Detected by: {final_result.get('detectedBy', 'unknown')}")
print(f"  Reason: {final_result.get('reason', '')}")
