import reflex as rx
import requests
import asyncio
import functools
import logging


class ChatState(rx.State):
    chat_open: bool = False
    chat_messages: list[dict[str, str]] = []
    chat_input: str = ""
    chat_loading: bool = False
    related_questions: list[str] = []
    last_citations: list[dict[str, str]] = []
    magisterium_api_key: str = (
        "sk_josele_76d9fbda03b12d7cc0a458bce68812735d690038b46a1b3421e855b37e3f82b3"
    )

    @rx.event
    def toggle_chat(self):
        self.chat_open = not self.chat_open

    @rx.event
    def set_chat_input(self, value: str):
        self.chat_input = value

    @rx.event
    def send_message(self):
        if not self.chat_input.strip() or self.chat_loading:
            return
        user_msg = self.chat_input.strip()
        self.chat_messages.append({"role": "user", "content": user_msg})
        self.chat_input = ""
        self.chat_loading = True
        self.related_questions = []
        self.last_citations = []
        return [
            ChatState.call_magisterium_api,
            rx.call_script(
                "setTimeout(() => document.getElementById('chat-bottom')?.scrollIntoView({behavior:'smooth'}), 100)"
            ),
        ]

    @rx.event
    def send_related_question(self, question: str):
        self.chat_input = question
        return ChatState.send_message

    @rx.event
    def clear_chat(self):
        self.chat_messages = []
        self.chat_input = ""
        self.chat_loading = False
        self.related_questions = []
        self.last_citations = []

    @rx.event(background=True)
    async def call_magisterium_api(self):
        async with self:
            messages_for_api = []
            messages_for_api.append(
                {
                    "role": "system",
                    "content": "Eres un asistente bíblico católico que responde en español. Ayudas a los usuarios a explorar personajes, eventos y enseñanzas de la Biblia. Proporciona respuestas claras y fundamentadas en las Escrituras y la tradición católica.",
                }
            )
            recent = self.chat_messages[-10:]
            for m in recent:
                messages_for_api.append({"role": m["role"], "content": m["content"]})
            api_key = self.magisterium_api_key
        try:
            url = "https://www.magisterium.com/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "magisterium-1",
                "messages": messages_for_api,
                "stream": False,
                "return_related_questions": True,
            }
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    requests.post, url, headers=headers, json=data, timeout=60
                ),
            )
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                citations = result.get("citations", [])
                related = result.get("related_questions", [])
                simple_citations = []
                for c in citations:
                    simple_citations.append(
                        {
                            "title": c.get("document_title", ""),
                            "text": c.get("cited_text", "")[:200],
                            "url": c.get("source_url", ""),
                            "author": c.get("document_author", ""),
                        }
                    )
                async with self:
                    self.chat_messages.append({"role": "assistant", "content": content})
                    self.last_citations = simple_citations
                    self.related_questions = related[:4] if related else []
                    self.chat_loading = False
            else:
                async with self:
                    self.chat_messages.append(
                        {
                            "role": "assistant",
                            "content": f"Error: No pude obtener respuesta ({response.status_code}). Intenta de nuevo.",
                        }
                    )
                    self.chat_loading = False
        except Exception as e:
            logging.exception("Magisterium API error")
            async with self:
                self.chat_messages.append(
                    {
                        "role": "assistant",
                        "content": f"Error de conexión. Por favor intenta de nuevo.",
                    }
                )
                self.chat_loading = False
        yield rx.call_script(
            "setTimeout(() => document.getElementById('chat-bottom')?.scrollIntoView({behavior:'smooth'}), 100)"
        )

    @rx.event
    def handle_key_down(self, key: str):
        if key == "Enter" and (not self.chat_loading):
            return ChatState.send_message