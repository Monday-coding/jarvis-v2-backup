#!/usr/bin/env python3
"""
Test script for Hybrid Content-Based Conversation State Detector.
Tests various scenarios and edge cases with improved priority strategy.
"""

import sys
import json
from content_based_detector_v2 import ContentBasedDetectorHybrid


class TestSuite:
    """Test suite for hybrid conversation state detector."""

    def __init__(self):
        self.detector = ContentBasedDetectorHybrid()
        self.passed = 0
        self.failed = 0
        self.tests = []

    def run_test(self, name: str, user_input: str,
                 session_history: list,
                 expected_state: str,
                 expected_method: str) -> bool:
        """Run a single test case."""
        result = self.detector.detect(user_input, session_history)

        passed = (result["conversationState"] == expected_state)
        method_match = (result["detectedBy"] == expected_method)
        full_match = passed and method_match

        test_result = {
            "name": name,
            "passed": full_match,
            "expected_state": expected_state,
            "actual_state": result["conversationState"],
            "expected_method": expected_method,
            "actual_method": result["detectedBy"],
            "similarity": result.get("similarityToPrevious", 0.0),
            "confidence": result.get("confidence", 0.0),
            "reason": result.get("reason", "")
        }

        self.tests.append(test_result)

        if full_match:
            self.passed += 1
            print(f"✅ PASS: {name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {name}")
            if not passed:
                print(f"   Expected: {expected_state}, Got: {result['conversationState']}")
            if not method_match:
                print(f"   Expected method: {expected_method}, Got: {result['detectedBy']}")
            print(f"   Similarity: {result.get('similarityToPrevious', 0.0):.2f}")
            print(f"   Detected by: {result.get('detectedBy', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0.0):.2f}")

        return full_match

    def run_all_tests(self):
        """Run all test cases."""
        print("=" * 80)
        print("Hybrid Strategy - Test Suite")
        print("=" * 80)
        print()

        # Test 1: Continuation (High similarity) - DEPENDS ON SIMILARITY
        # Since similarity is unreliable, this test may fail
        # But the message doesn't have topic change keywords
        self.run_test(
            "Continuation - High similarity",
            user_input="今天天氣怎麼樣？",
            session_history=[
                "你好，今天天氣怎麼樣？",
                "我在香港，今天有點冷"
            ],
            expected_state="continuation",
            expected_method="similarity"  # May fail due to similarity issues
        )

        # Test 2: New Conversation (Low similarity) - DEPENDS ON SIMILARITY
        # This tests if a completely unrelated topic is detected
        self.run_test(
            "New Conversation - Low similarity",
            user_input="你好，請問你叫什麼名字？",
            session_history=[
                "昨天我在香港吃的燒鵝很好吃"
            ],
            expected_state="new_conversation",
            expected_method="similarity"  # May fail due to similarity issues
        )

        # Test 3: Topic Change (Keyword - High Priority)
        self.run_test(
            "Topic Change - Keyword (High)",
            user_input="然後呢，接著說什麼？",
            session_history=[
                "這是一個關於 Python 的示例"
            ],
            expected_state="topic_change",
            expected_method="keyword_high"
        )

        # Test 4: Topic Change (Keyword - Medium Priority)
        self.run_test(
            "Topic Change - Keyword (Medium)",
            user_input="怎麼優化這個函數的性能？",
            session_history=[
                "這是一個關於 Python 的示例"
            ],
            expected_state="topic_change",
            expected_method="keyword_medium"
        )

        # Test 5: Topic Change (Context Shift)
        self.run_test(
            "Topic Change - Context Shift",
            user_input="順便問一下，這個項目進度如何？",
            session_history=[
                "這是一個關於 Python 的示例",
                "你覺得這個代碼怎麼樣？"
            ],
            expected_state="topic_change",
            expected_method="topic_shift"
        )

        # Test 6: Continuation (Medium Similarity) - DEPENDS ON SIMILARITY
        # Tests if continuing conversation is detected
        # Note: "需要我幫你查一下嗎？" contains "需要" (removed from medium)
        # so it may pass if not filtered by low priority
        self.run_test(
            "Continuation - Medium Similarity",
            user_input="需要我幫你查一下嗎？",
            session_history=[
                "你好，今天天氣怎麼樣？",
                "我在香港，今天有點冷"
            ],
            expected_state="continuation",
            expected_method="similarity"  # May fail due to similarity issues
        )

        # Test 7: Empty History
        self.run_test(
            "New Conversation - Empty History",
            user_input="你好，我是新用戶",
            session_history=[],
            expected_state="new_conversation",
            expected_method="empty_history"
        )

        # Test 8: Multiple Keywords
        self.run_test(
            "Topic Change - Multiple Keywords",
            user_input="另外，順便問一下你覺得這個怎麼樣？然後呢？",
            session_history=[
                "今天天氣不錯"
            ],
            expected_state="topic_change",
            expected_method="keyword_high"
        )

        # Test 9: Chat Topic (Continuation) - DEPENDS ON SIMILARITY
        # Tests if chat continuation is detected
        # Note: "最近有什麼新消息嗎？" contains "什麼" and "嗎" (removed from medium)
        # These are now in low priority and will be ignored
        # This is correct behavior - they are conversational particles
        self.run_test(
            "Chat Topic - Continuation",
            user_input="最近有什麼新消息嗎？",
            session_history=[
                "我最近在學習 OpenClaw",
                "這個系統很有趣"
            ],
            expected_state="continuation",
            expected_method="ignored_low_priority"  # May be detected by similarity instead
        )

        # Test 10: Code Topic (Continuation) - DEPENDS ON SIMILARITY
        # Tests if code continuation is detected
        # Note: "怎麼寫這個函數？" contains "怎麼" (removed from medium)
        # This is now in low priority and will be ignored
        # This is correct behavior - "怎麼" is a conversational particle
        self.run_test(
            "Code Topic - Continuation",
            user_input="怎麼寫這個函數？",
            session_history=[
                "這是一個關於 Python 的示例",
                "你覺得這個代碼怎麼樣？"
            ],
            expected_state="continuation",
            expected_method="ignored_low_priority"  # May be detected by similarity instead
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
                    print(f"   Expected state: {test['expected_state']}, Got: {test['actual_state']}")
                    print(f"   Expected method: {test['expected_method']}, Got: {test['actual_method']}")
                    print(f"   Similarity: {test['similarity']:.2f}")
                    print(f"   Detected by: {test['actual_method']}")
                    print(f"   Confidence: {test['confidence']:.2f}")
                    print(f"   Reason: {test['reason']}")

        return self.failed == 0


def test_real_scenario():
    """Test with real session history."""
    print("=" * 80)
    print("Real Scenario Test - Hybrid Strategy")
    print("=" * 80)
    print()

    detector = ContentBasedDetectorHybrid()

    # Simulate a real conversation
    print("Conversation History:")
    history = [
        "你好，歡迎使用 Jarvis！",
        "今天有什麼我可以幫你的嗎？"
    ]

    for i, msg in enumerate(history, 1):
        print(f"  {i}. {msg}")

    print()
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
            print("Usage: python test_detector_v2.py [options]")
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
