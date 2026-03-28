import reflex as rx
from app.states.bible_state import BibleState, BibleEvent, EraGroup


def render_event_card(event: BibleEvent, index: int) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(event["emoji"], class_name="text-4xl"),
                class_name="w-16 h-16 bg-[#faf6eb] rounded-full flex items-center justify-center border-4 border-[#d4b886] shadow-md z-10 shrink-0",
            ),
            rx.el.div(
                rx.el.h3(
                    event["title"],
                    class_name="text-xl font-bold font-serif text-[#4a3320] mb-1",
                ),
                rx.el.div(
                    rx.el.span(
                        event["date_label"],
                        class_name="text-xs font-semibold text-stone-500 bg-stone-100 px-2 py-1 rounded-full border border-stone-200",
                    ),
                    rx.el.span(
                        event["scripture_ref"],
                        class_name="text-xs font-semibold text-stone-500 bg-stone-100 px-2 py-1 rounded-full border border-stone-200",
                    ),
                    class_name="flex gap-2 mb-2",
                ),
                rx.el.p(event["description"], class_name="text-sm text-stone-700"),
                class_name="bg-white/80 p-5 rounded-2xl shadow-sm border border-[#d4b886] flex-1 hover:shadow-md hover:bg-white transition-all cursor-pointer",
                on_click=lambda: BibleState.select_event(event["id"]),
            ),
            class_name="flex items-center gap-6 w-full max-w-2xl mx-auto",
        ),
        class_name="relative py-4 group "
        + rx.cond(
            BibleState.selected_event_id == event["id"],
            "scale-[1.02] transition-transform",
            "",
        ),
    )


def render_era_section(group: EraGroup) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(group["emoji"], class_name="text-3xl mr-3"),
            rx.el.h2(group["era"], class_name="text-2xl font-bold font-serif"),
            class_name=f"flex items-center justify-center p-4 rounded-xl shadow-sm border-2 mb-8 mt-12 {group['color']}",
        ),
        rx.el.div(
            rx.el.div(
                class_name="absolute left-8 top-0 bottom-0 w-1 bg-[#d4b886] rounded-full"
            ),
            rx.foreach(group["events"], lambda evt, i: render_event_card(evt, i)),
            class_name="relative pl-0 md:pl-0 flex flex-col gap-4",
        ),
        class_name="max-w-4xl mx-auto w-full px-4",
    )


def timeline_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Cronología Bíblica",
                    class_name="text-3xl sm:text-4xl md:text-5xl font-bold font-serif text-[#4a3320] text-center mb-4",
                ),
                rx.el.p(
                    "Recorre la narrativa de las Escrituras desde la Creación hasta el Apocalipsis.",
                    class_name="text-lg text-[#8b5a2b] text-center italic mb-12 px-4",
                ),
                class_name="max-w-4xl mx-auto pt-12",
            ),
            rx.el.div(
                rx.foreach(BibleState.timeline_events_by_era, render_era_section),
                class_name="px-4",
            ),
            class_name="min-h-full pb-32 bg-[url('https://www.transparenttextures.com/patterns/aged-paper.png')] bg-opacity-50",
        ),
        class_name="w-full h-[calc(100vh-80px)] overflow-y-auto bg-[#faf6eb]",
    )