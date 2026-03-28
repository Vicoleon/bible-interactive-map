import reflex as rx
from app.states.bible_state import BibleState


def search_filter_chip(label: str) -> rx.Component:
    return rx.el.button(
        label,
        on_click=lambda: BibleState.set_search_category(label),
        class_name="px-3 py-1 text-xs font-medium rounded-full transition-colors "
        + rx.cond(
            BibleState.search_category == label,
            "bg-[#8b5a2b] text-white shadow-sm",
            "bg-stone-200 text-stone-600 hover:bg-stone-300",
        ),
    )


def unified_search() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "search",
                size=18,
                class_name="absolute left-4 top-1/2 -translate-y-1/2 text-[#8b5a2b]",
            ),
            rx.el.input(
                placeholder="Buscar en la Biblia...",
                on_change=BibleState.update_unified_search,
                on_focus=lambda: BibleState.set_search_focused(True),
                class_name="w-full pl-12 pr-10 py-3 bg-white/90 border-2 border-[#d4b886] rounded-xl focus:outline-none focus:ring-4 focus:ring-[#8b5a2b]/30 focus:border-[#8b5a2b] text-stone-800 placeholder-stone-400 shadow-sm transition-all text-lg font-serif",
                default_value=BibleState.unified_search_query,
            ),
            rx.cond(
                BibleState.unified_search_query.length() > 0,
                rx.el.button(
                    rx.icon("x", size=16),
                    on_click=BibleState.clear_search,
                    class_name="absolute right-4 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-700 p-1 rounded-full hover:bg-stone-100 transition-colors",
                ),
            ),
            class_name="relative z-50",
        ),
        rx.cond(
            BibleState.search_focused,
            rx.el.div(
                search_filter_chip("Todos"),
                search_filter_chip("Personajes"),
                search_filter_chip("Eventos"),
                search_filter_chip("Escrituras"),
                search_filter_chip("Libros"),
                class_name="flex gap-2 justify-center mt-2 animate-fade-in",
            ),
        ),
        rx.cond(
            BibleState.search_focused & (BibleState.unified_search_query.length() >= 2),
            rx.el.div(
                rx.cond(
                    BibleState.total_search_results == 0,
                    rx.el.div(
                        "No se encontraron resultados para '"
                        + BibleState.unified_search_query
                        + "'",
                        class_name="text-center text-stone-500 py-8 italic font-serif",
                    ),
                    rx.el.div(
                        rx.cond(
                            BibleState.search_results_characters.length() > 0,
                            rx.el.div(
                                rx.el.h4(
                                    "👤 Personajes",
                                    class_name="text-sm font-bold text-purple-800 bg-purple-100 px-3 py-1 rounded-t-lg border-b border-purple-200",
                                ),
                                rx.el.div(
                                    rx.foreach(
                                        BibleState.search_results_characters,
                                        lambda char: rx.el.div(
                                            rx.el.span(
                                                char["emoji"],
                                                class_name="text-2xl w-10 h-10 flex items-center justify-center bg-stone-100 rounded-full shrink-0",
                                            ),
                                            rx.el.div(
                                                rx.el.div(
                                                    char["name"],
                                                    class_name="font-bold text-stone-800 group-hover:text-purple-700 transition-colors",
                                                ),
                                                rx.el.div(
                                                    char["role"] + " • " + char["era"],
                                                    class_name="text-xs text-stone-500",
                                                ),
                                                class_name="flex-1",
                                            ),
                                            on_click=lambda: BibleState.select_character(
                                                char["id"]
                                            ),
                                            class_name="flex items-center gap-3 p-3 hover:bg-purple-50 cursor-pointer transition-colors border-b border-stone-100 last:border-0 group",
                                        ),
                                    )
                                ),
                                class_name="mb-4 bg-white rounded-lg shadow-sm border border-stone-200",
                            ),
                        ),
                        rx.cond(
                            BibleState.search_results_events.length() > 0,
                            rx.el.div(
                                rx.el.h4(
                                    "📅 Eventos",
                                    class_name="text-sm font-bold text-amber-800 bg-amber-100 px-3 py-1 rounded-t-lg border-b border-amber-200",
                                ),
                                rx.el.div(
                                    rx.foreach(
                                        BibleState.search_results_events,
                                        lambda ev: rx.el.div(
                                            rx.el.span(
                                                ev["emoji"],
                                                class_name="text-2xl w-10 h-10 flex items-center justify-center bg-stone-100 rounded-full shrink-0",
                                            ),
                                            rx.el.div(
                                                rx.el.div(
                                                    ev["title"],
                                                    class_name="font-bold text-stone-800 group-hover:text-amber-700 transition-colors",
                                                ),
                                                rx.el.div(
                                                    ev["date_label"],
                                                    class_name="text-xs text-stone-500",
                                                ),
                                                class_name="flex-1",
                                            ),
                                            on_click=lambda: BibleState.select_event(
                                                ev["id"]
                                            ),
                                            class_name="flex items-center gap-3 p-3 hover:bg-amber-50 cursor-pointer transition-colors border-b border-stone-100 last:border-0 group",
                                        ),
                                    )
                                ),
                                class_name="mb-4 bg-white rounded-lg shadow-sm border border-stone-200",
                            ),
                        ),
                        rx.cond(
                            BibleState.search_results_scriptures.length() > 0,
                            rx.el.div(
                                rx.el.h4(
                                    "📖 Escrituras",
                                    class_name="text-sm font-bold text-blue-800 bg-blue-100 px-3 py-1 rounded-t-lg border-b border-blue-200",
                                ),
                                rx.el.div(
                                    rx.foreach(
                                        BibleState.search_results_scriptures,
                                        lambda ev: rx.el.div(
                                            rx.el.span(
                                                ev["emoji"],
                                                class_name="text-xl shrink-0",
                                            ),
                                            rx.el.div(
                                                rx.el.span(
                                                    ev["scripture_ref"],
                                                    class_name="font-bold text-blue-700 mr-1",
                                                ),
                                                rx.el.span(
                                                    "en " + ev["title"],
                                                    class_name="text-sm text-stone-600",
                                                ),
                                                class_name="flex-1",
                                            ),
                                            on_click=lambda: BibleState.select_event(
                                                ev["id"]
                                            ),
                                            class_name="flex items-center gap-3 p-3 hover:bg-blue-50 cursor-pointer transition-colors border-b border-stone-100 last:border-0",
                                        ),
                                    )
                                ),
                                class_name="mb-4 bg-white rounded-lg shadow-sm border border-stone-200",
                            ),
                        ),
                        rx.cond(
                            BibleState.search_results_books.length() > 0,
                            rx.el.div(
                                rx.el.h4(
                                    "📚 Libros",
                                    class_name="text-sm font-bold text-emerald-800 bg-emerald-100 px-3 py-1 rounded-t-lg border-b border-emerald-200",
                                ),
                                rx.el.div(
                                    rx.foreach(
                                        BibleState.search_results_books,
                                        lambda book: rx.el.div(
                                            rx.el.span(
                                                book["emoji"],
                                                class_name="text-2xl w-10 h-10 flex items-center justify-center bg-stone-100 rounded-full shrink-0",
                                            ),
                                            rx.el.div(
                                                rx.el.div(
                                                    book["name"],
                                                    class_name="font-bold text-stone-800 group-hover:text-emerald-700 transition-colors",
                                                ),
                                                rx.el.div(
                                                    book["category"]
                                                    + " • "
                                                    + book["chapters"].to_string()
                                                    + " cap.",
                                                    class_name="text-xs text-stone-500",
                                                ),
                                                class_name="flex-1",
                                            ),
                                            on_click=lambda: BibleState.select_book(
                                                book["id"]
                                            ),
                                            class_name="flex items-center gap-3 p-3 hover:bg-emerald-50 cursor-pointer transition-colors border-b border-stone-100 last:border-0 group",
                                        ),
                                    )
                                ),
                                class_name="mb-4 bg-white rounded-lg shadow-sm border border-stone-200",
                            ),
                        ),
                        rx.cond(
                            BibleState.scripture_search_loading
                            | (BibleState.scripture_search_results.length() > 0),
                            rx.el.div(
                                rx.el.h4(
                                    "📖 Versículos Encontrados",
                                    rx.el.span(
                                        "API.Bible",
                                        class_name="ml-2 text-[10px] bg-amber-200 text-amber-800 px-2 py-0.5 rounded-full uppercase tracking-wider",
                                    ),
                                    class_name="text-sm font-bold text-amber-900 bg-amber-100/80 px-3 py-2 rounded-t-lg border-b border-amber-200 flex items-center",
                                ),
                                rx.cond(
                                    BibleState.scripture_search_loading,
                                    rx.el.div(
                                        rx.icon(
                                            "loader",
                                            size=16,
                                            class_name="animate-spin text-amber-500 mr-2",
                                        ),
                                        rx.el.span(
                                            "Buscando en la Biblia...",
                                            class_name="text-sm text-stone-500 italic",
                                        ),
                                        class_name="flex items-center justify-center p-4 bg-amber-50/30",
                                    ),
                                    rx.el.div(
                                        rx.foreach(
                                            BibleState.scripture_search_results,
                                            lambda res: rx.el.div(
                                                rx.el.span(
                                                    "📖",
                                                    class_name="text-2xl w-10 h-10 flex items-center justify-center bg-white rounded-full shrink-0 shadow-sm border border-stone-100",
                                                ),
                                                rx.el.div(
                                                    rx.el.div(
                                                        res["reference"],
                                                        class_name="font-bold text-[#8b5a2b] font-serif group-hover:text-amber-700 transition-colors",
                                                    ),
                                                    rx.el.div(
                                                        res["text"],
                                                        class_name="text-xs text-stone-500 line-clamp-2 mt-1",
                                                    ),
                                                    class_name="flex-1",
                                                ),
                                                on_click=lambda: BibleState.select_scripture_result(
                                                    res
                                                ),
                                                class_name="flex items-center gap-3 p-3 bg-amber-50/30 hover:bg-amber-100/50 cursor-pointer transition-colors border-b border-stone-100 last:border-0 group",
                                            ),
                                        )
                                    ),
                                ),
                                class_name="mb-4 bg-white rounded-lg shadow-sm border border-stone-200 overflow-hidden",
                            ),
                        ),
                        rx.el.div(
                            BibleState.total_search_results.to_string()
                            + " resultados encontrados",
                            class_name="text-center text-xs text-stone-400 font-medium py-2",
                        ),
                    ),
                ),
                class_name="absolute top-full left-0 right-0 md:left-1/2 md:right-auto md:-translate-x-1/2 mt-4 w-full md:w-[480px] max-h-[70vh] md:max-h-[500px] overflow-y-auto bg-[#faf6eb] bg-[url('https://www.transparenttextures.com/patterns/aged-paper.png')] rounded-2xl shadow-[0_10px_40px_-10px_rgba(0,0,0,0.3)] border-2 border-[#d4b886] p-4 z-50 animate-fade-in no-scrollbar",
            ),
        ),
        class_name="relative w-full max-w-[500px]",
    )