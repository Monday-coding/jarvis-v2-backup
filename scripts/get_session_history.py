#!/usr/bin/env python3
"""
Utility script to extract session history for content-based detector.
"""

import json
import sys
import os
from typing import List, Dict

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_based_detector import ContentBasedDetector


def extract_messages_from_session_file(session_file: str,
                                       last_n: int = 10) -> List[str]:
    """
    Extract last N messages from session JSONL file.

    Args:
        session_file: Path to session file
        last_n: Number of messages to extract

    Returns:
        List of messages in reverse chronological order
    """
    messages = []

    if not os.path.exists(session_file):
        print(f"Warning: Session file not found: {session_file}")
        return messages

    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            # Read last N lines
            lines = f.readlines()
            relevant_lines = lines[-last_n:] if last_n < len(lines) else lines

            for line in relevant_lines:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                    # Extract message from different possible fields
                    message = (
                        entry.get('message') or
                        entry.get('assistant') or
                        entry.get('user') or
                        str(entry.get('content', ''))
                    )

                    if message:
                        messages.append(message)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse line: {line[:50]}...")
                    continue

    except Exception as e:
        print(f"Error reading session file: {e}")
        return messages

    return messages


def extract_session_key_from_file(session_file: str) -> str:
    """
    Extract session key from session file.

    Args:
        session_file: Path to session file

    Returns:
        Session key or empty string
    """
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                entry = json.loads(line)
                if 'sessionKey' in entry:
                    return entry['sessionKey']

        return ""
    except Exception as e:
        print(f"Error extracting session key: {e}")
        return ""


def detect_state_with_history(user_input: str,
                              session_file: str,
                              last_n: int = 10) -> Dict:
    """
    Detect conversation state using session history.

    Args:
        user_input: Current user message
        session_file: Path to session file
        last_n: Number of messages to use from history

    Returns:
        Detection result from ContentBasedDetector
    """
    # Extract messages from session
    history = extract_messages_from_session_file(session_file, last_n)

    # Get session key (for potential fallback)
    session_key = extract_session_key_from_file(session_file)

    # Detect state
    detector = ContentBasedDetector()
    result = detector.detect(user_input, history, session_key)

    # Add session key to result
    result['sessionKey'] = session_key
    result['historyLength'] = len(history)

    return result


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract session history and detect conversation state'
    )

    parser.add_argument(
        'session_file',
        type=str,
        help='Path to session JSONL file'
    )

    parser.add_argument(
        '--user-input',
        type=str,
        help='User input message (if not provided, interactive mode)'
    )

    parser.add_argument(
        '--last-n',
        type=int,
        default=10,
        help='Number of messages to extract from history (default: 10)'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'pretty', 'simple'],
        default='pretty',
        help='Output format (default: pretty)'
    )

    args = parser.parse_args()

    # Get user input if not provided
    user_input = args.user_input
    if not user_input:
        print(f"Reading session file: {args.session_file}")
        print()
        user_input = input("Enter your message: ")

    # Detect state
    result = detect_state_with_history(user_input, args.session_file, args.last_n)

    # Format output
    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.format == 'simple':
        print(f"Conversation State: {result['conversationState']}")
        print(f"Similarity: {result.get('similarityToPrevious', 0.0):.2f}")
        print(f"Detected by: {result['detectedBy']}")
        print(f"Confidence: {result.get('confidence', 0.0):.2f}")
        print(f"History Length: {result['historyLength']}")
    else:  # pretty
        print("=" * 80)
        print("Conversation State Detection Result")
        print("=" * 80)
        print(f"\nConversation State: {result['conversationState']}")
        print(f"Similarity to Previous: {result.get('similarityToPrevious', 0.0):.3f}")
        print(f"Detected by: {result['detectedBy']}")
        print(f"Confidence: {result.get('confidence', 0.0):.3f}")
        print(f"Session Key: {result.get('sessionKey', 'N/A')}")
        print(f"History Length: {result['historyLength']} messages")
        print(f"\nReason: {result.get('reason', 'N/A')}")
        print("=" * 80)


if __name__ == "__main__":
    main()
