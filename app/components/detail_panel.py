import reflex as rx
from app.states.bible_state import BibleState


def get_role_color(role: str) -> str:
    return rx.match(
        role,
        ("Profeta", "bg-purple-100 text-purple-800 border-purple-300"),
        ("Rey", "bg-yellow-100 text-yellow-800 border-yellow-300"),
        ("Reina", "bg-yellow-100 text-yellow-800 border-yellow-300"),
        ("Apóstol", "bg-blue-100 text-blue-800 border-blue-300"),
        ("Patriarca", "bg-amber-100 text-amber-800 border-amber-300"),
        ("Matriarca", "bg-amber-100 text-amber-800 border-amber-300"),
        ("Mesías", "bg-indigo-100 text-indigo-900 border-indigo-400 font-bold"),
        "bg-stone-100 text-stone-700 border-stone-300",
    )


def character_detail() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            BibleState.selected_character["emoji"],
            class_name="text-5xl mb-4 bg-stone-100 w-20 h-20 flex items-center justify-center rounded-full shadow-inner border-2 border-stone-300",
        ),
        rx.el.h2(
            BibleState.selected_character["name"],
            class_name="text-2xl md:text-3xl font-bold text-[#4a3320] font-serif mb-2",
        ),
        rx.el.div(
            rx.el.span(
                BibleState.selected_character["role"],
                class_name=f"px-3 py-1 rounded-full text-sm border {get_role_color(BibleState.selected_character['role'])}",
            ),
            rx.el.span(
                BibleState.selected_character["testament"],
                class_name="px-3 py-1 rounded-full text-sm bg-stone-200 text-stone-700 border border-stone-300",
            ),
            rx.el.span(
                BibleState.selected_character["era"],
                class_name="px-3 py-1 rounded-full text-sm bg-stone-200 text-stone-700 border border-stone-300",
            ),
            class_name="flex flex-wrap gap-2 mb-6",
        ),
        rx.el.p(
            BibleState.selected_character["description"],
            class_name="text-stone-700 text-base md:text-lg leading-relaxed mb-8 border-l-4 border-[#8b5a2b] pl-4 italic",
        ),
        rx.el.h3(
            "Conexiones",
            class_name="text-xl font-bold text-[#4a3320] font-serif mb-4 border-b border-stone-300 pb-2",
        ),
        rx.el.ul(
            rx.foreach(
                BibleState.selected_character_connections,
                lambda conn: rx.el.li(
                    rx.el.div(
                        rx.icon(
                            rx.match(
                                conn["type"],
                                ("familia", "users"),
                                ("mentor", "graduation-cap"),
                                ("aliado", "handshake"),
                                ("profecía", "sparkles"),
                                ("linaje", "git-merge"),
                                "link",
                            ),
                            size=16,
                            class_name=rx.match(
                                conn["type"],
                                ("profecía", "text-amber-500"),
                                "text-stone-500",
                            ),
                        ),
                        rx.el.span(
                            conn["name"],
                            class_name="font-semibold text-stone-800 group-hover:text-[#8b5a2b] transition-colors",
                        ),
                        rx.el.span("•", class_name="text-stone-400 text-xs"),
                        rx.el.span(conn["desc"], class_name="text-stone-600 text-sm"),
                        class_name="flex items-center gap-2 cursor-pointer group",
                        on_click=lambda: BibleState.select_character(conn["id"]),
                    ),
                    class_name="py-3 border-b border-stone-100 last:border-0 hover:bg-white/80 transition-colors px-2 -mx-2 rounded-lg",
                ),
            ),
            class_name="bg-white/50 rounded-xl p-4 shadow-sm border border-stone-200",
        ),
        rx.cond(
            BibleState.character_events.length() > 0,
            rx.el.div(
                rx.el.h3(
                    "📅 Eventos",
                    class_name="text-xl font-bold text-[#4a3320] font-serif mt-6 mb-4 border-b border-stone-300 pb-2",
                ),
                rx.el.div(
                    rx.foreach(
                        BibleState.character_events,
                        lambda ev: rx.el.div(
                            rx.el.span(ev["emoji"], class_name="text-2xl shrink-0"),
                            rx.el.div(
                                rx.el.div(
                                    ev["title"],
                                    class_name="font-semibold text-stone-800 group-hover:text-[#8b5a2b] transition-colors",
                                ),
                                rx.el.div(
                                    ev["date_label"],
                                    class_name="text-xs text-stone-500 font-medium",
                                ),
                                class_name="flex flex-col",
                            ),
                            on_click=lambda: BibleState.select_event(ev["id"]),
                            class_name="flex items-center gap-3 cursor-pointer group bg-white/60 p-3 rounded-xl border border-stone-200 shadow-sm hover:bg-white mb-3 hover:shadow-md transition-all",
                        ),
                    )
                ),
            ),
        ),
        class_name="flex flex-col",
    )


