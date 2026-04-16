import reflex as rx

from app.data.saints import SaintRecord
from app.states.saints_state import SaintsState


def stat_block(label: str, value: rx.Var | int) -> rx.Component:
    return rx.el.div(
        rx.el.div(value, class_name="text-xl 2xl:text-lg font-bold font-serif text-[#4a3320] leading-none"),
        rx.el.div(
            label,
            class_name="text-[11px] 2xl:text-[10px] uppercase tracking-wider text-stone-500 font-semibold mt-1",
        ),
        class_name="min-w-24 2xl:min-w-20 border-l border-[#d4b886] pl-4 2xl:pl-3",
    )


def filter_button(label: str, active: rx.Var, action) -> rx.Component:
    return rx.el.button(
        label,
        on_click=action,
        class_name="px-3 py-1.5 text-sm font-semibold rounded-full border transition-colors whitespace-nowrap "
        + rx.cond(
            active,
            "bg-[#4a3320] text-white border-[#4a3320]",
            "bg-white/70 text-stone-700 border-[#d4b886] hover:bg-[#f5e9d3]",
        ),
    )


def saint_chip(label: str) -> rx.Component:
    return rx.el.span(
        label,
        class_name="px-2.5 py-1 rounded-full bg-[#f5e9d3] border border-[#d4b886] text-xs font-semibold text-[#6b421a]",
    )


def timeline_entry(saint: SaintRecord) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.el.div(
                class_name="w-3 h-3 rounded-full bg-[#8b5a2b] border-2 border-[#faf6eb] shadow-sm "
                + rx.cond(
                    SaintsState.selected_saint_id == saint["id"],
                    "scale-150 bg-[#4a3320]",
                    "",
                ),
            ),
            class_name="relative z-10 w-8 flex justify-center pt-1",
        ),
        rx.el.div(
            rx.el.div(
                saint["date_label"],
                class_name="text-xs font-bold text-[#8b5a2b] mb-1",
            ),
            rx.el.h3(
                saint["name"],
                class_name="font-serif text-base font-bold text-[#4a3320] text-left leading-tight",
            ),
            rx.el.div(
                rx.el.span(saint["honorific"]),
                rx.el.span(" • "),
                rx.el.span(saint["period"]),
                class_name="text-xs font-semibold text-[#8b5a2b] text-left",
            ),
            rx.el.p(
                saint["summary"],
                class_name="text-xs text-stone-600 text-left leading-snug line-clamp-2 mt-2",
            ),
            class_name="flex-1 min-w-0",
        ),
        on_click=lambda: SaintsState.set_selected_saint(saint["id"]),
        class_name="relative w-full flex items-start gap-2 py-4 pr-3 hover:bg-white/70 transition-colors text-left "
        + rx.cond(
            SaintsState.selected_saint_id == saint["id"],
            "bg-white shadow-[inset_4px_0_0_#8b5a2b]",
            "bg-transparent",
        ),
    )


