import reflex as rx
from app.states.chat_state import ChatState


def chat_message(msg: dict, index: int) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                msg["content"],
                class_name=rx.cond(
                    msg["role"] == "user",
                    "bg-[#8b5a2b] text-white px-4 py-3 rounded-2xl rounded-br-sm max-w-[85%] shadow-sm text-sm leading-relaxed whitespace-pre-wrap",
                    "bg-white text-stone-800 px-4 py-3 rounded-2xl rounded-bl-sm max-w-[85%] shadow-sm border border-stone-200 text-sm leading-relaxed whitespace-pre-wrap",
                ),
            ),
            class_name=rx.cond(
                msg["role"] == "user", "flex justify-end", "flex justify-start"
            ),
        ),
        class_name="mb-3",
    )


def citations_section() -> rx.Component:
    return rx.cond(
        ChatState.last_citations.length() > 0,
        rx.el.div(
            rx.el.div(
                rx.icon("book-marked", size=14, class_name="text-amber-700"),
                rx.el.span("Fuentes", class_name="text-xs font-bold text-amber-800"),
                rx.el.span(
                    ChatState.last_citations.length().to_string(),
                    class_name="text-[10px] bg-amber-200 text-amber-800 px-1.5 py-0.5 rounded-full",
                ),
                class_name="flex items-center gap-1.5 mb-2",
            ),
            rx.foreach(
                ChatState.last_citations,
                lambda c: rx.el.div(
                    rx.el.div(
                        c["title"],
                        class_name="font-semibold text-[11px] text-stone-700 leading-tight",
                    ),
                    rx.cond(
                        c["author"] != "",
                        rx.el.div(
                            c["author"], class_name="text-[10px] text-stone-500 italic"
                        ),
                    ),
                    rx.cond(
                        c["text"] != "",
                        rx.el.div(
                            c["text"],
                            class_name="text-[10px] text-stone-600 mt-1 line-clamp-2",
                        ),
                    ),
                    class_name="bg-amber-50/80 border border-amber-200 rounded-lg p-2 mb-1.5",
                ),
            ),
            class_name="mx-2 mb-3 px-3 py-2 bg-amber-50/50 rounded-xl border border-amber-100",
        ),
    )


def related_questions_chips() -> rx.Component:
    return rx.cond(
        ChatState.related_questions.length() > 0,
        rx.el.div(
            rx.el.div(
                "Preguntas relacionadas:",
                class_name="text-[10px] text-stone-500 font-medium mb-1.5 uppercase tracking-wider",
            ),
            rx.el.div(
                rx.foreach(
                    ChatState.related_questions,
                    lambda q: rx.el.button(
                        q,
                        on_click=lambda: ChatState.send_related_question(q),
                        class_name="text-xs bg-white border border-[#d4b886] text-[#8b5a2b] rounded-full px-3 py-1.5 hover:bg-[#8b5a2b] hover:text-white transition-colors shadow-sm text-left",
                    ),
                ),
                class_name="flex flex-wrap gap-1.5",
            ),
            class_name="mx-2 mb-3 px-3 py-2",
        ),
    )


