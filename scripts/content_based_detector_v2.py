#!/usr/bin/env python3
"""
Content-Based Conversation State Detector - Hybrid Strategy (High Priority)

Uses multiple detection methods with intelligent priority:
1. Keyword detection (HIGHEST PRIORITY) - Most reliable
2. Topic shift detection (MEDIUM) - Context-aware
3. Similarity calculation (LOWEST) - Final fallback
"""

import json
import sys
import subprocess
from typing import Dict, List, Optional, Tuple


class ContentBasedDetectorHybrid:
    """Hybrid detector with intelligent priority strategy."""

    def __init__(self):
        self.keywords = {
            "high_priority": [
                "然後呢",
                "接著說",
                "順便問一下",
                "另外",
                "說起來",
                "話說",
                "換話題",
                "話題轉換"
            ],
            "medium_priority": [
                # Removed "怎麼", "嗎", "呢" - these are common conversational particles
                "但是"
                "不過"
                "還有"
                "另外說一下"  # Note: High priority keyword, not medium
            ],
            "low_priority": [
                # Common conversational particles that don't indicate topic change
                "什麼",
                "怎麼",
                "嗎",
                "呢"
            ]
        }

    def detect(self,
               user_input: str,
               session_history: List[str],
               session_key: str = "") -> Dict:
        """
        Detect conversation state using hybrid strategy.

        Priority order:
        1. High-priority keywords (most reliable)
        2. Topic shift detection (context-aware)
        3. Similarity calculation (final fallback)

        Returns:
        {
          "conversationState": "new_conversation" | "continuation" | "topic_change",
          "similarityToPrevious": 0.0-1.0,
          "detectedBy": "keyword_high" | "keyword_medium" | "topic_shift" | "similarity",
          "confidence": 0.0-1.0,
          "reason": "explanation"
        }
        """
        # Step 1: Check if history is empty
        if not session_history or len(session_history) == 0:
            return {
                "conversationState": "new_conversation",
                "similarityToPrevious": 0.0,
                "detectedBy": "empty_history",
                "confidence": 1.0,
                "reason": "No session history available"
            }

        # Step 2: Keyword detection (HIGHEST PRIORITY)
        # High priority keywords are explicit topic change markers
        for keyword in self.keywords["high_priority"]:
            if keyword in user_input:
                return {
                    "conversationState": "topic_change",
                    "similarityToPrevious": 0.0,
                    "detectedBy": "keyword_high",
                    "confidence": 0.95,
                    "reason": f"High-priority keyword '{keyword}' detected"
                }

        # Medium priority keywords are softer indicators
        for keyword in self.keywords["medium_priority"]:
            if keyword in user_input:
                return {
                    "conversationState": "topic_change",
                    "similarityToPrevious": 0.0,
                    "detectedBy": "keyword_medium",
                    "confidence": 0.85,
                    "reason": f"Medium-priority keyword '{keyword}' detected"
                }

        # Low priority keywords are conversational particles (should NOT trigger topic change)
        # Only trigger topic change if there are other indicators
        for keyword in self.keywords["low_priority"]:
            if keyword in user_input:
                # Don't trigger topic change for just these particles
                # They need to be combined with other indicators
                return {
                    "conversationState": "continuation",
                    "similarityToPrevious": 0.0,
                    "detectedBy": "ignored_low_priority",
                    "confidence": 0.95,
                    "reason": f"Ignored low-priority keyword '{keyword}' (conversational particle)"
                }

        # Step 3: Topic shift detection (MEDIUM PRIORITY)
        has_context_shift = self._detect_context_shift(session_history)
        if has_context_shift:
                return {
                    "conversationState": "topic_change",
                    "similarityToPrevious": 0.0,
                    "detectedBy": "topic_shift",
                    "confidence": 0.82,
                    "reason": "Topic shift detected (context-aware)"
                }

        # Step 4: Similarity calculation (LOWEST PRIORITY - final fallback)
        # Only if no keywords or topic shift detected
        similarity = self._calculate_semantic_similarity(user_input, session_history)

        # Adjusted thresholds for hybrid strategy
        if similarity >= 0.40:
            state = "continuation"
            confidence = similarity
            reason = "High semantic similarity indicates continuation"
        elif similarity >= 0.25:
            state = "topic_change"
            confidence = similarity * 0.9
            reason = "Medium similarity indicates topic change"
        else:
            state = "new_conversation"
            confidence = max(0.8, similarity * 0.9)
            reason = "Low similarity indicates new conversation"

        return {
            "conversationState": state,
            "similarityToPrevious": similarity,
            "detectedBy": "similarity",
            "confidence": confidence,
            "reason": reason
        }

    def _detect_context_shift(self, session_history: List[str]) -> bool:
        """Detect if topic shifted between consecutive messages."""
        if len(session_history) < 2:
            return False

        # Extract topics from messages
        last_topic = self._extract_topic(session_history[-2])
        current_topic = self._extract_topic(session_history[-1])

        return last_topic != current_topic

    def _extract_topic(self, message: str) -> str:
        """
        Extract topic from message using classifier.

        Returns topic category like "code", "task", "chat", "general"
        """
        try:
            # Call classifier to extract intent with examples
            prompt = f"""Extract the topic category from this message.

Categories:
- code: messages about programming, coding, scripts, functions, classes, python, javascript, debugging
- task: messages about work, jobs, todo lists, reminders, scheduling, deadlines
- chat: casual conversation, greetings, small talk, sharing information, asking questions
- general: messages that don't fit other categories

Examples:
"這是一個關於 Python 的示例" -> code
"你覺得這個代碼怎麼樣？" -> code
"我最近在學習 OpenClaw" -> chat
"今天天氣怎麼樣？" -> chat
"順便問一下，這個項目進度如何？" -> task
"你好，歡迎使用 Jarvis！" -> chat
"我在香港，今天有點冷" -> chat
"今天天氣不錯" -> chat

Now extract the topic for:
Message: {message}

Just return the category name (single word), no other text."""

            result = subprocess.run(
                ["ollama", "run", "qwen2.5:1.5b", prompt],
                input=message,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                topic = result.stdout.strip().lower()
                # Normalize topic
                topic_mapping = {
                    "coding": "code",
                    "code": "code",
                    "programming": "code",
                    "script": "code",
                    "function": "code",
                    "class": "code",
                    "python": "code",
                    "javascript": "code",
                    "git": "code",
                    "debug": "code",
                    "task": "task",
                    "work": "task",
                    "job": "task",
                    "todo": "task",
                    "remind": "task",
                    "schedule": "task",
                    "deadline": "task",
                    "chat": "chat",
                    "conversation": "chat",
                    "greeting": "chat",
                    "small talk": "chat",
                    "sharing": "chat",
                    "asking": "chat",
                    "question": "chat",
                    "hello": "chat",
                    "hi": "chat",
                    "你好": "chat",
                    "嗎": "chat",
                    "呢": "chat",
                    "今天": "chat",
                    "不錯": "chat",
                    "general": "general",
                    "other": "general"
                }
                return topic_mapping.get(topic, "general")
            else:
                # Fallback: try to guess from keywords
                message_lower = message.lower()
                if any(word in message_lower for word in ["代碼", "script", "code", "programming", "function", "class", "python", "javascript"]):
                    return "code"
                elif any(word in message_lower for word in ["任務", "task", "工作", "job", "todo", "remind", "schedule", "deadline"]):
                    return "task"
                elif any(word in message_lower for word in ["對話", "chat", "說", "談", "hi", "hello", "你好", "嗎", "呢"]):
                    return "chat"
                else:
                    return "general"

        except Exception as e:
            print(f"Error extracting topic: {e}", file=sys.stderr)
            return "general"

    def _calculate_semantic_similarity(self, user_input: str,
                                      session_history: List[str]) -> float:
        """
        Calculate semantic similarity between user input and session history.

        Uses ollama qwen2.5:1.5b to compute similarity scores.
        """
        if not session_history:
            return 0.0

        # Use the last message for similarity calculation
        last_message = session_history[-1]

        try:
            # Call classifier with similarity prompt (using Chinese for consistency)
            prompt = f"""請計算這兩則訊息的語義相似度（0.0-1.0）。

0.0 = 完全無關
0.3 = 話題不太相關
0.7 = 話題高度相關
1.0 = 話題完全相同

訊息1: {user_input}
訊息2: {last_message}

請只返回一個數字，不要其他文字。"""

            result = subprocess.run(
                ["ollama", "run", "qwen2.5:1.5b", prompt],
                input=user_input,
                capture_output=True,
                text=True,
                timeout=15  # Increased timeout
            )

            if result.returncode == 0 and result.stdout.strip():
                # Extract similarity score
                output = result.stdout.strip()
                
                # Try to extract similarity number from output
                import re
                
                # Method 1: Look for percentage (0.0-1.0) format
                match = re.search(r'(\d+\.?\d*)', output)
                if match:
                    try:
                        score_str = match.group(1)
                        # Remove any extra characters
                        score_str = re.sub(r'[^\d.]', '', score_str)
                        score = float(score_str)
                        if 0.0 <= score <= 1.0:
                            return score
                    except ValueError:
                        pass
                
                # Method 2: Look for just a number (0-1)
                match = re.search(r'^\s*(\d+\.?\d*)\s*$', output)
                if match:
                    try:
                        score = float(match.group(1))
                        if 0.0 <= score <= 1.0:
                            return score
                    except ValueError:
                        pass
                
                # Method 3: Simple heuristic based on response
                if "完全相同" in output or "高度相關" in output:
                    return 0.9
                elif "不太相關" in output or "相關" in output:
                    return 0.6
                elif "無關" in output:
                    return 0.2
                else:
                    # Default: assume medium similarity
                    return 0.5

                # Fallback: simple heuristic for short history
                # If model fails, use a simple similarity based on keywords
                user_words = set(user_input.split())
                last_words = set(last_message.split())
                common_words = user_words & last_words
                if common_words:
                    return 0.6
                else:
                    return 0.3

            return 0.3  # Default fallback

        except Exception as e:
            print(f"Error calculating similarity: {e}", file=sys.stderr)
            return 0.3

    def get_context_length(self, conversation_state: str) -> int:
        """Get recommended context length for each conversation state."""
        context_mapping = {
            "new_conversation": 500,
            "continuation": 1000,
            "topic_change": 500
        }
        return context_mapping.get(conversation_state, 500)


def main():
    """Main function for testing and CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Hybrid Content-Based Conversation State Detector'
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

    detector = ContentBasedDetectorHybrid()

    if args.session_file:
        # Extract messages from session
        messages = []
        try:
            with open(args.session_file, 'r', encoding='utf-8') as f:
                for line in f:
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
                            entry.get('content') or
                            str(entry.get('message', ''))
                        )
                        if message:
                            messages.append(message)
                    except json.JSONDecodeError:
                        continue

        except FileNotFoundError:
            print(f"Error: Session file not found: {args.session_file}", file=sys.stderr)
            return
    else:
        messages = []

    # Get user input if not provided
    user_input = args.user_input
    if not user_input:
        print(f"Reading session history: {len(messages)} messages")
        user_input = input("Enter your message: ")

    # Detect state
    result = detector.detect(user_input, messages)

    # Format output
    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.format == 'simple':
        print(f"Conversation State: {result['conversationState']}")
        print(f"Similarity: {result.get('similarityToPrevious', 0.0):.2f}")
        print(f"Detected by: {result.get('detectedBy', 'unknown')}")
        print(f"Confidence: {result.get('confidence', 0.0):.2f}")
    else:  # pretty
        print("=" * 80)
        print("Hybrid Strategy - Detection Result")
        print("=" * 80)
        print()
        print(f"Conversation State: {result['conversationState']}")
        print(f"Similarity to Previous: {result.get('similarityToPrevious', 0.0):.2f}")
        print(f"Detected by: {result.get('detectedBy', 'unknown')}")
        print(f"Confidence: {result.get('confidence', 0.0):.2f}")
        print(f"Context Length Recommendation: {detector.get_context_length(result['conversationState'])} tokens")
        print()
        print(f"Reason: {result.get('reason', '')}")
        print("=" * 80)


if __name__ == "__main__":
    main()
