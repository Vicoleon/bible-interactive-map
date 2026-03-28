import reflex as rx
from app.states.bible_state import BibleState
from app.components.unified_search import unified_search


def navigation() -> rx.Component:
    return rx.el.nav(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("book-open", class_name="text-[#8b5a2b] mr-3", size=28),
                    rx.el.h1(
                        "Mapa Bíblico",
                        class_name="text-2xl font-bold text-[#4a3320] font-serif tracking-wide whitespace-nowrap hidden sm:block",
                    ),
                    class_name="flex items-center shrink-0",
                ),
                rx.el.div(
                    unified_search(),
                    class_name="flex-1 hidden md:flex justify-center px-8",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("search", size=20),
                        on_click=BibleState.toggle_mobile_search,
                        class_name="md:hidden p-2 rounded-lg bg-white/50 border border-[#d4b886] text-[#8b5a2b]",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.el.span("🗺️ "),
                            rx.el.span("Mapa", class_name="hidden sm:inline"),
                            on_click=lambda: BibleState.set_active_view("map"),
                            class_name="px-3 sm:px-4 py-2 rounded-l-lg border border-[#d4b886] font-medium transition-colors "
                            + rx.cond(
                                BibleState.active_view == "map",
                                "bg-[#8b5a2b] text-white",
                                "bg-white/80 text-stone-700 hover:bg-stone-100",
                            ),
                        ),
                        rx.el.button(
                            rx.el.span("📜 "),
                            rx.el.span("Cronología", class_name="hidden sm:inline"),
                            on_click=lambda: BibleState.set_active_view("timeline"),
                            class_name="px-3 sm:px-4 py-2 rounded-r-lg border border-l-0 border-[#d4b886] font-medium transition-colors "
                            + rx.cond(
                                BibleState.active_view == "timeline",
                                "bg-[#8b5a2b] text-white",
                                "bg-white/80 text-stone-700 hover:bg-stone-100",
                            ),
                        ),
                        class_name="flex items-center shadow-sm",
                    ),
                    rx.cond(
                        (BibleState.view_state != "overview")
                        & (BibleState.active_view == "map"),
                        rx.el.button(
                            rx.icon("arrow-left", size=18),
                            rx.el.span("Volver", class_name="hidden sm:inline ml-2"),
                            on_click=lambda: BibleState.set_view("overview"),
                            class_name="flex items-center px-3 py-2 bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-lg border border-stone-300 font-medium transition-colors shadow-sm",
                        ),
                    ),
                    class_name="flex items-center gap-2 sm:gap-4 shrink-0",
                ),
                class_name="max-w-7xl w-full mx-auto flex justify-between items-center",
            ),
            rx.cond(
                BibleState.search_mobile_open,
                rx.el.div(
                    unified_search(),
                    class_name="md:hidden mt-3 max-w-7xl mx-auto w-full animate-fade-in",
                ),
            ),
            class_name="w-full",
        ),
        rx.cond(
            (BibleState.view_state != "overview") & (BibleState.active_view == "map"),
            rx.el.div(
                rx.el.div(
                    rx.foreach(
                        BibleState.eras,
                        lambda era: rx.el.button(
                            era,
                            on_click=lambda: BibleState.set_era(era),
                            class_name="px-3 py-1 text-sm font-medium rounded-full whitespace-nowrap transition-colors "
                            + rx.cond(
                                (BibleState.selected_era == era)
                                | (era == "Todos") & (BibleState.selected_era == "All"),
                                "bg-[#8b5a2b] text-white shadow-md",
                                "bg-white/50 text-[#8b5a2b] hover:bg-[#8b5a2b]/20 border border-[#d4b886]",
                            ),
                        ),
                    ),
                    class_name="flex gap-2 overflow-x-auto py-2 pb-2 no-scrollbar",
                ),
                rx.cond(
                    BibleState.is_filtering,
                    rx.el.div(
                        rx.el.span(
                            BibleState.match_count.to_string() + " coincidencias",
                            class_name="text-sm font-bold text-[#8b5a2b]",
                        ),
                        class_name="ml-4 shrink-0",
                    ),
                ),
                class_name="max-w-7xl mx-auto flex items-center mt-2",
            ),
        ),
        class_name="bg-[#f5e9d3]/90 backdrop-blur-md border-b-2 border-[#d4b886] p-4 sticky top-0 z-40 shadow-sm flex flex-col",
    )