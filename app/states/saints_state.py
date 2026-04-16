import unicodedata

import reflex as rx

from app.data.saints import SAINT_CATEGORIES, SAINT_PERIODS, SAINTS, SaintRecord


def normalize_text(value: str) -> str:
    nfkd = unicodedata.normalize("NFKD", value)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def format_year(year: int) -> str:
    if year < 0:
        return f"{abs(year)} a.C."
    return f"{year} d.C."


class SaintsState(rx.State):
    saints: list[SaintRecord] = SAINTS
    periods: list[str] = SAINT_PERIODS
    categories: list[str] = SAINT_CATEGORIES
    selected_period: str = "Todos"
    selected_category: str = "Todos"
    search_query: str = ""
    selected_saint_id: str = "augustine"

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def clear_search_query(self):
        self.search_query = ""

    @rx.event
    def set_period(self, period: str):
        self.selected_period = period

    @rx.event
    def set_category(self, category: str):
        self.selected_category = category

    @rx.event
    def set_selected_saint(self, saint_id: str):
        self.selected_saint_id = saint_id

    @rx.var
    def selected_saint(self) -> SaintRecord:
        return next((s for s in self.saints if s["id"] == self.selected_saint_id), self.saints[0])

    @rx.var
    def selected_writings(self) -> list[str]:
        return list(self.selected_saint["writings"])

    @rx.var
    def selected_themes(self) -> list[str]:
        return list(self.selected_saint["themes"])

    @rx.var
    def selected_history_paragraphs(self) -> list[str]:
        saint = self.selected_saint
        writings = ", ".join(saint["writings"])
        themes = ", ".join(saint["themes"])
        related_names = [
            s["name"] for s in self.saints if s["id"] in set(saint["related"])
        ]
        related_text = ", ".join(related_names)
        paragraphs = [
            saint["biography"],
            (
                f"Cronologicamente, su vida se situa entre {format_year(saint['birth_year'])} "
                f"y {format_year(saint['death_year'])}. La referencia {saint['date_label']} "
                "permite ubicarlo dentro de la gran linea historica de la Iglesia, desde la "
                "edad apostolica y patristica hasta las reformas medievales, la evangelizacion "
                "moderna y los testigos contemporaneos."
            ),
            (
                f"Su vida pertenece al periodo {saint['period']} y se ubica principalmente en "
                f"{saint['location']}, dentro del ambito de {saint['region']}. Esta ubicacion "
                "ayuda a leer su santidad en una Iglesia concreta: con sus crisis, preguntas, "
                "necesidades pastorales, lenguajes culturales y formas propias de vivir la fe."
            ),
            (
                f"La tradicion lo recuerda bajo el titulo de {saint['honorific']} y lo clasifica "
                f"en esta antologia como {saint['category']}. Ese dato no es solo una etiqueta: "
                "senala el modo en que su testimonio fue recibido por la Iglesia, ya sea por su "
                "doctrina, martirio, fundacion, predicacion, vida monastica, servicio pastoral o "
                "influencia espiritual."
            ),
            (
                f"Entre los materiales asociados a su legado se encuentran: {writings}. Estos "
                "textos, testimonios o tradiciones permiten estudiar no solo los hechos externos "
                "de su vida, sino tambien su pensamiento, su forma de orar, su lectura de la "
                "Escritura y el impacto que dejo en generaciones posteriores."
            ),
            (
                f"Los grandes temas para leer su figura son: {themes}. A traves de esos temas se "
                "puede conectar su biografia con cuestiones mas amplias de la teologia catolica: "
                "la gracia, la Iglesia, los sacramentos, la mision, la caridad, la vida interior, "
                "la reforma y la fidelidad en tiempos dificiles."
            ),
            (
                f"Su memoria liturgica se celebra el {saint['feast_day']} y su patronazgo se asocia "
                f"con {saint['patronage']}. En la practica devocional, estos patronazgos resumen "
                "la manera en que el pueblo cristiano ha reconocido su cercania para necesidades "
                "concretas de la vida cotidiana."
            ),
        ]
        if related_text:
            paragraphs.append(
                f"Dentro de esta antologia se conecta especialmente con {related_text}. Estas conexiones "
                "sirven para estudiar cadenas de influencia: maestros y discipulos, familias espirituales, "
                "controversias doctrinales, reformas religiosas y tradiciones de oracion que atraviesan los siglos."
            )
        return paragraphs

    @rx.var
    def filtered_saints(self) -> list[SaintRecord]:
        query = normalize_text(self.search_query.strip())
        result = self.saints
        if self.selected_period != "Todos":
            result = [s for s in result if s["period"] == self.selected_period]
        if self.selected_category != "Todos":
            result = [s for s in result if s["category"] == self.selected_category]
        if query:
            result = [
                s
                for s in result
                if query
                in normalize_text(
                    " ".join(
                        [
                            s["name"],
                            s["honorific"],
                            s["category"],
                            s["period"],
                            s["region"],
                            s["summary"],
                            s["biography"],
                            " ".join(s["writings"]),
                            " ".join(s["themes"]),
                        ]
                    )
                )
            ]
        return sorted(result, key=lambda s: s["birth_year"])

    @rx.var
    def filtered_count(self) -> int:
        return len(self.filtered_saints)

    @rx.var
    def doctors_count(self) -> int:
        return len([s for s in self.saints if s["category"] == "Doctor de la Iglesia"])

    @rx.var
    def fathers_count(self) -> int:
        return len([s for s in self.saints if s["category"] == "Padre de la Iglesia"])

    @rx.var
    def writings_count(self) -> int:
        return sum(len(s["writings"]) for s in self.saints)

    @rx.var
    def selected_related_saints(self) -> list[SaintRecord]:
        saint = self.selected_saint
        related_ids = set(saint["related"])
        return [s for s in self.saints if s["id"] in related_ids]
