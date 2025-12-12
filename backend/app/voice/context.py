"""
Conversation Context Factory

Creates and manages LLM conversation context.
"""

from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext


def create_context(messages: list[dict[str, str]]) -> OpenAILLMContext:
    """
    Create an LLM conversation context.

    Args:
        messages: Initial messages (typically system prompt).

    Returns:
        Configured OpenAILLMContext instance.
    """
    return OpenAILLMContext(messages)
