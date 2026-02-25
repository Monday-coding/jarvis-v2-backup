#!/usr/bin/env python3
"""
Test script for Content-Based Conversation State Detector.
Tests various scenarios and edge cases.
"""

import sys
import json
from content_based_detector import ContentBasedDetector


class TestSuite:
    """Test suite for conversation state detector."""

    def __init__(self):
        self.detector = ContentBasedDetector()
        self.passed = 0
        self.failed = 0
        self.tests = []

    def run_test(self, name: str, user_input: str,
                 session_history: list,
                 expected_state: str) -> bool:
        """Run a single test case."""
        result = self.detector.detect(user_input, session_history)

        passed = result["conversationState"] == expected_state
        confidence = result.get("confidence", 0.0)

        test_result = {
            "name": name,
            "passed": passed,
            "expected": expected_state,
            "actual": result["conversationState"],
            "similarity": result.get("similarityToPrevious", 0.0),
            "detectedBy": result.get("detectedBy", "unknown"),
            "confidence": confidence,
            "reason": result.get("reason", "")
        }

        self.tests.append(test_result)

        if passed:
            self.passed += 1
            print(f"✅ PASS: {name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {name}")
            print(f"   Expected: {expected_state}, Got: {result['conversationState']}")
            print(f"   Similarity: {result.get('similarityToPrevious', 0.0)}")
            print(f"   Detected by: {result.get('detectedBy', 'unknown')}")

        return passed

    def run_all_tests(self):
        """Run all test cases."""
        print("=" * 80)
        print("Content-Based Conversation State Detector - Test Suite")
        print("=" * 80)
        print()

        # Test 1: Continuation (Medium-High Similarity)
        self.run_test(
            "Continuation - High similarity",
            user_input="今天天氣怎麼樣？",
            session_history=[
                "你好，今天天氣怎麼樣？",
                "我在香港，今天有點冷"
            ],
            expected_state="continuation"
        )

        # Test 2: New Conversation (Low Similarity)
        self.run_test(
            "New Conversation - Low similarity",
            user_input="你好，請問你叫什麼名字？",
            session_history=[
                "昨天我在香港吃的燒鵝很好吃"
            ],
            expected_state="new_conversation"
        )

        # Test 3: Topic Change (Keyword)
        self.run_test(
            "Topic Change - Keyword detected",
            user_input="然後呢，接著說什麼？",
            session_history=[
                "這是一個關於 Python 的示例"
            ],
            expected_state="topic_change"
        )

        # Test 4: Topic Change (Context Shift)
        self.run_test(
            "Topic Change - Context shift",
            user_input="順便問一下，這個項目進度如何？",
            session_history=[
                "這是一個關於 Python 的示例",
                "你覺得這個代碼怎麼樣？"
            ],
            expected_state="topic_change"
        )

        # Test 5: Continuation (Medium Similarity)
        self.run_test(
            "Continuation - Medium similarity",
            user_input="需要我幫你查一下嗎？",
            session_history=[
                "你好，今天天氣怎麼樣？",
                "我在香港，今天有點冷"
            ],
            expected_state="continuation"
        )

        # Test 6: Empty History
        self.run_test(
            "New Conversation - Empty history",
            user_input="你好，我是新用戶",
            session_history=[],
            expected_state="new_conversation"
        )

        # Test 7: Multiple Keywords
        self.run_test(
            "Topic Change - Multiple keywords",
            user_input="另外，順便問一下你覺得這個怎麼樣？然後呢？",
            session_history=[
                "今天天氣不錯"
            ],
            expected_state="topic_change"
        )

        # Test 8: Chat Topic (Continuation)
        self.run_test(
            "Chat Topic - Continuation",
            user_input="最近有什麼新消息嗎？",
            session_history=[
                "我最近在學習 OpenClaw",
                "這個系統很有趣"
            ],
            expected_state="continuation"
        )

        # Test 9: Code Topic (Continuation)
        self.run_test(
            "Code Topic - Continuation",
            user_input="怎麼優化這個函數的性能？",
            session_history=[
                "這是一個關於 Python 的示例",
                "你覺得這個代碼怎麼樣？"
            ],
            expected_state="continuation"
        )

        # Print summary
        print()
        print("=" * 80)
        print("Test Summary")
        print("=" * 80)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Success Rate: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print()

        if self.failed > 0:
            print("Failed Tests Details:")
            print("-" * 80)
            for test in self.tests:
                if not test["passed"]:
                    print(f"❌ {test['name']}")
                    print(f"   Expected: {test['expected']}, Got: {test['actual']}")
                    print(f"   Similarity: {test['similarity']}")
                    print(f"   Detected by: {test['detectedBy']}")
                    print(f"   Confidence: {test['confidence']}")
                    print(f"   Reason: {test['reason']}")
                    print()

        return self.failed == 0


def test_real_scenario():
    """Test with real session history."""
    print("=" * 80)
    print("Real Scenario Test")
    print("=" * 80)
    print()

    detector = ContentBasedDetector()

    # Simulate a real conversation
    print("Conversation History:")
    history = [
        "你好，歡迎使用 Jarvis！我是你的 AI 助手。",
        "今天有什麼我可以幫你的嗎？"
    ]

    for i, msg in enumerate(history, 1):
        print(f"{i}. {msg}")

    print()
    print("New Message:")
    user_input = input("Enter your message: ")

    result = detector.detect(user_input, history)

    print()
    print("Detection Result:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()
    print(f"Context Length Recommendation: {detector.get_context_length(result['conversationState'])} tokens")


def main():
    """Main test runner."""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--real":
            test_real_scenario()
        elif sys.argv[1] == "--help":
            print("Usage: python test_detector.py [options]")
            print("  --test         Run automated test suite")
            print("  --real         Interactive real scenario test")
            print("  --help         Show this help message")
        else:
            print("Unknown option. Use --help for usage information.")
            sys.exit(1)
    else:
        test_suite = TestSuite()
        success = test_suite.run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
