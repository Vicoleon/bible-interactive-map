import reflex as rx
from app.components.navigation import navigation
from app.components.map_canvas import map_canvas
from app.components.detail_panel import detail_panel
from app.components.timeline_view import timeline_view
from app.states.bible_state import BibleState


def context_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.close(
                rx.el.button(
                    rx.icon("x", size=24),
                    class_name="absolute top-4 right-4 p-2 rounded-full hover:bg-stone-200 transition-colors z-10",
                )
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("chevron-left", size=20),
                    on_click=lambda: BibleState.navigate_context_chapter(-1),
                    class_name="p-2 rounded-lg bg-stone-100 hover:bg-stone-200 transition-colors",
                ),
                rx.el.div(
                    rx.dialog.title(
                        BibleState.context_chapter_reference,
                        class_name="text-3xl font-bold font-serif text-[#4a3320] text-center mb-1",
                    ),
                    rx.dialog.description(
                        "Capítulo Completo",
                        class_name="text-sm text-[#8b5a2b] text-center font-medium",
                    ),
                    class_name="flex-1",
                ),
                rx.el.button(
                    rx.icon("chevron-right", size=20),
                    on_click=lambda: BibleState.navigate_context_chapter(1),
                    class_name="p-2 rounded-lg bg-stone-100 hover:bg-stone-200 transition-colors",
                ),
                class_name="flex items-center justify-between px-8 pt-8 pb-4",
            ),
            rx.cond(
                BibleState.audio_is_available,
                rx.el.div(
                    rx.cond(
                        BibleState.audio_url != "",
                        rx.el.div(
                            rx.el.div(
                                rx.icon(
                                    "volume-2",
                                    size=18,
                                    class_name="text-[#8b5a2b] shrink-0",
                                ),
                                rx.el.span(
                                    "Audio Disponible (English - WEB)",
                                    class_name="text-sm text-[#8b5a2b] font-medium",
                                ),
                                class_name="flex items-center gap-2 mb-2",
                            ),
                            rx.el.audio(
                                rx.el.source(
                                    src=BibleState.audio_url, type="audio/mpeg"
                                ),
                                controls=True,
                                auto_play=True,
                                class_name="w-full h-10 rounded-lg",
                            ),
                            rx.el.button(
                                rx.icon("x", size=14, class_name="mr-1"),
                                "Cerrar Audio",
                                on_click=BibleState.stop_audio,
                                class_name="mt-2 text-xs text-stone-500 hover:text-stone-700 flex items-center gap-1 mx-auto transition-colors",
                            ),
                            class_name="bg-amber-50/80 border border-amber-200 rounded-xl p-4 mx-8 mt-4 mb-4",
                        ),
                        rx.el.div(
                            rx.cond(
                                BibleState.audio_loading,
                                rx.el.button(
                                    rx.icon(
                                        "loader",
                                        size=16,
                                        class_name="animate-spin mr-2",
                                    ),
                                    "Cargando audio...",
                                    disabled=True,
                                    class_name="flex items-center px-4 py-2 bg-stone-200 text-stone-500 rounded-lg text-sm font-medium mx-auto",
                                ),
                                rx.el.button(
                                    rx.icon("headphones", size=16, class_name="mr-2"),
                                    "🔊 Escuchar Capítulo",
                                    on_click=lambda: BibleState.fetch_audio(
                                        BibleState.context_chapter_id
                                    ),
                                    class_name="flex items-center px-4 py-2 bg-[#8b5a2b] hover:bg-[#6b421a] text-white rounded-lg text-sm font-medium mx-auto shadow-sm transition-all",
                                ),
                            ),
                            rx.el.p(
                                "Audio en inglés (World English Bible)",
                                class_name="text-[10px] text-stone-400 text-center mt-1 italic",
                            ),
                            class_name="flex flex-col items-center mx-8 mt-4 mb-4",
                        ),
                    )
                ),
            ),
            rx.el.div(class_name="h-px bg-[#d4b886] mx-8"),
            rx.cond(
                BibleState.context_chapter_loading,
                rx.el.div(
                    rx.icon(
                        "loader",
                        size=32,
                        class_name="animate-spin text-[#8b5a2b] mx-auto mb-4",
                    ),
                    rx.el.p(
                        "Cargando capítulo...",
                        class_name="text-stone-500 text-center italic font-serif text-lg",
                    ),
                    class_name="flex flex-col items-center justify-center py-20",
                ),
                rx.el.div(
                    rx.el.div(
                        BibleState.context_chapter_text,
                        class_name="font-serif text-stone-800 text-lg leading-loose text-justify whitespace-pre-wrap",
                    ),
                    class_name="bg-[url('https://www.transparenttextures.com/patterns/aged-paper.png')] bg-[#f4ebd8] p-8 mx-8 my-6 rounded-2xl shadow-inner border-2 border-[#d4b886] overflow-y-auto max-h-[60vh] no-scrollbar",
                ),
            ),
            class_name="bg-[#faf6eb] rounded-3xl shadow-2xl border-4 border-[#d4b886] max-w-4xl w-full relative overflow-hidden p-0",
            style={"max_height": "90vh"},
        ),
        open=BibleState.context_modal_open,
        on_open_change=lambda open: rx.cond(
            ~open, BibleState.close_context_modal(), rx.noop()
        ),
    )


def index() -> rx.Component:
    return rx.el.div(
        rx.el.style("""
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
            @keyframes pulseGlow { 0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(139, 90, 43, 0.7); } 50% { transform: scale(1.05); box-shadow: 0 0 15px 10px rgba(139, 90, 43, 0); } 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(139, 90, 43, 0); } }
            @keyframes flowDash { to { stroke-dashoffset: -24; } }
            @keyframes float { 0% { transform: translate(-50%, -50%) translateY(0px); } 50% { transform: translate(-50%, -50%) translateY(-5px); } 100% { transform: translate(-50%, -50%) translateY(0px); } }

            .animate-fade-in { animation: fadeIn 0.5s ease-out forwards; }
            .animate-slide-in-right { animation: slideInRight 0.4s ease-out forwards; }
            .animate-pulse-glow { animation: pulseGlow 2s infinite; }
            .animate-flow { stroke-dasharray: 12 12; animation: flowDash 1s linear infinite; }
            .animate-float { animation: float 4s ease-in-out infinite; }

            .bg-parchment { background-image: url('https://www.transparenttextures.com/patterns/aged-paper.png'); }
            .bg-crosshatch { background-image: url('https://www.transparenttextures.com/patterns/cross-stripes.png'); }
        """),
        navigation(),
        rx.el.main(
            rx.cond(BibleState.active_view == "map", map_canvas(), timeline_view()),
            detail_panel(),
            class_name="relative w-full flex-1 overflow-hidden",
        ),
        context_modal(),
        class_name="min-h-screen flex flex-col font-['Inter'] bg-[#eaddc5] overflow-hidden",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/")