def chat_panel() -> rx.Component:
    return rx.fragment(
        rx.el.button(
            rx.cond(
                ChatState.chat_open,
                rx.icon("x", size=24, class_name="text-white"),
                rx.icon("message-circle", size=24, class_name="text-white"),
            ),
            on_click=ChatState.toggle_chat,
            class_name="fixed bottom-4 right-4 md:bottom-8 md:right-8 z-50 w-14 h-14 rounded-full bg-[#8b5a2b] shadow-lg hover:bg-[#6b421a] flex items-center justify-center transition-all hover:scale-110 "
            + rx.cond(~ChatState.chat_open, "animate-pulse-glow", ""),
        ),
        rx.cond(
            ChatState.chat_open,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            "🤖 Asistente Bíblico",
                            class_name="font-serif font-bold text-white text-lg",
                        ),
                        rx.el.div(
                            "Magisterium AI",
                            class_name="text-amber-200 text-[10px] uppercase tracking-wider font-medium",
                        ),
                        class_name="flex flex-col",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.icon(
                                "trash-2",
                                size=16,
                                class_name="text-white/70 hover:text-white",
                            ),
                            on_click=ChatState.clear_chat,
                            class_name="p-2 rounded-lg hover:bg-white/10 transition-colors",
                            title="Limpiar chat",
                        ),
                        class_name="flex items-center gap-1",
                    ),
                    class_name="flex items-center justify-between bg-[#8b5a2b] px-4 py-3 rounded-t-2xl shrink-0",
                ),
                rx.el.div(
                    rx.cond(
                        ChatState.chat_messages.length() == 0,
                        rx.el.div(
                            rx.el.div("📖", class_name="text-4xl mb-3"),
                            rx.el.div(
                                "¡Bienvenido!",
                                class_name="font-serif font-bold text-[#4a3320] text-xl mb-2",
                            ),
                            rx.el.div(
                                "Pregúntame sobre personajes bíblicos, eventos, enseñanzas o cualquier tema de las Escrituras.",
                                class_name="text-sm text-stone-600 text-center leading-relaxed",
                            ),
                            class_name="flex flex-col items-center justify-center h-full px-8 py-12",
                        ),
                        rx.el.div(
                            rx.foreach(
                                ChatState.chat_messages,
                                lambda msg, idx: chat_message(msg, idx),
                            ),
                            citations_section(),
                            rx.cond(
                                ChatState.chat_loading,
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.div(
                                            class_name="w-2 h-2 bg-[#8b5a2b] rounded-full animate-bounce [animation-delay:0ms]"
                                        ),
                                        rx.el.div(
                                            class_name="w-2 h-2 bg-[#8b5a2b] rounded-full animate-bounce [animation-delay:150ms]"
                                        ),
                                        rx.el.div(
                                            class_name="w-2 h-2 bg-[#8b5a2b] rounded-full animate-bounce [animation-delay:300ms]"
                                        ),
                                        class_name="flex gap-1.5 bg-white px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm border border-stone-200 w-fit",
                                    ),
                                    class_name="flex justify-start mb-3",
                                ),
                            ),
                            related_questions_chips(),
                            rx.el.div(id="chat-bottom"),
                            class_name="flex flex-col",
                        ),
                    ),
                    class_name="flex-1 overflow-y-auto p-3 bg-[url('https://www.transparenttextures.com/patterns/aged-paper.png')] bg-[#faf6eb] no-scrollbar",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.input(
                            placeholder="Pregunta sobre la Biblia...",
                            on_change=ChatState.set_chat_input,
                            on_key_down=ChatState.handle_key_down,
                            disabled=ChatState.chat_loading,
                            class_name="flex-1 bg-transparent text-sm text-stone-800 placeholder-stone-400 focus:outline-none font-serif disabled:opacity-50",
                            default_value=ChatState.chat_input,
                        ),
                        rx.el.button(
                            rx.icon("arrow-up", size=18, class_name="text-white"),
                            on_click=ChatState.send_message,
                            disabled=ChatState.chat_loading,
                            class_name="w-9 h-9 rounded-full bg-[#8b5a2b] hover:bg-[#6b421a] flex items-center justify-center shrink-0 transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
                        ),
                        class_name="flex items-center gap-2 bg-white border-2 border-[#d4b886] rounded-xl px-3 py-2",
                    ),
                    class_name="p-3 bg-[#f5e9d3] border-t border-[#d4b886] rounded-b-2xl shrink-0",
                ),
                class_name="fixed bottom-20 right-4 md:bottom-24 md:right-8 z-50 w-[calc(100vw-2rem)] sm:w-[400px] h-[500px] md:h-[550px] rounded-2xl shadow-2xl border-2 border-[#d4b886] flex flex-col overflow-hidden animate-fade-in",
            ),
        ),
    )