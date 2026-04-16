import reflex as rx
from app.states.bible_state import BibleState, ALL_BIBLE_BOOKS


def testament_filter() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            "Todos",
            on_click=lambda: BibleState.set_reader_testament_filter("all"),
            class_name="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors "
            + rx.cond(
                BibleState.reader_testament_filter == "all",
                "bg-[#8b5a2b] text-white",
                "bg-white text-stone-600 hover:bg-stone-100 border border-stone-200",
            ),
        ),
        rx.el.button(
            "Antiguo T.",
            on_click=lambda: BibleState.set_reader_testament_filter("AT"),
            class_name="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors "
            + rx.cond(
                BibleState.reader_testament_filter == "AT",
                "bg-[#8b5a2b] text-white",
                "bg-white text-stone-600 hover:bg-stone-100 border border-stone-200",
            ),
        ),
        rx.el.button(
            "Nuevo T.",
            on_click=lambda: BibleState.set_reader_testament_filter("NT"),
            class_name="px-3 py-1.5 text-sm font-medium rounded-lg transition-colors "
            + rx.cond(
                BibleState.reader_testament_filter == "NT",
                "bg-[#8b5a2b] text-white",
                "bg-white text-stone-600 hover:bg-stone-100 border border-stone-200",
            ),
        ),
        class_name="flex gap-2 p-3 border-b border-[#d4b886]",
    )


def book_row(book: dict) -> rx.Component:
    is_expanded = BibleState.reader_expanded_book == book["api_id"]
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                book["name"],
                class_name="font-serif font-semibold text-stone-800 text-base",
            ),
            rx.icon(
                rx.cond(is_expanded, "chevron-down", "chevron-right"),
                size=20,
                class_name="text-stone-400 transition-transform",
            ),
            on_click=lambda: BibleState.toggle_reader_book(book["api_id"]),
            class_name="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-[#f5e9d3] transition-colors border-b border-stone-200 "
            + rx.cond(is_expanded, "bg-[#f5e9d3]", ""),
        ),
        rx.cond(
            is_expanded,
            rx.el.div(
                rx.foreach(
                    BibleState.reader_chapter_list,
                    lambda ch: rx.el.button(
                        ch.to_string(),
                        on_click=lambda: BibleState.select_reader_chapter(
                            book["api_id"], book["name"], ch
                        ),
                        class_name="w-10 h-10 rounded-lg text-sm font-medium transition-all flex items-center justify-center "
                        + rx.cond(
                            (BibleState.reader_selected_book == book["api_id"])
                            & (BibleState.reader_selected_chapter == ch),
                            "bg-[#8b5a2b] text-white shadow-md",
                            "bg-white text-stone-700 border border-stone-200 hover:border-[#8b5a2b] hover:text-[#8b5a2b]",
                        ),
                    ),
                ),
                class_name="grid grid-cols-6 sm:grid-cols-8 gap-2 p-4 bg-[#faf6eb] border-b border-stone-200 animate-fade-in",
            ),
        ),
    )


def scripture_display() -> rx.Component:
    return rx.cond(
        BibleState.reader_selected_chapter > 0,
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    rx.icon("chevron-left", size=20),
                    on_click=BibleState.reader_prev_chapter,
                    disabled=BibleState.reader_selected_chapter <= 1,
                    class_name="p-2 rounded-lg bg-stone-100 hover:bg-stone-200 transition-colors disabled:opacity-30 disabled:cursor-not-allowed",
                ),
                rx.el.div(
                    rx.el.div(
                        BibleState.reader_selected_book_name,
                        class_name="font-serif font-bold text-[#4a3320] text-lg sm:text-xl text-center",
                    ),
                    rx.el.div(
                        "Capítulo " + BibleState.reader_selected_chapter.to_string(),
                        class_name="text-sm text-[#8b5a2b] text-center font-medium",
                    ),
                    class_name="flex flex-col flex-1",
                ),
                rx.el.button(
                    rx.icon("chevron-right", size=20),
                    on_click=BibleState.reader_next_chapter,
                    disabled=BibleState.reader_selected_chapter
                    >= BibleState.reader_max_chapters,
                    class_name="p-2 rounded-lg bg-stone-100 hover:bg-stone-200 transition-colors disabled:opacity-30 disabled:cursor-not-allowed",
                ),
                class_name="flex items-center justify-between px-4 py-3 bg-[#f5e9d3] border-b border-[#d4b886] sticky top-0 z-10",
            ),
            rx.cond(
                BibleState.reader_loading,
                rx.el.div(
                    rx.icon(
                        "loader",
                        size=32,
                        class_name="animate-spin text-[#8b5a2b] mx-auto mb-4",
                    ),
                    rx.el.p(
                        "Cargando capítulo...",
                        class_name="text-stone-500 text-center italic font-serif",
                    ),
                    class_name="flex flex-col items-center justify-center py-20",
                ),
                rx.el.div(
                    rx.el.div(
                        BibleState.reader_text,
                        class_name="font-serif text-stone-800 text-lg leading-loose text-justify whitespace-pre-wrap",
                    ),
                    class_name="bg-[url('https://www.transparenttextures.com/patterns/aged-paper.png')] bg-[#f4ebd8] p-5 sm:p-8 m-3 sm:m-4 rounded-2xl shadow-inner border-2 border-[#d4b886]",
                ),
            ),
            class_name="flex-1 overflow-y-auto",
        ),
        rx.el.div(
            rx.el.div("📖", class_name="text-6xl mb-4"),
            rx.el.div(
                "Lector Bíblico",
                class_name="font-serif font-bold text-[#4a3320] text-2xl mb-2",
            ),
            rx.el.div(
                "Selecciona un libro y capítulo para comenzar a leer.",
                class_name="text-stone-500 text-center font-serif italic",
            ),
            class_name="flex flex-col items-center justify-center h-full px-8",
        ),
    )


def bible_reader() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            testament_filter(),
            rx.el.div(
                rx.foreach(BibleState.all_bible_books_list, book_row),
                class_name="overflow-y-auto flex-1 no-scrollbar",
            ),
            class_name="w-full md:w-[340px] flex flex-col border-r-0 md:border-r-2 border-[#d4b886] bg-[#faf6eb] "
            + rx.cond(BibleState.reader_selected_chapter > 0, "hidden md:flex", "flex"),
        ),
        rx.el.div(
            rx.cond(
                BibleState.reader_selected_chapter > 0,
                rx.el.div(
                    rx.el.button(
                        rx.icon("arrow-left", size=18),
                        rx.el.span("Libros", class_name="ml-2 text-sm font-medium"),
                        on_click=lambda: BibleState.set_reader_selected_chapter_zero(),
                        class_name="md:hidden flex items-center px-3 py-2 bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-lg border border-stone-300 m-3",
                    )
                ),
                rx.fragment(),
            ),
            scripture_display(),
            class_name="flex-1 flex flex-col bg-[#faf6eb] overflow-hidden "
            + rx.cond(BibleState.reader_selected_chapter > 0, "flex", "hidden md:flex"),
        ),
        class_name="w-full h-[calc(100vh-80px)] flex flex-col md:flex-row overflow-hidden",
    )