import reflex as rx
from app.states.bible_state import BibleState, Character


def get_node_style(role: str) -> str:
    return rx.match(
        role,
        ("Profeta", "border-purple-600 bg-purple-50 text-purple-900 shadow-purple-200"),
        ("Rey", "border-yellow-500 bg-yellow-50 text-yellow-900 shadow-yellow-200"),
        ("Reina", "border-yellow-500 bg-yellow-50 text-yellow-900 shadow-yellow-200"),
        ("Apóstol", "border-blue-600 bg-blue-50 text-blue-900 shadow-blue-200"),
        ("Patriarca", "border-amber-700 bg-amber-50 text-amber-900 shadow-amber-200"),
        ("Matriarca", "border-amber-700 bg-amber-50 text-amber-900 shadow-amber-200"),
        (
            "Mesías",
            "border-indigo-600 bg-indigo-50 text-indigo-900 shadow-indigo-300 ring-2 ring-indigo-400 ring-offset-2 ring-offset-[#faf6eb]",
        ),
        "border-stone-500 bg-stone-50 text-stone-800 shadow-stone-200",
    )


def render_character_node(char: Character) -> rx.Component:
    is_selected = BibleState.selected_character_id == char["id"]
    is_hovered = BibleState.hovered_character_id == char["id"]
    is_matched = BibleState.matched_character_ids.contains(char["id"])
    is_dimmed = BibleState.is_filtering & ~is_matched
    return rx.el.div(
        rx.el.div(
            rx.el.span(char["emoji"], class_name="text-2xl"),
            class_name=f"w-16 h-16 rounded-full border-4 flex items-center justify-center shadow-lg transition-all duration-300 cursor-pointer {get_node_style(char['role'])} "
            + rx.cond(
                is_selected,
                "scale-110 ring-4 ring-[#8b5a2b] ring-offset-2 ring-offset-[#faf6eb]",
                "",
            )
            + rx.cond(is_hovered, "scale-110 shadow-xl z-20", "")
            + rx.cond(
                is_matched & BibleState.is_filtering,
                " ring-2 ring-amber-400 shadow-[0_0_15px_rgba(251,191,36,0.8)]",
                "",
            ),
            on_click=lambda: BibleState.select_character(char["id"]),
            on_mouse_enter=lambda: BibleState.set_hovered(char["id"]),
            on_mouse_leave=BibleState.clear_hovered,
        ),
        rx.el.div(
            rx.el.div(
                char["name"],
                class_name="font-bold text-sm text-[#4a3320] text-center drop-shadow-md whitespace-nowrap",
            ),
            rx.el.div(
                char["role"],
                class_name="text-[10px] text-stone-600 text-center font-medium bg-white/70 px-1 rounded-full whitespace-nowrap",
            ),
            class_name="absolute top-full left-1/2 -translate-x-1/2 mt-2 flex flex-col items-center pointer-events-none",
        ),
        class_name="absolute transform -translate-x-1/2 -translate-y-1/2 z-10 transition-opacity duration-300 "
        + rx.cond(is_dimmed, "opacity-20 grayscale", "opacity-100"),
        style={"left": f"{char['x']}%", "top": f"{char['y']}%"},
    )