def event_detail() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            BibleState.selected_event["emoji"],
            class_name="text-5xl mb-4 bg-[#faf6eb] w-20 h-20 flex items-center justify-center rounded-2xl shadow-sm border-2 border-[#d4b886]",
        ),
        rx.el.h2(
            BibleState.selected_event["title"],
            class_name="text-2xl md:text-3xl font-bold text-[#4a3320] font-serif mb-4",
        ),
        rx.el.div(
            rx.el.span(
                BibleState.selected_event["date_label"],
                class_name="px-3 py-1 rounded-full text-sm bg-[#8b5a2b] text-white font-medium",
            ),
            rx.el.span(
                BibleState.selected_event["scripture_ref"],
                class_name="px-3 py-1 rounded-full text-sm bg-stone-200 text-stone-700 border border-stone-300 font-medium",
            ),
            rx.el.span(
                BibleState.selected_event["era"],
                class_name="px-3 py-1 rounded-full text-sm bg-stone-200 text-stone-700 border border-stone-300",
            ),
            class_name="flex flex-wrap gap-2 mb-6",
        ),
        rx.el.p(
            BibleState.selected_event["description"],
            class_name="text-stone-700 text-lg leading-relaxed mb-8 border-l-4 border-[#8b5a2b] pl-4 italic",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "📖 Escritura",
                    class_name="text-xl font-bold text-[#4a3320] font-serif",
                ),
                rx.el.div(
                    rx.el.button(
                        "Leer Pasaje",
                        on_click=lambda: BibleState.fetch_scripture(
                            BibleState.selected_event["scripture_ref"]
                        ),
                        class_name="px-4 py-1.5 bg-[#8b5a2b] text-white text-sm font-medium rounded-lg hover:bg-[#6b421a] transition-all shadow-sm",
                    ),
                    rx.el.button(
                        "Leer Capítulo",
                        on_click=BibleState.open_event_context_modal,
                        class_name="px-4 py-1.5 bg-white text-[#8b5a2b] text-sm font-medium rounded-lg border-2 border-[#8b5a2b] hover:bg-[#8b5a2b] hover:text-white transition-all shadow-sm",
                    ),
                    class_name="flex flex-wrap gap-2",
                ),
                class_name="flex justify-between items-center mb-4 border-b border-stone-300 pb-2",
            ),
            rx.cond(
                BibleState.scripture_loading,
                rx.el.div(
                    "Cargando pasaje...",
                    class_name="text-stone-500 italic py-6 text-center animate-pulse",
                ),
                rx.cond(
                    BibleState.scripture_error != "",
                    rx.el.div(
                        BibleState.scripture_error,
                        class_name="text-red-500 py-4 text-sm",
                    ),
                    rx.cond(
                        BibleState.scripture_text != "",
                        rx.el.div(
                            rx.el.h4(
                                BibleState.scripture_reference,
                                class_name="font-serif font-bold text-center mb-4 text-[#8b5a2b] border-b border-[#d4b886] pb-2",
                            ),
                            rx.el.div(
                                BibleState.scripture_text,
                                class_name="font-serif text-stone-800 leading-loose text-justify whitespace-pre-wrap",
                            ),
                            class_name="bg-[url('https://www.transparenttextures.com/patterns/aged-paper.png')] bg-[#f4ebd8] p-6 rounded-xl shadow-inner border-2 border-[#d4b886] mb-8 max-h-[300px] md:max-h-[400px] overflow-y-auto no-scrollbar",
                        ),
                    ),
                ),
            ),
        ),
        rx.cond(
            BibleState.has_cross_testament_connection,
            rx.el.div(
                rx.icon("sparkles", size=18, class_name="text-amber-500 mr-2"),
                rx.el.span("Conexión Profética", class_name="font-bold text-amber-700"),
                class_name="flex items-center mb-4 bg-amber-50 p-3 rounded-lg border border-amber-200 shadow-sm",
            ),
        ),
        rx.cond(
            BibleState.selected_event_connected_details.length() > 0,
            rx.el.div(
                rx.el.h3(
                    "Eventos Conectados",
                    class_name="text-xl font-bold text-[#4a3320] font-serif mb-4 border-b border-stone-300 pb-2",
                ),
                rx.el.div(
                    rx.foreach(
                        BibleState.selected_event_connected_details,
                        lambda ev: rx.el.div(
                            rx.icon(
                                "arrow-right", size=16, class_name="text-stone-400 mr-2"
                            ),
                            rx.el.div(
                                rx.el.span(
                                    ev["emoji"], class_name="text-2xl shrink-0 mr-3"
                                ),
                                rx.el.span(
                                    ev["title"],
                                    class_name="font-semibold text-stone-800 group-hover:text-[#8b5a2b] transition-colors",
                                ),
                                class_name="flex items-center bg-white/60 p-3 rounded-xl border border-stone-200 shadow-sm hover:bg-white hover:shadow-md transition-all flex-1",
                            ),
                            on_click=lambda: BibleState.select_event(ev["id"]),
                            class_name="flex items-center cursor-pointer group mb-3",
                        ),
                    ),
                    class_name="mb-8",
                ),
            ),
        ),
        rx.el.h3(
            "Personajes Involucrados",
            class_name="text-xl font-bold text-[#4a3320] font-serif mb-4 border-b border-stone-300 pb-2",
        ),
        rx.el.div(
            rx.foreach(
                BibleState.selected_event_characters,
                lambda char: rx.el.div(
                    rx.el.span(char["emoji"], class_name="text-xl"),
                    rx.el.span(
                        char["name"],
                        class_name="font-semibold text-stone-800 group-hover:text-[#8b5a2b] transition-colors",
                    ),
                    on_click=lambda: BibleState.select_character(char["id"]),
                    class_name="flex items-center gap-2 cursor-pointer group bg-white/50 p-2 rounded-lg border border-stone-200 shadow-sm hover:bg-white",
                ),
            ),
            class_name="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8",
        ),
        class_name="flex flex-col",
    )