def selected_saint_detail() -> rx.Component:
    return rx.cond(
        SaintsState.selected_saint,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        SaintsState.selected_saint["category"],
                        class_name="text-xs uppercase tracking-wider font-bold text-[#8b5a2b] mb-2",
                    ),
                    rx.el.h2(
                        SaintsState.selected_saint["name"],
                        class_name="text-3xl md:text-4xl font-bold font-serif text-[#4a3320] leading-tight",
                    ),
                    rx.el.p(
                        SaintsState.selected_saint["honorific"],
                        class_name="text-lg italic text-[#8b5a2b] mt-1",
                    ),
                    class_name="min-w-0",
                ),
                rx.el.div(
                    SaintsState.selected_saint["date_label"],
                    class_name="px-4 py-2 bg-[#4a3320] text-white rounded-lg font-bold whitespace-nowrap",
                ),
                class_name="flex items-start justify-between gap-4 border-b border-[#d4b886] pb-5",
            ),
            rx.el.div(
                saint_chip(SaintsState.selected_saint["period"]),
                saint_chip(SaintsState.selected_saint["region"]),
                saint_chip(SaintsState.selected_saint["feast_day"]),
                class_name="flex flex-wrap gap-2 mt-5",
            ),
            rx.el.p(
                SaintsState.selected_saint["summary"],
                class_name="text-lg leading-relaxed text-stone-800 font-serif italic border-l-4 border-[#8b5a2b] pl-4 mt-6",
            ),
            rx.el.div(
                rx.el.h3("Historia", class_name="font-serif text-2xl font-bold text-[#4a3320] mb-3"),
                rx.el.div(
                    rx.foreach(
                        SaintsState.selected_history_paragraphs,
                        lambda paragraph: rx.el.p(
                            paragraph,
                            class_name="text-stone-700 leading-relaxed mb-5 text-base md:text-lg",
                        ),
                    ),
                    class_name="max-w-none",
                ),
                class_name="mt-8",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h3("Materiales y obras", class_name="font-serif text-xl font-bold text-[#4a3320] mb-3"),
                    rx.el.ul(
                        rx.foreach(
                            SaintsState.selected_writings,
                            lambda item: rx.el.li(
                                rx.icon("book-open", size=15, class_name="text-[#8b5a2b] mt-0.5 shrink-0"),
                                rx.el.span(item),
                                class_name="flex gap-2 text-sm text-stone-700 py-1.5",
                            ),
                        ),
                    ),
                    class_name="bg-white/55 border border-[#ead8b8] rounded-lg p-4",
                ),
                rx.el.div(
                    rx.el.h3("Temas", class_name="font-serif text-xl font-bold text-[#4a3320] mb-3"),
                    rx.el.div(
                        rx.foreach(SaintsState.selected_themes, saint_chip),
                        class_name="flex flex-wrap gap-2",
                    ),
                    rx.el.div(
                        rx.el.div("Patronazgo", class_name="text-xs uppercase tracking-wider font-bold text-stone-500 mt-5 mb-1"),
                        rx.el.p(SaintsState.selected_saint["patronage"], class_name="text-sm text-stone-700"),
                        rx.el.div("Lugar", class_name="text-xs uppercase tracking-wider font-bold text-stone-500 mt-4 mb-1"),
                        rx.el.p(SaintsState.selected_saint["location"], class_name="text-sm text-stone-700"),
                    ),
                    class_name="bg-white/55 border border-[#ead8b8] rounded-lg p-4",
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-8",
            ),
            rx.cond(
                SaintsState.selected_related_saints.length() > 0,
                rx.el.div(
                    rx.el.h3("Conexiones", class_name="font-serif text-xl font-bold text-[#4a3320] mb-3"),
                    rx.el.div(
                        rx.foreach(
                            SaintsState.selected_related_saints,
                            lambda saint: rx.el.button(
                                saint["name"],
                                on_click=lambda: SaintsState.set_selected_saint(saint["id"]),
                                class_name="text-sm font-semibold text-[#8b5a2b] hover:text-[#4a3320] px-3 py-2 bg-white/60 border border-[#ead8b8] rounded-lg",
                            ),
                        ),
                        class_name="flex flex-wrap gap-2",
                    ),
                    class_name="mt-8",
                ),
            ),
            class_name="bg-[#faf6eb] border-2 border-[#d4b886] rounded-xl shadow-sm p-5 md:p-8",
        ),
        rx.el.div(
            "Selecciona un santo para ver su ficha.",
            class_name="bg-[#faf6eb] border-2 border-[#d4b886] rounded-xl p-8 text-center text-stone-600",
        ),
    )