def overview_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Antiguo Testamento",
                    class_name="text-2xl md:text-4xl font-serif font-bold text-[#4a3320] mb-4 text-center",
                ),
                rx.el.p(
                    "Ley, Profetas y Escritos",
                    class_name="text-[#8b5a2b] text-center font-medium text-lg italic mb-8",
                ),
                rx.el.div(
                    rx.icon("scroll", size=48, class_name="text-[#d4b886] mb-6"),
                    rx.el.button(
                        "Explorar Antiguo Testamento",
                        on_click=lambda: BibleState.set_view("old_testament"),
                        class_name="px-6 py-3 md:px-8 md:py-4 bg-[#8b5a2b] hover:bg-[#6b421a] text-white rounded-xl shadow-lg hover:shadow-xl transition-all text-base md:text-lg font-bold",
                    ),
                    class_name="flex flex-col items-center justify-center h-40 md:h-64",
                ),
                class_name="flex-1 bg-[#faf6eb] rounded-3xl p-6 md:p-10 shadow-2xl border-4 border-[#e8d5b5] hover:border-[#8b5a2b] transition-all duration-500 cursor-pointer group hover:-translate-y-2 relative overflow-hidden",
                on_click=lambda: BibleState.set_view("old_testament"),
            ),
            rx.el.div(
                rx.el.h2(
                    "Nuevo Testamento",
                    class_name="text-2xl md:text-4xl font-serif font-bold text-[#4a3320] mb-4 text-center",
                ),
                rx.el.p(
                    "Evangelios, Hechos y Epístolas",
                    class_name="text-[#8b5a2b] text-center font-medium text-lg italic mb-8",
                ),
                rx.el.div(
                    rx.icon(
                        "book-open-text", size=48, class_name="text-[#d4b886] mb-6"
                    ),
                    rx.el.button(
                        "Explorar Nuevo Testamento",
                        on_click=lambda: BibleState.set_view("new_testament"),
                        class_name="px-6 py-3 md:px-8 md:py-4 bg-[#8b5a2b] hover:bg-[#6b421a] text-white rounded-xl shadow-lg hover:shadow-xl transition-all text-base md:text-lg font-bold",
                    ),
                    class_name="flex flex-col items-center justify-center h-40 md:h-64",
                ),
                class_name="flex-1 bg-[#faf6eb] rounded-3xl p-6 md:p-10 shadow-2xl border-4 border-[#e8d5b5] hover:border-[#8b5a2b] transition-all duration-500 cursor-pointer group hover:-translate-y-2 relative overflow-hidden",
                on_click=lambda: BibleState.set_view("new_testament"),
            ),
            class_name="flex flex-col md:flex-row gap-6 md:gap-12 w-full max-w-6xl mx-auto mt-8 md:mt-20 p-4",
        ),
        class_name="w-full h-[calc(100vh-80px)] flex flex-col items-center bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#eaddc5] to-[#d4b886] overflow-y-auto",
    )


def render_svg_line(line: dict) -> rx.Component:
    color_class = rx.match(
        line["type"],
        ("familia", "stroke-[#8b5a2b]"),
        ("mentor", "stroke-blue-400"),
        ("aliado", "stroke-green-500"),
        ("profecía", "stroke-amber-400"),
        ("linaje", "stroke-stone-400"),
        "stroke-stone-300",
    )
    dash_array = rx.match(
        line["type"],
        ("familia", "none"),
        ("mentor", "8, 8"),
        ("aliado", "4, 4"),
        ("profecía", "12, 12"),
        ("linaje", "none"),
        "none",
    )
    stroke_width = rx.cond(line["type"] == "profecía", "4", "2")
    opacity_class = rx.cond(
        line["is_dimmed"],
        "opacity-10",
        rx.cond(
            line["is_active"],
            "opacity-100 drop-shadow-[0_0_8px_rgba(251,191,36,0.8)]",
            "opacity-50",
        ),
    )
    return rx.el.svg.line(
        x1=f"{line['x1']}%",
        y1=f"{line['y1']}%",
        x2=f"{line['x2']}%",
        y2=f"{line['y2']}%",
        class_name=f"{color_class} {opacity_class} transition-all duration-300",
        stroke_width=stroke_width,
        stroke_dasharray=dash_array,
    )


def legend_line_sample(type_name: str, color: str, dash: str) -> rx.Component:
    return rx.el.div(
        rx.el.svg(
            rx.el.svg.line(
                x1="0",
                y1="4",
                x2="24",
                y2="4",
                stroke=color,
                stroke_width="2",
                stroke_dasharray=dash,
                class_name=rx.cond(type_name == "Profecía", "animate-flow", ""),
            ),
            class_name="w-6 h-2 mr-2",
            viewBox="0 0 24 8",
        ),
        rx.el.span(type_name, class_name="text-xs text-stone-600 font-medium"),
        class_name="flex items-center",
    )


def era_label(text: str, top: str) -> rx.Component:
    return rx.fragment(
        rx.el.div(
            text,
            class_name="absolute left-4 text-sm font-serif font-bold text-[#8b5a2b]/60 uppercase tracking-wider pointer-events-none",
            style={"top": top},
        ),
        rx.el.div(
            class_name="absolute left-[10%] right-[10%] h-px bg-[#d4b886]/30 pointer-events-none",
            style={"top": top},
        ),
    )


def ot_era_labels() -> rx.Component:
    return rx.fragment(
        era_label("🌍 Creación", "2%"),
        era_label("🌊 Pre-Diluvio", "9%"),
        era_label("⛺ Patriarcal", "16%"),
        era_label("🏜️ Éxodo", "40%"),
        era_label("⚔️ Conquista & Jueces", "53%"),
        era_label("👑 Reino Unido", "69%"),
        era_label("💔 Reino Dividido", "81%"),
        era_label("⛓️ Exilio", "89%"),
        era_label("🧱 Post-Exilio", "95%"),
    )


def nt_era_labels() -> rx.Component:
    return rx.fragment(
        era_label("✨ Evangelios", "6%"), era_label("🕊️ Iglesia Primitiva", "59%")
    )


