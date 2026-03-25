from providers.llm_provider import LLMProvider
from core.config import settings
from core.logger import get_logger
from core.prompts import build_system_prompt, format_user_message, build_rag_user_message
from enums.chat import MessageRole
from schemas.chat import ConversationMessage

logger = get_logger(__name__)


class ChatSession:

    def __init__(self, max_turns: int):
        self.messages: list[ConversationMessage] = []
        self.max_entries = max_turns * 2

    def add_turn(self, user_msg: str, assistant_reply: str):
        self.messages.append(
            ConversationMessage(role=MessageRole.USER, content=user_msg)
        )
        self.messages.append(
            ConversationMessage(role=MessageRole.ASSISTANT, content=assistant_reply)
        )
        if len(self.messages) > self.max_entries:
            self.messages = self.messages[-self.max_entries:]

    @property
    def turn_count(self) -> int:
        return len(self.messages) // 2


class ChatService:

    def __init__(self, llm_provider: LLMProvider) -> None:
        self._llm = llm_provider
        self._sessions: dict[str, ChatSession] = {}
        logger.info("ChatService initialized.")

    def handle_message(
        self,
        session_id: str,
        user_message: str,
        context: str | None = None,
        tenant_id: str = "general",
    ) -> dict:
        session = self._get_session(session_id)
        clean_message = format_user_message(user_message)

        system_prompt = build_system_prompt(tenant_id)

        if context:
            final_message = build_rag_user_message(clean_message, context)
            logger.info(f"RAG mode | tenant={tenant_id} | session={session_id} | turns={session.turn_count}")
        else:
            final_message = clean_message
            logger.info(f"General mode | tenant={tenant_id} | session={session_id} | turns={session.turn_count}")

        try:
            reply = self._llm.chat(
                system_prompt=system_prompt,
                history=session.messages,
                user_message=final_message,
            )
        except Exception as e:
            logger.error(f"LLM call failed | session={session_id} | error={e}")
            raise RuntimeError("LLM call failed") from e

        session.add_turn(clean_message, reply)

        logger.info(
            f"Reply generated | tenant={tenant_id} | session={session_id} "
            f"| turns={session.turn_count} "
            f"| reply_len={len(reply)}"
        )

        return {
            "session_id": session_id,
            "reply": reply,
            "turn_count": session.turn_count,
        }

    def clear_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Session cleared: {session_id}")
            return True
        logger.debug(f"Clear called on non-existent session: {session_id}")
        return False

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def get_turn_count(self, session_id: str) -> int:
        if session_id in self._sessions:
            return self._sessions[session_id].turn_count
        return 0

    def _get_session(self, session_id: str) -> ChatSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = ChatSession(
                max_turns=settings.session_max_turns
            )
            logger.debug(f"New session created: {session_id}")
        return self._sessions[session_id]