def saints_wiki() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Antologia catolica",
                            class_name="text-xs uppercase tracking-[0.22em] font-bold text-[#8b5a2b] mb-2",
                        ),
                        rx.el.h1(
                            "Santos, Padres y Doctores de la Fe",
                            class_name="text-3xl md:text-5xl font-serif font-bold text-[#4a3320] leading-tight max-w-none",
                        ),
                        rx.el.p(
                            "Una cronologia navegable para estudiar vidas, historia, escritos y grandes temas de la santidad catolica.",
                            class_name="text-base text-stone-700 mt-3 max-w-none leading-relaxed",
                        ),
                        class_name="flex-1 min-w-0",
                    ),
                    class_name="max-w-[96rem] mx-auto px-5 md:px-8 pt-6 pb-5",
                ),
                class_name="bg-[#f5e9d3] border-b border-[#d4b886]",
            ),
            rx.el.section(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon("search", size=18, class_name="absolute left-4 top-1/2 -translate-y-1/2 text-[#8b5a2b]"),
                            rx.el.input(
                                placeholder="Buscar por nombre, epoca, tema, obra o lugar...",
                                value=SaintsState.search_query,
                                on_change=SaintsState.set_search_query,
                                class_name="w-full pl-11 pr-10 py-3 bg-white border-2 border-[#d4b886] rounded-lg focus:outline-none focus:ring-4 focus:ring-[#8b5a2b]/20 text-stone-800",
                            ),
                            rx.cond(
                                SaintsState.search_query.length() > 0,
                                rx.el.button(
                                    rx.icon("x", size=16),
                                    on_click=SaintsState.clear_search_query,
                                    class_name="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-stone-500 hover:text-[#4a3320]",
                                ),
                            ),
                            class_name="relative",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("Epoca", class_name="text-xs uppercase tracking-wider font-bold text-stone-500 mr-2"),
                                rx.foreach(
                                    SaintsState.periods,
                                    lambda period: filter_button(
                                        period,
                                        SaintsState.selected_period == period,
                                        lambda: SaintsState.set_period(period),
                                    ),
                                ),
                                class_name="flex items-center gap-2 overflow-x-auto no-scrollbar py-2",
                            ),
                            rx.el.div(
                                rx.el.span("Tipo", class_name="text-xs uppercase tracking-wider font-bold text-stone-500 mr-2"),
                                rx.foreach(
                                    SaintsState.categories,
                                    lambda category: filter_button(
                                        category,
                                        SaintsState.selected_category == category,
                                        lambda: SaintsState.set_category(category),
                                    ),
                                ),
                                class_name="flex items-center gap-2 overflow-x-auto no-scrollbar py-2",
                            ),
                            class_name="mt-3",
                        ),
                        class_name="lg:col-span-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            SaintsState.filtered_count,
                            class_name="text-3xl font-bold font-serif text-[#4a3320]",
                        ),
                        rx.el.div("resultados", class_name="text-sm text-stone-500 font-semibold"),
                        rx.el.div(
                            rx.el.span(SaintsState.saints.length()),
                            rx.el.span(" santos · "),
                            rx.el.span(SaintsState.doctors_count),
                            rx.el.span(" doctores · "),
                            rx.el.span(SaintsState.writings_count),
                            rx.el.span(" materiales"),
                            class_name="text-xs text-stone-500 mt-3 leading-relaxed",
                        ),
                        class_name="bg-white/60 border border-[#d4b886] rounded-lg p-4 text-center",
                    ),
                    class_name="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-5 gap-4 px-5 md:px-8 py-5",
                ),
                class_name="bg-[#ead8b8]/55 border-b border-[#d4b886]",
            ),
            rx.el.section(
                rx.el.div(
                    rx.el.aside(
                        rx.el.div(
                            rx.el.h2(
                                "Cronologia",
                                class_name="font-serif text-2xl font-bold text-[#4a3320]",
                            ),
                            rx.el.p(
                                "Selecciona un santo para leer su historia completa.",
                                class_name="text-sm text-stone-600 mt-1",
                            ),
                            class_name="px-4 pt-4 pb-3 border-b border-[#d4b886]",
                        ),
                        rx.el.div(
                            rx.el.div(
                                class_name="absolute left-4 top-0 bottom-0 w-px bg-[#d4b886]",
                            ),
                            rx.foreach(SaintsState.filtered_saints, timeline_entry),
                            class_name="relative pl-0",
                        ),
                        class_name="lg:sticky lg:top-28 lg:self-start max-h-[76vh] overflow-y-auto no-scrollbar bg-[#fdf9ef] border border-[#d4b886] rounded-lg",
                    ),
                    rx.el.div(
                        selected_saint_detail(),
                        class_name="min-w-0",
                    ),
                    class_name="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-[380px_1fr] gap-6 px-5 md:px-8 py-8",
                ),
            ),
            class_name="min-h-full bg-[#faf6eb]",
        ),
        class_name="w-full h-[calc(100vh-80px)] overflow-y-auto bg-[#faf6eb]",
    )