def book_detail() -> rx.Component:
    book = BibleState.selected_book
    return rx.cond(
        book != None,
        rx.el.div(
            rx.el.div(
                book["emoji"],
                class_name="text-5xl mb-4 bg-emerald-50 w-20 h-20 flex items-center justify-center rounded-2xl shadow-sm border-2 border-emerald-200",
            ),
            rx.el.h2(
                book["name"],
                class_name="text-2xl md:text-3xl font-bold text-[#4a3320] font-serif mb-2",
            ),
            rx.el.div(
                rx.el.span(
                    book["testament"],
                    class_name="px-3 py-1 rounded-full text-sm bg-stone-200 text-stone-700 border border-stone-300 font-medium",
                ),
                rx.el.span(
                    book["category"],
                    class_name="px-3 py-1 rounded-full text-sm bg-emerald-100 text-emerald-800 border border-emerald-300",
                ),
                rx.el.span(
                    book["chapters"].to_string() + " Capítulos",
                    class_name="px-3 py-1 rounded-full text-sm bg-stone-100 text-stone-600 border border-stone-200",
                ),
                class_name="flex flex-wrap gap-2 mb-8",
            ),
            rx.el.h3(
                "📖 Lector Bíblico",
                class_name="text-xl font-bold text-[#4a3320] font-serif mb-4 border-b border-stone-300 pb-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.button(
                        rx.icon("chevron-left", size=16),
                        on_click=lambda: BibleState.set_book_chapter(
                            BibleState.book_scripture_chapter - 1
                        ),
                        class_name="p-2 bg-stone-100 rounded-lg hover:bg-stone-200 transition-colors disabled:opacity-50",
                    ),
                    rx.el.span(
                        "Capítulo " + BibleState.book_scripture_chapter.to_string(),
                        class_name="font-medium font-serif text-lg text-stone-800 min-w-[100px] text-center",
                    ),
                    rx.el.button(
                        rx.icon("chevron-right", size=16),
                        on_click=lambda: BibleState.set_book_chapter(
                            BibleState.book_scripture_chapter + 1
                        ),
                        class_name="p-2 bg-stone-100 rounded-lg hover:bg-stone-200 transition-colors",
                    ),
                    class_name="flex items-center justify-between mb-4",
                ),
                rx.el.button(
                    "Cargar Capítulo",
                    on_click=lambda: BibleState.fetch_book_chapter(
                        book["api_id"], BibleState.book_scripture_chapter
                    ),
                    class_name="w-full py-2 bg-[#8b5a2b] text-white font-medium rounded-lg hover:bg-[#6b421a] transition-all shadow-sm mb-4",
                ),
                rx.cond(
                    BibleState.book_scripture_loading,
                    rx.el.div(
                        "Cargando...",
                        class_name="text-center text-stone-500 italic py-4 animate-pulse",
                    ),
                    rx.cond(
                        BibleState.book_scripture_text != "",
                        rx.el.div(
                            BibleState.book_scripture_text,
                            class_name="font-serif text-stone-800 leading-loose text-justify whitespace-pre-wrap bg-[url('https://www.transparenttextures.com/patterns/aged-paper.png')] bg-[#f4ebd8] p-6 rounded-xl shadow-inner border-2 border-[#d4b886] max-h-[250px] md:max-h-[300px] overflow-y-auto no-scrollbar",
                        ),
                    ),
                ),
            ),
            rx.cond(
                book["related_events"].length() > 0,
                rx.el.div(
                    rx.el.h3(
                        "📅 Eventos Relacionados",
                        class_name="text-xl font-bold text-[#4a3320] font-serif mt-8 mb-4 border-b border-stone-300 pb-2",
                    ),
                    rx.el.div(
                        rx.foreach(
                            BibleState.events,
                            lambda ev: rx.cond(
                                book["related_events"].contains(ev["id"]),
                                rx.el.div(
                                    rx.el.span(
                                        ev["emoji"], class_name="text-2xl shrink-0 mr-3"
                                    ),
                                    rx.el.div(
                                        rx.el.div(
                                            ev["title"],
                                            class_name="font-semibold text-stone-800 group-hover:text-[#8b5a2b] transition-colors",
                                        ),
                                        rx.el.div(
                                            ev["date_label"],
                                            class_name="text-xs text-stone-500 font-medium",
                                        ),
                                    ),
                                    on_click=lambda: BibleState.select_event(ev["id"]),
                                    class_name="flex items-center cursor-pointer group bg-white/60 p-3 rounded-xl border border-stone-200 shadow-sm hover:bg-white mb-3 hover:shadow-md transition-all",
                                ),
                                rx.fragment(),
                            ),
                        )
                    ),
                ),
            ),
            class_name="flex flex-col",
        ),
        rx.fragment(),
    )


