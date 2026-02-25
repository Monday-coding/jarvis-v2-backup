#!/usr/bin/env python3
"""
Test script for z.ai API integration.
Tests connectivity and hybrid detection strategy.
"""

import sys
import os
from zai_hybrid_detector import HybridDetector


class ZaiTestSuite:
    """Test suite for z.ai API integration."""

    def __init__(self):
        self.detector = HybridDetector()
        self.passed = 0
        self.failed = 0
        self.tests = []

    def test_zai_connectivity(self):
        """Test if z.ai API is accessible."""
        print("=" * 80)
        print("Testing z.ai API Connectivity")
        print("=" * 80)
        print()

        zai_key = os.environ.get("ZAI_API_KEY")
        if not zai_key:
            print("❌ FAIL: ZAI_API_KEY not found in environment")
            print("   Please set ZAI_API_KEY environment variable")
            return False

        print(f"✅ API Key found: {zai_key[:8]}...{zai_key[-4:]}")

        try:
            from zhipuai import ZhipuAI
            client = ZhipuAI(api_key=zai_key)
            
            # Test with a simple chat call
            response = client.chat.invoke(
                model="zhipu-embedding-v3",
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            print("✅ PASS: z.ai API is accessible")
            print(f"   Response received: {response}")
            return True
            
        except Exception as e:
            print(f"❌ FAIL: z.ai API error: {e}")
            return False

    def test_hybrid_detection_with_zai(self):
        """Test hybrid detection with z.ai API."""
        print()
        print("=" * 80)
        print("Testing Hybrid Detection with z.ai")
        print("=" * 80)
        print()

        test_cases = [
            {
                "name": "Continuation (High Similarity)",
                "input": "今天天氣怎麼樣？",
                "history": [
                    "你好，今天天氣怎麼樣？",
                    "我在香港，今天有點冷"
                ],
                "expected_state": "continuation"
            },
            {
                "name": "Topic Change (Context Shift)",
                "input": "順便問一下，這個項目進度如何？",
                "history": [
                    "這是一個關於 Python 的示例",
                    "你覺得這個代碼怎麼樣？"
                ],
                "expected_state": "topic_change"
            },
            {
                "name": "New Conversation (Different Topic)",
                "input": "你好，請問你叫什麼名字？",
                "history": [
                    "昨天我在香港吃的燒鵝很好吃"
                ],
                "expected_state": "new_conversation"
            },
            {
                "name": "Code Topic (Continuation)",
                "input": "怎麼優化這個函數的性能？",
                "history": [
                    "這是一個關於 Python 的示例",
                    "你覺得這個代碼怎麼樣？"
                ],
                "expected_state": "continuation"
            }
        ]

        for test in test_cases:
            result = self.detector.detect(
                test["input"],
                test["history"],
                use_zai=True  # Force use z.ai API
            )

            passed = (result["conversationState"] == test["expected_state"])
            method = result.get("detectedBy", "unknown")
            is_zai = (method == "zai_api")

            self.tests.append({
                "name": test["name"],
                "passed": passed,
                "is_zai": is_zai,
                "expected_state": test["expected_state"],
                "actual_state": result["conversationState"],
                "detected_by": method,
                "confidence": result.get("confidence", 0.0),
                "reason": result.get("reason", "")
            })

            if passed:
                self.passed += 1
                api_indicator = "🌐 z.ai" if is_zai else "💻 Local"
                print(f"✅ PASS: {test['name']} ({api_indicator})")
            else:
                self.failed += 1
                api_indicator = "🌐 z.ai" if is_zai else "💻 Local"
                print(f"❌ FAIL: {test['name']} ({api_indicator})")
                print(f"   Expected: {test['expected_state']}, Got: {result['conversationState']}")
                print(f"   Detected by: {method}")
                print(f"   Confidence: {result.get('confidence', 0.0):.2f}")

        return self.failed == 0

    def run_all_tests(self):
        """Run all tests."""
        print("=" * 80)
        print("z.ai Integration Test Suite")
        print("=" * 80)
        print()

        # Test 1: API Connectivity
        if not self.test_zai_connectivity():
            print()
            print("⚠️  Skipping hybrid detection tests - API not accessible")
            return False

        # Test 2: Hybrid Detection
        success = self.test_hybrid_detection_with_zai()

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

        zai_count = sum(1 for t in self.tests if t.get("is_zai", False))
        print(f"z.ai API Usage: {zai_count}/{len(self.tests)} calls ({zai_count/len(self.tests)*100:.0f}%)")
        print()

        if self.failed > 0:
            print("Failed Tests Details:")
            print("-" * 80)
            for test in self.tests:
                if not test["passed"]:
                    zai_indicator = "🌐 z.ai" if test.get("is_zai", False) else "💻 Local"
                    print(f"❌ {test['name']} ({zai_indicator})")
                    print(f"   Expected: {test['expected_state']}, Got: {test['actual_state']}")
                    print(f"   Detected by: {test['detected_by']}")

        return self.failed == 0


def main():
    """Main test runner."""
    import sys

    print("=" * 80)
    print("z.ai Integration Test Suite")
    print("=" * 80)
    print()
    print("📋 Available Tests:")
    print("  1. Test z.ai API connectivity")
    print("  2. Test hybrid detection with z.ai")
    print()

    test_suite = ZaiTestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
