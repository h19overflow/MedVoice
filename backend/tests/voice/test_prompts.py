"""
Unit tests for voice.llm.prompts module.

Tests prompt generation and message formatting.
"""

import pytest

from backend.app.voice.llm.prompts import (
    MEDICAL_INTAKE_PROMPT,
    get_system_message,
    get_greeting_message,
)


class TestPromptConstants:
    """Test prompt constant values."""

    def test_medical_intake_prompt_exists(self):
        """Test that medical intake prompt is defined."""
        assert MEDICAL_INTAKE_PROMPT
        assert isinstance(MEDICAL_INTAKE_PROMPT, str)

    def test_medical_intake_prompt_contains_key_terms(self):
        """Test that medical prompt contains relevant keywords."""
        prompt = MEDICAL_INTAKE_PROMPT
        assert "medical" in prompt.lower()
        assert "patient" in prompt.lower() or "information" in prompt.lower()
        assert "voice" in prompt.lower() or "conversation" in prompt.lower()

    def test_medical_intake_prompt_is_voice_focused(self):
        """Test that prompt mentions voice/brief responses."""
        prompt = MEDICAL_INTAKE_PROMPT
        assert any(
            word in prompt.lower()
            for word in ["voice", "brief", "sentence", "short"]
        )


class TestGetSystemMessage:
    """Test get_system_message function."""

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        result = get_system_message()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        """Test that result has required keys."""
        result = get_system_message()
        assert "role" in result
        assert "content" in result

    def test_system_role_is_system(self):
        """Test that role is 'system'."""
        result = get_system_message()
        assert result["role"] == "system"

    def test_default_content_is_medical_prompt(self):
        """Test that default content is the medical prompt."""
        result = get_system_message()
        assert result["content"] == MEDICAL_INTAKE_PROMPT

    def test_custom_prompt(self):
        """Test with custom prompt."""
        custom_prompt = "You are a helpful assistant."
        result = get_system_message(custom_prompt)
        assert result["content"] == custom_prompt

    def test_empty_prompt(self):
        """Test with empty prompt string."""
        result = get_system_message("")
        assert result["content"] == ""
        assert result["role"] == "system"

    @pytest.mark.parametrize("prompt", [
        "Short prompt",
        "A much longer prompt that spans multiple words and concepts",
        "Prompt with special chars: !@#$%^&*()",
        "Prompt\nwith\nnewlines",
    ])
    def test_various_prompts(self, prompt):
        """Test get_system_message with various prompt formats."""
        result = get_system_message(prompt)
        assert result["content"] == prompt
        assert result["role"] == "system"

    def test_message_format_is_openai_compatible(self):
        """Test that message format is OpenAI-compatible."""
        result = get_system_message()
        # Should match OpenAI message format
        assert isinstance(result, dict)
        assert set(result.keys()) == {"role", "content"}
        assert isinstance(result["role"], str)
        assert isinstance(result["content"], str)


class TestGetGreetingMessage:
    """Test get_greeting_message function."""

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        result = get_greeting_message()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        """Test that result has required keys."""
        result = get_greeting_message()
        assert "role" in result
        assert "content" in result

    def test_system_role_is_system(self):
        """Test that role is 'system'."""
        result = get_greeting_message()
        assert result["role"] == "system"

    def test_content_is_non_empty(self):
        """Test that content is not empty."""
        result = get_greeting_message()
        assert result["content"]
        assert len(result["content"]) > 0

    def test_greeting_mentions_greeting(self):
        """Test that greeting message mentions greeting."""
        result = get_greeting_message()
        assert "greet" in result["content"].lower()

    def test_greeting_mentions_patient(self):
        """Test that greeting message is patient-focused."""
        result = get_greeting_message()
        content_lower = result["content"].lower()
        assert any(word in content_lower for word in ["patient", "welcome", "help"])

    def test_message_format_is_openai_compatible(self):
        """Test that message format is OpenAI-compatible."""
        result = get_greeting_message()
        assert isinstance(result, dict)
        assert set(result.keys()) == {"role", "content"}
        assert isinstance(result["role"], str)
        assert isinstance(result["content"], str)

    def test_greeting_is_different_from_system(self):
        """Test that greeting is different from system message."""
        greeting = get_greeting_message()
        system = get_system_message()
        assert greeting["content"] != system["content"]
        # Both should be system role
        assert greeting["role"] == system["role"] == "system"


class TestPromptIntegration:
    """Test prompt functions together."""

    def test_can_build_conversation_start(self):
        """Test building initial conversation with system + greeting."""
        system_msg = get_system_message()
        greeting_msg = get_greeting_message()

        conversation = [system_msg, greeting_msg]

        assert len(conversation) == 2
        assert conversation[0]["role"] == "system"
        assert conversation[1]["role"] == "system"
        assert conversation[0]["content"] != conversation[1]["content"]

    def test_multiple_prompts_different_content(self):
        """Test that different prompts produce different messages."""
        prompt1 = get_system_message("Prompt 1")
        prompt2 = get_system_message("Prompt 2")

        assert prompt1["content"] != prompt2["content"]
        assert prompt1["role"] == prompt2["role"]
