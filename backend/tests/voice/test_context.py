"""
Unit tests for voice.context module.

Tests LLM conversation context factory.
"""

import pytest
from unittest.mock import patch, MagicMock

from backend.app.voice.context import create_context


class TestCreateContext:
    """Test create_context factory function."""

    def test_returns_openai_llm_context_instance(self, mock_openai_llm_context):
        """Test that function returns OpenAILLMContext instance."""
        messages = [{"role": "system", "content": "Test"}]
        result = create_context(messages)
        assert mock_openai_llm_context.called

    def test_passes_messages_to_context(self, mock_openai_llm_context):
        """Test that messages are passed to OpenAILLMContext."""
        messages = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
        ]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert call_args[0][0] == messages

    def test_empty_messages_list(self, mock_openai_llm_context):
        """Test with empty messages list."""
        messages = []

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert call_args[0][0] == []

    def test_single_message(self, mock_openai_llm_context):
        """Test with single message."""
        messages = [{"role": "system", "content": "You are a helpful assistant"}]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert len(call_args[0][0]) == 1

    def test_multiple_messages(self, mock_openai_llm_context):
        """Test with multiple messages."""
        messages = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Follow-up question"},
        ]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert len(call_args[0][0]) == 4

    @pytest.mark.parametrize("role", ["system", "user", "assistant"])
    def test_various_message_roles(self, mock_openai_llm_context, role):
        """Test with various message roles."""
        messages = [{"role": role, "content": f"{role} message"}]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert call_args[0][0][0]["role"] == role

    def test_context_instantiation_called_once(self, mock_openai_llm_context):
        """Test that OpenAILLMContext is instantiated once."""
        messages = [{"role": "system", "content": "Test"}]

        create_context(messages)

        assert mock_openai_llm_context.call_count == 1

    def test_messages_passed_as_first_positional_argument(self, mock_openai_llm_context):
        """Test that messages are first positional argument."""
        messages = [{"role": "system", "content": "Test"}]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        # Should be positional argument, not keyword
        assert len(call_args[0]) >= 1
        assert call_args[0][0] == messages


class TestContextIntegration:
    """Test context creation in realistic scenarios."""

    def test_medical_intake_conversation_start(self, mock_openai_llm_context):
        """Test context for medical intake conversation."""
        messages = [
            {
                "role": "system",
                "content": "You are a medical intake assistant. Keep responses brief for voice.",
            },
            {
                "role": "system",
                "content": "Greet the patient warmly and ask how you can help them today.",
            },
        ]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert len(call_args[0][0]) == 2

    def test_conversation_with_history(self, mock_openai_llm_context):
        """Test context with conversation history."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is your name?"},
            {"role": "assistant", "content": "I am MedVoice."},
            {"role": "user", "content": "Can you help me?"},
        ]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert len(call_args[0][0]) == 4

    def test_multiple_context_instances_independent(self, mock_openai_llm_context):
        """Test that multiple contexts are independent."""
        mock_openai_llm_context.reset_mock()

        messages1 = [{"role": "system", "content": "Context 1"}]
        messages2 = [{"role": "system", "content": "Context 2"}]

        create_context(messages1)
        create_context(messages2)

        assert mock_openai_llm_context.call_count == 2
        calls = mock_openai_llm_context.call_args_list
        assert calls[0][0][0] == messages1
        assert calls[1][0][0] == messages2


class TestCreateContextEdgeCases:
    """Test edge cases for context creation."""

    def test_message_with_empty_content(self, mock_openai_llm_context):
        """Test with message containing empty content."""
        messages = [{"role": "system", "content": ""}]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert call_args[0][0][0]["content"] == ""

    def test_message_with_very_long_content(self, mock_openai_llm_context):
        """Test with very long message content."""
        long_content = "x" * 10000
        messages = [{"role": "system", "content": long_content}]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert len(call_args[0][0][0]["content"]) == 10000

    def test_message_with_special_characters(self, mock_openai_llm_context):
        """Test with special characters in content."""
        messages = [
            {
                "role": "system",
                "content": "Special chars: !@#$%^&*()_+-=[]{}|;:',.<>?/~`",
            }
        ]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert "!@#$%^&*()" in call_args[0][0][0]["content"]

    def test_message_with_unicode_characters(self, mock_openai_llm_context):
        """Test with Unicode characters in content."""
        messages = [
            {
                "role": "system",
                "content": "Unicode: 你好世界 مرحبا العالم Здравствуй мир",
            }
        ]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert "你好世界" in call_args[0][0][0]["content"]

    def test_message_with_newlines(self, mock_openai_llm_context):
        """Test with newlines in message content."""
        multiline_content = "Line 1\nLine 2\nLine 3"
        messages = [{"role": "system", "content": multiline_content}]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert "\n" in call_args[0][0][0]["content"]

    def test_message_dict_structure_preserved(self, mock_openai_llm_context):
        """Test that message dictionary structure is preserved."""
        messages = [
            {
                "role": "user",
                "content": "Test message",
                "extra_field": "extra_value",  # Extra field
            }
        ]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        msg = call_args[0][0][0]
        assert msg["role"] == "user"
        assert msg["content"] == "Test message"
        assert msg["extra_field"] == "extra_value"

    def test_large_message_list(self, mock_openai_llm_context):
        """Test with large number of messages."""
        messages = [
            {"role": "system", "content": "System"},
            *[{"role": "user", "content": f"Message {i}"} for i in range(100)],
        ]

        create_context(messages)

        call_args = mock_openai_llm_context.call_args
        assert len(call_args[0][0]) == 101
