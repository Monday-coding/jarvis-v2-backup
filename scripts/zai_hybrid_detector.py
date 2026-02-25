#!/usr/bin/env python3
"""
Hybrid Conversation State Detector with z.ai API Integration.
Combines local qwen2.5:1.5b (free) with z.ai API (paid, more accurate).
"""

import json
import sys
import os
import subprocess
from typing import Dict, List, Optional, Tuple
from zhipuai import ZhipuAI


class HybridDetector:
    """Hybrid detector with z.ai API integration for difficult cases."""

    def __init__(self, zai_api_key: str = None):
        """Initialize detector with z.ai API key."""
        if zai_api_key is None:
            # Try to get from environment
            zai_api_key = os.environ.get("ZAI_API_KEY")
        
        self.zai_client = ZhipuAI(api_key=zai_api_key) if zai_api_key else None
        self.zai_confidence_threshold = 0.7  # Only trust z.ai if confidence > 0.7
        
        # Keywords for high priority detection
        self.high_priority_keywords = [
            "然後呢", "接著說", "順便問一下", "另外", "說起來", 
            "話說", "換話題", "話題轉換"
        ]
        
        # Medium priority keywords (removed to reduce false positives)
        # Moved to low priority to be ignored

        # Low priority keywords (conversational particles - should NOT trigger topic change)
        self.low_priority_keywords = [
            "什麼", "怎麼", "嗎", "呢"
        ]

    def _is_difficult_case(self, user_input: str) -> bool:
        """Detect if this is a difficult case that needs zai."""
        difficult_patterns = [
            "代碼", "程式", "算法", "優化", "函數", "類", 
            "對象", "實例", "模式", "架構", "流程", "步驟"
        ]
        
        return any(pattern in user_input for pattern in difficult_patterns)

    def extract_topic_qwen(self, message: str) -> str:
        """Extract topic using local qwen."""
        try:
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
                # Fallback: guess from keywords
                message_lower = message.lower()
                if any(word in message_lower for word in ["代碼", "script", "code", "programming", "function"]):
                    return "code"
                elif any(word in message_lower for word in ["任務", "task", "工作", "job", "todo", "remind"]):
                    return "task"
                elif any(word in message_lower for word in ["對話", "chat", "說", "談", "hi", "hello", "你好", "嗎", "呢"]):
                    return "chat"
                else:
                    return "general"

        except Exception as e:
            print(f"Error extracting topic: {e}", file=sys.stderr)
            return "general"

    def calculate_similarity_qwen(self, user_input: str, session_history: List[str]) -> float:
        """Calculate semantic similarity using local qwen."""
        if not session_history:
            return 0.0

        last_message = session_history[-1]

        try:
            prompt = f"""計算這兩則訊息的語義相似度（0.0-1.0）。

0.0 = 完全無關
1.0 = 高度相關

訊息1: {user_input}
訊息2: {last_message}

只返回一個數字，不要其他文字。
"""

            result = subprocess.run(
                ["ollama", "run", "qwen2.5:1.5b", prompt],
                input=user_input,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                # Extract similarity score
                output = result.stdout.strip()
                
                # Try to extract number using multiple patterns
                import re
                
                # Pattern 1: Decimal format (0.00-1.00)
                match = re.search(r'(\d+\.\d+)', output)
                if match:
                    try:
                        score = float(match.group(1))
                        return min(max(score, 0.0), 1.0)
                    except ValueError:
                        pass
                
                # Pattern 2: Just a number
                match = re.search(r'^\s*(\d+\.?\d*)\s*$', output)
                if match:
                    try:
                        score = float(match.group(1))
                        return min(max(score, 0.0), 1.0)
                    except ValueError:
                        pass
                
                # Pattern 3: Percentage format (85%)
                match = re.search(r'(\d+)%', output)
                if match:
                    try:
                        score = float(match.group(1)) / 100.0
                        return min(max(score, 0.0), 1.0)
                    except ValueError:
                        pass
                
                # Pattern 4: Descriptive text
                if "完全相同" in output or "高度相關" in output:
                    return 0.9
                elif "不太相關" in output or "中度相關" in output:
                    return 0.6
                elif "無關" in output or "不太相關" in output:
                    return 0.3
                elif "很不同" in output or "完全不關" in output:
                    return 0.1

            # Fallback: simple heuristic for short history
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

    def call_zai_api(self, user_input: str, session_history: List[str]) -> Dict:
        """Call z.ai API for classification and similarity."""
        if not self.zai_client:
            return {
                "error": "Z.ai client not initialized",
                "state": None,
                "confidence": 0.0,
                "similarity": 0.0
            }

        try:
            # Prepare input for z.ai
            history_text = "\n".join(session_history[-3:])  # Last 3 messages
            
            prompt = f"""
你是一個智能對話狀態檢測助手。

請分析以下對話並判斷對話狀態：
1. new_conversation - 完全新對話，無關聯
2. continuation - 續接對話，話題相同或高度相關
3. topic_change - 話題轉換，話題不同但相關
4. 其他

對話歷史：
{history_text}

當前用戶輸入：
{user_input}

請返回 JSON 格式：
{{
  "state": "new_conversation" | "continuation" | "topic_change",
  "confidence": 0.0-1.0 (置信度),
  "similarity": 0.0-1.0 (相似度),
  "reason": "判斷理由"
  "detected_topic": "code" | "task" | "chat" | "general"
}}
"""

            response = self.zai_client.chat.invoke(
                model="zhipu-embedding-v3",  # Use embedding model for similarity
                messages=[{"role": "user", "content": prompt}]
            )

            return {
                "error": None,
                "state": None,
                "confidence": 0.0,
                "similarity": 0.0,
                "zai_response": response
            }

        except Exception as e:
            return {
                "error": str(e),
                "state": None,
                "confidence": 0.0,
                "similarity": 0.0
            }

    def detect(self, user_input: str, session_history: List[str], use_zai: bool = False) -> Dict:
        """
        Hybrid detection with intelligent z.ai API integration.
        
        Strategy:
        1. Keyword detection (HIGHEST PRIORITY) - most reliable
        2. Topic shift detection (MEDIUM) - context-aware
        3. Similarity calculation (LOWEST PRIORITY) - qwen local
        4. Zai API (OPTIONAL) - only for difficult cases or low confidence
        
        Args:
            user_input: Current user message
            session_history: Conversation history
            use_zai: Force use z.ai API (for testing)
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
        for keyword in self.high_priority_keywords:
            if keyword in user_input:
                return {
                    "conversationState": "topic_change",
                    "similarityToPrevious": 0.0,
                    "detectedBy": "keyword_high",
                    "confidence": 0.95,
                    "reason": f"High-priority keyword '{keyword}' detected"
                }

        # Step 3: Topic shift detection (MEDIUM)
        topic1 = self.extract_topic_qwen(session_history[-2])
        topic2 = self.extract_topic_qwen(session_history[-1])
        topic_shift = (topic1 != topic2)
        
        if topic_shift:
            return {
                "conversationState": "topic_change",
                "similarityToPrevious": 0.0,
                "detectedBy": "topic_shift",
                "confidence": 0.85,
                "reason": f"Topic shift: {topic1} → {topic2}"
            }

        # Step 4: Similarity calculation (LOWEST PRIORITY - LOCAL)
        similarity = self.calculate_similarity_qwen(user_input, session_history)

        # Determine if we should use zai
        should_use_zai = (
            use_zai or  # Force use zai
            self._is_difficult_case(user_input) or  # Difficult topics
            (similarity is None or similarity < 0.5)  # Low confidence in local
        )

        # Step 5: Zai API call (if needed)
        zai_result = None
        if should_use_zai:
            zai_result = self.call_zai_api(user_input, session_history)
            
            if zai_result.get("error"):
                # Zai failed, use local result
                pass
            else:
                # Check if zai is confident enough
                try:
                    zai_content = zai_result.get("zai_response", {})
                    if isinstance(zai_content, str):
                        import json
                        zai_data = json.loads(zai_content)
                    elif hasattr(zai_content, 'content'):
                        zai_data = {
                            "content": zai_content.content,
                            "usage": getattr(zai_content, 'usage', {})
                        }
                    
                    zai_confidence = float(zai_data.get("confidence", 0.5))
                    
                    if zai_confidence > self.zai_confidence_threshold:
                        # Trust zai's judgment
                        similarity = float(zai_data.get("similarity", similarity))
                        
                        # Map zai state to our state
                        zai_state = zai_data.get("state", "continuation")
                        if zai_state == "topic_change":
                            detected_state = "topic_change"
                        elif zai_state == "new_conversation":
                            detected_state = "new_conversation"
                        else:
                            detected_state = "continuation"
                        
                        return {
                            "conversationState": detected_state,
                            "similarityToPrevious": similarity,
                            "detectedBy": "zai_api",
                            "confidence": zai_confidence,
                            "similarity": similarity,
                            "reason": f"Z.ai API (confidence: {zai_confidence:.2f})"
                        }
                except Exception:
                    # Parsing failed, use local result
                    pass

        # Step 6: Make final decision based on priority
        if zai_result and not zai_result.get("error") and zai_result.get("detectedBy") == "zai_api":
            # Zai API succeeded, use its result
            pass
        else:
            # Use local similarity result
            if similarity >= 0.65:
                state = "continuation"
                confidence = similarity
                reason = "High semantic similarity indicates continuation"
            elif similarity >= 0.45:
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
            "detectedBy": "zai_api" if (zai_result and not zai_result.get("error")) else "similarity",
            "confidence": confidence,
            "reason": reason
        }

    def get_context_length(self, conversation_state: str) -> int:
        """Get recommended context length for each conversation state."""
        context_mapping = {
            "new_conversation": 500,
            "continuation": 1000,
            "topic_change": 500
        }
        return context_mapping.get(conversation_state, 500)


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Hybrid Content-Based Conversation State Detector with z.ai API'
    )

    parser.add_argument(
        '--use-zai',
        action='store_true',
        help='Force use z.ai API for detection'
    )

    parser.add_argument(
        '--test-zai',
        action='store_true',
        help='Test z.ai API connectivity'
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

    args = parser.parse_args()

    if args.test_zai:
        # Test z.ai API
        if not os.environ.get("ZAI_API_KEY"):
            print("⚠️  ZAI_API_KEY not found in environment")
            print("   Please set ZAI_API_KEY environment variable")
            sys.exit(1)
        
        detector = HybridDetector()
        print("🔧 Testing z.ai API...")
        
        test_input = "請分析這段對話的狀態：\n\nUser: 今天天氣怎麼樣？\n\nAssistant: 我在香港，今天有點冷。"
        
        result = detector.detect(test_input, ["User: 今天天氣怎麼樣？", "Assistant: 我在香港，今天有點冷。"], use_zai=True)
        
        print(f"📊 Z.ai Result:")
        print(f"   State: {result.get('conversationState', 'N/A')}")
        print(f"   Confidence: {result.get('confidence', 'N/A'):.2f}")
        print(f"   Reason: {result.get('reason', 'N/A')}")
        
        if result.get("error"):
            print(f"   Error: {result['error']}")
        else:
            print(f"   Detected by: {result.get('detectedBy', 'N/A')}")
        
        sys.exit(0)

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
            print(f"❌ Error: Session file not found: {args.session_file}", file=sys.stderr)
            return
        except Exception as e:
            print(f"❌ Error reading session file: {e}", file=sys.stderr)
            return

        # Get user input if not provided
        user_input = args.user_input
        if not user_input:
            print(f"Reading session history: {len(messages)} messages")
            user_input = input("Enter your message: ")

        # Detect state
        detector = HybridDetector()
        result = detector.detect(user_input, messages, args.use_zai)

        # Format output
        print("=" * 80)
        print("Hybrid Detector - z.ai Integration")
        print("=" * 80)
        print()
        print(f"Conversation State: {result['conversationState']}")
        print(f"Similarity to Previous: {result.get('similarityToPrevious', 0.0):.2f}")
        print(f"Detected by: {result.get('detectedBy', 'unknown')}")
        print(f"Confidence: {result.get('confidence', 0.0):.2f}")
        print()
        print(f"Reason: {result.get('reason', '')}")
        print("=" * 80)
        print()
        print(f"Context Length Recommendation: {detector.get_context_length(result['conversationState'])} tokens")
        print()
        if result.get("error"):
            print(f"⚠️  Z.ai Error: {result['error']}")

        return


if __name__ == "__main__":
    main()