def scripture_detail() -> rx.Component:
    return rx.cond(
        BibleState.selected_scripture_result != None,
        rx.el.div(
            rx.el.div(
                "📖",
                class_name="text-5xl mb-4 bg-[#faf6eb] w-20 h-20 flex items-center justify-center rounded-2xl shadow-sm border-2 border-[#d4b886]",
            ),
            rx.el.h2(
                BibleState.selected_scripture_result["reference"],
                class_name="text-3xl font-bold text-[#4a3320] font-serif mb-4",
            ),
            rx.el.div(
                rx.el.span(
                    rx.cond(
                        BibleState.selected_scripture_result["type"] == "passage",
                        "Pasaje",
                        "Versículo",
                    ),
                    class_name="px-3 py-1 rounded-full text-sm bg-amber-100 text-amber-800 border border-amber-300 font-medium",
                ),
                class_name="flex flex-wrap gap-2 mb-8",
            ),
            rx.el.div(
                rx.el.div(
                    BibleState.scripture_text,
                    class_name="font-serif text-stone-800 leading-loose text-justify whitespace-pre-wrap",
                ),
                class_name="bg-[url('https://www.transparenttextures.com/patterns/aged-paper.png')] bg-[#f4ebd8] p-6 rounded-xl shadow-inner border-2 border-[#d4b886] mb-8 overflow-y-auto no-scrollbar max-h-[500px]",
            ),
            rx.el.button(
                "📖 Leer Capítulo Completo",
                on_click=BibleState.open_context_modal,
                class_name="w-full py-3 bg-[#8b5a2b] text-white font-medium rounded-xl hover:bg-[#6b421a] transition-all shadow-md text-lg",
            ),
            class_name="flex flex-col",
        ),
        rx.fragment(),
    )


def detail_panel() -> rx.Component:
    return rx.cond(
        (BibleState.selected_character_id != None)
        | (BibleState.selected_event_id != None)
        | (BibleState.selected_book_id != None)
        | (BibleState.selected_scripture_result != None),
        rx.el.div(
            rx.el.button(
                rx.icon("x", size=20, class_name="text-stone-500 hover:text-stone-800"),
                on_click=BibleState.clear_selection,
                class_name="absolute top-3 right-3 p-3 md:p-2 rounded-full hover:bg-stone-200 transition-colors z-10",
            ),
            rx.cond(
                BibleState.selected_character_id != None,
                character_detail(),
                rx.cond(
                    BibleState.selected_event_id != None,
                    event_detail(),
                    rx.cond(
                        BibleState.selected_book_id != None,
                        book_detail(),
                        rx.cond(
                            BibleState.selected_scripture_result != None,
                            scripture_detail(),
                            rx.fragment(),
                        ),
                    ),
                ),
            ),
            class_name="w-full md:w-[400px] bg-[#faf6eb] md:border-l-2 border-[#d4b886] shadow-2xl h-full overflow-y-auto p-4 sm:p-6 md:p-8 absolute inset-0 md:inset-auto md:right-0 md:top-0 z-40 animate-fade-in transition-all",
        ),
    )