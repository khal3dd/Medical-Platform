"""
LLM Provider — wraps the OpenRouter API.

OpenRouter exposes an OpenAI-compatible REST API, so we use the `openai`
Python SDK pointed at the OpenRouter base URL. This lets us access any
model available on OpenRouter (Claude, GPT-4o, Mistral, Llama, etc.)
just by changing LLM_MODEL in .env — no code changes needed.

Responsibilities:
- Initialize the OpenAI-compatible client with OpenRouter credentials
- Send messages to the OpenRouter API with the correct format
- Return the assistant's response text
- Handle API-level errors with clear, user-friendly messages
"""

from openai import OpenAI, APIConnectionError, APIStatusError, RateLimitError

from core.config import settings
from core.logger import get_logger
from schemas.chat import ConversationMessage

logger = get_logger(__name__)


class LLMProvider:
    """
    Thin wrapper around the OpenRouter API (OpenAI-compatible).

    Usage:
        provider = LLMProvider()
        reply = provider.chat(system_prompt, history, user_message)
    """

    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )
        self._model = settings.llm_model
        self._max_tokens = settings.llm_max_tokens
        self._temperature = settings.llm_temperature
        logger.info(
            f"LLMProvider initialized | model={self._model} "
            f"| base_url={settings.openrouter_base_url}"
        )

    def chat(
        self,
        system_prompt: str,
        history: list[ConversationMessage],
        user_message: str,
    ) -> str:
        """
        Send a conversation to the LLM via OpenRouter and return the reply text.

        Args:
            system_prompt:  The full assembled system prompt (from core/prompts.py).
            history:        Previous turns in the conversation (user + assistant pairs).
            user_message:   The latest message from the user.

        Returns:
            The assistant's reply as a plain string.

        Raises:
            RuntimeError: If the API call fails for any reason.
        """
        messages = self._build_messages(system_prompt, history, user_message)

        logger.debug(
            f"Calling OpenRouter API | model={self._model} "
            f"| turns={len(history)} | user_msg_len={len(user_message)}"
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                max_tokens=self._max_tokens,
                temperature=self._temperature,
                messages=messages,
            )
        except RateLimitError as e:
            logger.error(f"OpenRouter rate limit exceeded: {e}")
            raise RuntimeError(
                "The service is temporarily busy. Please try again in a moment."
            ) from e
        except APIConnectionError as e:
            logger.error(f"OpenRouter connection error: {e}")
            raise RuntimeError(
                "Could not connect to the AI service. Please check your internet connection."
            ) from e
        except APIStatusError as e:
            logger.error(f"OpenRouter API error: status={e.status_code} | {e.message}")
            raise RuntimeError(
                f"The AI service returned an error (status {e.status_code}). "
                "Please try again or contact support."
            ) from e

        reply_text = self._extract_text(response)
        logger.debug(f"Model replied | reply_len={len(reply_text)}")
        return reply_text

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_messages(
        self,
        system_prompt: str,
        history: list[ConversationMessage],
        user_message: str,
    ) -> list[dict]:
        """
        Build the full messages list in OpenAI/OpenRouter format.
        The system prompt goes first as a system-role message,
        followed by conversation history, then the new user message.
        """
        messages = [{"role": "system", "content": system_prompt}]

        for turn in history:
            messages.append({"role": turn.role.value, "content": turn.content})

        messages.append({"role": "user", "content": user_message})

        return messages

    def _extract_text(self, response) -> str:
        """
        Extract plain text from the OpenRouter/OpenAI response object.
        """
        try:
            text = response.choices[0].message.content
            if text:
                return text.strip()
        except (IndexError, AttributeError):
            pass

        logger.warning("LLM response contained no usable text content.")
        return "I'm sorry, I wasn't able to generate a response. Please try again."
