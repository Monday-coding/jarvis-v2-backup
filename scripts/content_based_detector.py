#!/usr/bin/env python3
"""
Content-Based Conversation State Detector
Detects conversation state based on semantic similarity and topic shifts.
"""

import json
import sys
import subprocess
from typing import Dict, List, Optional, Tuple


class ContentBasedDetector:
    """Detect conversation state using content analysis."""

    def __init__(self):
        self.keywords = [
            "然後呢",
            "接著說",
            "順便問一下",
            "另外",
            "說起來",
            "話說"
        ]

    def detect(self,
               user_input: str,
               session_history: List[str],
               session_key: str = "") -> Dict:
        """
        Detect conversation state based on content analysis.

        Args:
            user_input: Current user message
            session_history: List of previous messages (last 10 messages recommended)
            session_key: Current session key for fallback

        Returns:
            Dict with conversation state and related metrics
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

        # Step 2: Semantic similarity calculation
        similarity = self._calculate_semantic_similarity(user_input, session_history)

        # Step 3: Determine state based on similarity (MAIN DECISION)
        # Using adjusted thresholds for qwen2.5:1.5b
        if similarity >= 0.30:
            return {
                "conversationState": "continuation",
                "similarityToPrevious": similarity,
                "detectedBy": "content_similarity",
                "confidence": similarity,
                "reason": "High semantic similarity indicates continuation"
            }
        elif similarity >= 0.20:
            return {
                "conversationState": "topic_change",
                "similarityToPrevious": similarity,
                "detectedBy": "content_similarity",
                "confidence": similarity * 0.9,
                "reason": "Medium similarity indicates topic change"
            }
        else:
            # Low similarity → continue with keyword/context checks
            pass

        # Step 4: Keyword pattern matching
        has_keyword_change, keyword = self._detect_keyword_topic_change(user_input)
        if has_keyword_change:
            return {
                "conversationState": "topic_change",
                "similarityToPrevious": similarity,
                "detectedBy": "keyword_pattern",
                "confidence": 0.85,
                "keyword": keyword,
                "reason": f"Keyword '{keyword}' detected"
            }

        # Step 5: Context shift detection
        has_context_shift = self._detect_context_shift(session_history)
        if has_context_shift:
            return {
                "conversationState": "topic_change",
                "similarityToPrevious": similarity,
                "detectedBy": "context_shift",
                "confidence": 0.82,
                "reason": "Topic shift detected"
            }

        # Step 6: Fallback - session key check
        # This would require tracking previous session keys
        # For now, this is fallback only
        return {
            "conversationState": "new_conversation",
            "similarityToPrevious": similarity,
            "detectedBy": "content_similarity",
            "confidence": max(0.8, similarity * 0.9),
            "reason": "Low similarity indicates new conversation"
        }

    def _detect_keyword_topic_change(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """Detect keyword patterns that indicate topic change."""
        for keyword in self.keywords:
            if keyword in user_input:
                return True, keyword
        return False, None

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
                    "chat": "chat",
                    "conversation": "chat",
                    "task": "task",
                    "work": "task",
                    "job": "task",
                    "todo": "task",
                    "remind": "task",
                    "schedule": "task",
                    "deadline": "task",
                    "general": "general",
                    "other": "general"
                }
                return topic_mapping.get(topic, "general")
            else:
                # Fallback: try to guess from keywords
                message_lower = message.lower()
                if any(word in message_lower for word in ["代碼", "script", "code", "programming", "function", "class", "python", "javascript", "git", "debug"]):
                    return "code"
                elif any(word in message_lower for word in ["任務", "task", "工作", "job", "todo", "remind", "schedule", "deadline"]):
                    return "task"
                elif any(word in message_lower for word in ["對話", "chat", "說", "談", "hi", "hello", "你好", "嗎"]):
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
            prompt = f"""計算相似度分數（0-1）：

用戶: {user_input}
上一條訊息: {last_message}

只返回 0 到 1 之間的相似度分數，不要其他文字。"""

            result = subprocess.run(
                ["ollama", "run", "qwen2.5:1.5b", prompt],
                input=user_input,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                # Extract similarity score
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    # Try to extract number
                    import re
                    match = re.search(r'(\d+\.?\d*)', line)
                    if match:
                        try:
                            score = float(match.group(1))
                            return min(max(score, 0.0), 1.0)
                        except ValueError:
                            continue

            # Fallback: simple keyword matching for short history
            if len(session_history) == 1:
                user_words = set(user_input.split())
                last_words = set(last_message.split())
                common_words = user_words & last_words
                if common_words:
                    return min(0.7, len(common_words) / max(len(user_words), 1) * 2)

            return 0.5  # Default fallback

        except Exception as e:
            print(f"Error calculating similarity: {e}", file=sys.stderr)
            return 0.5

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
    detector = ContentBasedDetector()

    # Example usage
    user_input = "今天天氣怎麼樣？"
    session_history = [
        "你好，今天天氣怎麼樣？",
        "我在香港，今天有點冷",
        "需要我幫你查一下嗎？"
    ]

    result = detector.detect(user_input, session_history)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Allow file-based input
        if sys.argv[1] == "--test":
            main()
    else:
        main()
