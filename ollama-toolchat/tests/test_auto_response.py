"""
Tests for auto-response functionality in query classifier
"""

import pytest
from src.toolchat.agent.query_classifier import (
    is_auto_response,
    get_auto_response,
    classify_query,
    AUTO_RESPONSE_PATTERNS,
    AUTO_RESPONSES
)


class TestAutoResponse:
    """Test auto-response functionality"""
    
    def test_auto_response_detection(self):
        """Test that auto-response queries are correctly identified"""
        auto_queries = [
            "what can you do",
            "What do you do?",
            "what are your capabilities",
            "help",
            "what tools do you have",
            "what are you for",
            "how can you help me",
            "what should i ask you",
            "features",
            "commands"
        ]
        
        for query in auto_queries:
            assert is_auto_response(query), f"Query should be auto-response: {query}"
            response = get_auto_response(query)
            assert response is not None, f"Should have response for: {query}"
            assert len(response) > 0, f"Response should not be empty for: {query}"
    
    def test_non_auto_response_detection(self):
        """Test that non-auto-response queries are correctly identified"""
        non_auto_queries = [
            "how much disk space do I have",
            "what's my cpu temperature",
            "check my memory usage",
            "tell me a joke",
            "what's the weather",
            "organize my photos",
            "show running processes"
        ]
        
        for query in non_auto_queries:
            assert not is_auto_response(query), f"Query should NOT be auto-response: {query}"
            response = get_auto_response(query)
            assert response is None, f"Should NOT have response for: {query}"
    
    def test_classify_query_with_auto_response(self):
        """Test that classify_query properly handles auto-responses"""
        query = "what can you do"
        requires_tool, suggested_tool = classify_query(query)
        
        assert requires_tool is True
        assert suggested_tool == "auto_response:capabilities"
    
    def test_auto_response_content(self):
        """Test that auto-response content contains expected information"""
        query = "what can you do"
        response = get_auto_response(query)
        
        assert "SELO HostPilot" in response
        assert "System Monitoring" in response
        assert "Storage & Files" in response
        assert "Network" in response
        assert "Hardware & Logs" in response
        assert "Security First" in response
    
    def test_case_insensitive_matching(self):
        """Test that auto-response matching is case insensitive"""
        queries = [
            "WHAT CAN YOU DO",
            "What Can You Do",
            "HeLp",
            "FEATURES"
        ]
        
        for query in queries:
            assert is_auto_response(query), f"Case insensitive matching failed for: {query}"
    
    def test_partial_matching(self):
        """Test that partial phrase matching works"""
        queries = [
            "what can you help me with",
            "what are your capabilities exactly",
            "tell me your features"
        ]
        
        for query in queries:
            assert is_auto_response(query), f"Partial matching failed for: {query}"