def testament_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    class_name="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/aged-paper.png')] opacity-50 pointer-events-none"
                ),
                rx.el.svg(
                    rx.foreach(BibleState.connection_lines, render_svg_line),
                    class_name="absolute inset-0 w-full h-full pointer-events-none z-0",
                ),
                rx.cond(
                    BibleState.view_state == "old_testament",
                    ot_era_labels(),
                    nt_era_labels(),
                ),
                rx.foreach(BibleState.visible_characters, render_character_node),
                class_name="relative w-full bg-[#faf6eb] border-8 border-double border-[#d4b886] rounded-3xl shadow-[inset_0_0_100px_rgba(139,90,43,0.2)] overflow-visible mx-auto",
                style={"height": BibleState.map_canvas_height, "max-width": "1200px"},
                on_mount=BibleState.auto_close_legend,
            ),
            class_name="p-8 min-h-[2200px]",
        ),
        rx.el.div(
            rx.cond(
                BibleState.legend_expanded,
                rx.el.div(
                    rx.el.button(
                        rx.icon("x", size=16),
                        on_click=BibleState.toggle_legend,
                        class_name="absolute top-2 right-2 p-1 text-stone-400 hover:text-stone-800 transition-colors",
                    ),
                    rx.el.h3(
                        "Leyenda del Mapa",
                        class_name="font-serif font-bold text-[#4a3320] mb-3 border-b border-[#d4b886] pb-1 flex items-center gap-2",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Roles",
                            class_name="text-[10px] uppercase tracking-wider text-stone-500 font-bold mb-2",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    class_name="w-3 h-3 rounded-full bg-purple-500 mr-2"
                                ),
                                rx.el.span(
                                    "Profeta", class_name="text-sm text-stone-700"
                                ),
                                class_name="flex items-center",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name="w-3 h-3 rounded-full bg-yellow-500 mr-2"
                                ),
                                rx.el.span(
                                    "Realeza", class_name="text-sm text-stone-700"
                                ),
                                class_name="flex items-center",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name="w-3 h-3 rounded-full bg-blue-500 mr-2"
                                ),
                                rx.el.span(
                                    "Apóstol", class_name="text-sm text-stone-700"
                                ),
                                class_name="flex items-center",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    class_name="w-3 h-3 rounded-full bg-amber-700 mr-2"
                                ),
                                rx.el.span(
                                    "Patriarca", class_name="text-sm text-stone-700"
                                ),
                                class_name="flex items-center",
                            ),
                            class_name="grid grid-cols-2 gap-x-4 gap-y-2 mb-4",
                        ),
                        rx.el.p(
                            "Conexiones",
                            class_name="text-[10px] uppercase tracking-wider text-stone-500 font-bold mb-2",
                        ),
                        rx.el.div(
                            legend_line_sample("Familia", "#8b5a2b", "none"),
                            legend_line_sample("Mentor", "#60a5fa", "4, 4"),
                            legend_line_sample("Aliado", "#22c55e", "2, 2"),
                            legend_line_sample("Profecía", "#fbbf24", "6, 6"),
                            legend_line_sample("Linaje", "#a8a29e", "none"),
                            class_name="flex flex-col gap-1",
                        ),
                    ),
                    class_name="bg-[#faf6eb] backdrop-blur-sm p-5 rounded-2xl shadow-2xl border-2 border-[#d4b886] animate-fade-in w-64",
                ),
                rx.el.button(
                    rx.icon("map", size=24, class_name="text-[#8b5a2b]"),
                    rx.el.div(
                        "Leyenda",
                        class_name="absolute left-full ml-4 px-2 py-1 bg-stone-800 text-white text-[10px] rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none",
                    ),
                    on_click=BibleState.toggle_legend,
                    class_name="group relative w-12 h-12 rounded-full bg-[#faf6eb] border-2 border-[#d4b886] shadow-lg flex items-center justify-center hover:scale-110 hover:shadow-[0_0_15px_rgba(139,90,43,0.3)] transition-all duration-300",
                ),
            ),
            class_name="fixed bottom-4 left-4 md:bottom-12 md:left-12 z-40 transition-all duration-500",
        ),
        class_name="w-full h-[calc(100vh-80px)] overflow-y-auto no-scrollbar bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#eaddc5] to-[#d4b886] relative",
    )


def map_canvas() -> rx.Component:
    return rx.match(
        BibleState.view_state,
        ("overview", overview_view()),
        ("old_testament", testament_view()),
        ("new_testament", testament_view()),
        overview_view(),
    )