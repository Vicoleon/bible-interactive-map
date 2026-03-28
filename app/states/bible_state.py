import reflex as rx
import requests
import asyncio
import functools
from typing import TypedDict, Optional
import logging
import unicodedata
import re


def normalize_query(query: str) -> str:
    """Strip accents that cause API.Bible issues."""
    nfkd = unicodedata.normalize("NFKD", query)
    return "".join((c for c in nfkd if not unicodedata.combining(c)))


def strip_html(html: str) -> str:
    """Remove HTML tags and clean up text."""
    text = re.sub("<[^>]+>", "", html)
    text = re.sub("\\s+", " ", text).strip()
    return text


SCRIPTURE_REFS = {
    "Genesis 1-2": "GEN.1.1-GEN.2.25",
    "Genesis 3": "GEN.3.1-GEN.3.24",
    "Genesis 4": "GEN.4.1-GEN.4.16",
    "Genesis 5": "GEN.5.21-GEN.5.24",
    "Genesis 6-9": "GEN.6.9-GEN.6.22",
    "Genesis 11": "GEN.11.1-GEN.11.9",
    "Genesis 12": "GEN.12.1-GEN.12.9",
    "Genesis 15, 17": "GEN.15.1-GEN.15.6",
    "Genesis 19": "GEN.19.24-GEN.19.29",
    "Genesis 22": "GEN.22.1-GEN.22.14",
    "Genesis 28, 32": "GEN.28.10-GEN.28.17",
    "Genesis 37": "GEN.37.23-GEN.37.28",
    "Genesis 41-45": "GEN.41.38-GEN.41.45",
    "Exodus 2": "EXO.2.1-EXO.2.10",
    "Exodus 3": "EXO.3.1-EXO.3.6",
    "Exodus 7-12": "EXO.7.14-EXO.7.24",
    "Exodus 12": "EXO.12.1-EXO.12.14",
    "Exodus 14": "EXO.14.21-EXO.14.29",
    "Exodus 20": "EXO.20.1-EXO.20.17",
    "Exodus 32": "EXO.32.1-EXO.32.8",
    "Numbers 14": "NUM.14.26-NUM.14.35",
    "Joshua 3": "JOS.3.14-JOS.3.17",
    "Joshua 6": "JOS.6.15-JOS.6.21",
    "Joshua 10": "JOS.10.12-JOS.10.14",
    "Ruth 1-4": "RUT.1.16-RUT.1.18",
    "Judges 13-16": "JDG.16.28-JDG.16.30",
    "1 Samuel 3": "1SA.3.1-1SA.3.10",
    "1 Samuel 10": "1SA.10.1-1SA.10.1",
    "1 Samuel 17": "1SA.17.48-1SA.17.51",
    "2 Samuel 5": "2SA.5.1-2SA.5.5",
    "2 Samuel 11": "2SA.11.1-2SA.11.5",
    "1 Kings 6": "1KI.6.1-1KI.6.2",
    "1 Kings 3": "1KI.3.5-1KI.3.12",
    "1 Kings 12": "1KI.12.16-1KI.12.20",
    "1 Kings 18": "1KI.18.36-1KI.18.39",
    "2 Kings 2": "2KI.2.11-2KI.2.12",
    "Isaiah 6, 53": "ISA.53.1-ISA.53.6",
    "2 Kings 17": "2KI.17.5-2KI.17.7",
    "2 Kings 25": "2KI.25.8-2KI.25.12",
    "Daniel 6": "DAN.6.16-DAN.6.23",
    "Daniel 3": "DAN.3.19-DAN.3.27",
    "Daniel 7-12": "DAN.7.13-DAN.7.14",
    "Ezra 1": "EZR.1.1-EZR.1.4",
    "Ezra 3-6": "EZR.3.10-EZR.3.13",
    "Esther 4-7": "EST.4.13-EST.4.16",
    "Nehemiah 2-6": "NEH.2.17-NEH.2.18",
    "Luke 1": "LUK.1.26-LUK.1.38",
    "Luke 2": "LUK.2.1-LUK.2.14",
    "Matthew 2": "MAT.2.13-MAT.2.15",
    "Matthew 3": "MAT.3.13-MAT.3.17",
    "Matthew 4": "MAT.4.1-MAT.4.11",
    "Matthew 5-7": "MAT.5.1-MAT.5.12",
    "John 6": "JHN.6.9-JHN.6.14",
    "Matthew 17": "MAT.17.1-MAT.17.8",
    "John 11": "JHN.11.38-JHN.11.44",
    "Matthew 21": "MAT.21.6-MAT.21.11",
    "Matthew 26": "MAT.26.26-MAT.26.30",
    "Matthew 27": "MAT.27.32-MAT.27.54",
    "Matthew 28": "MAT.28.1-MAT.28.10",
    "Acts 1": "ACT.1.9-ACT.1.11",
    "Acts 2": "ACT.2.1-ACT.2.8",
    "Acts 7": "ACT.7.54-ACT.7.60",
    "Acts 9": "ACT.9.1-ACT.9.9",
    "Acts 13-20": "ACT.13.1-ACT.13.5",
    "Various": "2TI.4.6-2TI.4.8",
    "Revelation 1-22": "REV.1.1-REV.1.8",
    "History": "",
}


class Character(TypedDict):
    id: str
    name: str
    testament: str
    era: str
    description: str
    role: str
    emoji: str
    x: float
    y: float


class BibleBook(TypedDict):
    id: str
    name: str
    abbr: str
    testament: str
    category: str
    chapters: int
    emoji: str
    related_events: list[str]
    api_id: str


class Connection(TypedDict):
    source: str
    target: str
    type: str
    desc: str


class BibleEvent(TypedDict):
    id: str
    title: str
    era: str
    testament: str
    date_label: str
    description: str
    scripture_ref: str
    emoji: str
    characters_involved: list[str]
    connected_events: list[str]


class EraGroup(TypedDict):
    era: str
    color: str
    emoji: str
    events: list[BibleEvent]


class BibleState(rx.State):
    characters: list[Character] = [
        {
            "id": "c1",
            "name": "Adán",
            "testament": "OT",
            "era": "Creación",
            "description": "El primer hombre creado por Dios.",
            "role": "Patriarca",
            "emoji": "🧔",
            "x": 40,
            "y": 3,
        },
        {
            "id": "c2",
            "name": "Eva",
            "testament": "OT",
            "era": "Creación",
            "description": "La primera mujer, madre de todos los vivientes.",
            "role": "Matriarca",
            "emoji": "👩",
            "x": 55,
            "y": 3,
        },
        {
            "id": "c3",
            "name": "Noé",
            "testament": "OT",
            "era": "Pre-Diluvio",
            "description": "Constructor del arca, salvó a su familia del diluvio.",
            "role": "Patriarca",
            "emoji": "🚢",
            "x": 48,
            "y": 10,
        },
        {
            "id": "c4",
            "name": "Abraham",
            "testament": "OT",
            "era": "Patriarcal",
            "description": "Padre de muchas naciones, conocido por su fe.",
            "role": "Patriarca",
            "emoji": "⛺",
            "x": 40,
            "y": 17,
        },
        {
            "id": "c5",
            "name": "Sara",
            "testament": "OT",
            "era": "Patriarcal",
            "description": "Esposa de Abraham, madre de Isaac en su vejez.",
            "role": "Matriarca",
            "emoji": "👵",
            "x": 55,
            "y": 17,
        },
        {
            "id": "c6",
            "name": "Isaac",
            "testament": "OT",
            "era": "Patriarcal",
            "description": "Hijo de Abraham y Sara, hijo de la promesa.",
            "role": "Patriarca",
            "emoji": "👦",
            "x": 40,
            "y": 23,
        },
        {
            "id": "c21",
            "name": "Rebeca",
            "testament": "OT",
            "era": "Patriarcal",
            "description": "Esposa de Isaac, madre de Jacob y Esaú.",
            "role": "Matriarca",
            "emoji": "👰",
            "x": 55,
            "y": 23,
        },
        {
            "id": "c7",
            "name": "Jacob",
            "testament": "OT",
            "era": "Patriarcal",
            "description": "Hijo de Isaac, padre de las 12 tribus de Israel.",
            "role": "Patriarca",
            "emoji": "🏕️",
            "x": 40,
            "y": 29,
        },
        {
            "id": "c22",
            "name": "Raquel",
            "testament": "OT",
            "era": "Patriarcal",
            "description": "Esposa amada de Jacob, madre de José y Benjamín.",
            "role": "Matriarca",
            "emoji": "💕",
            "x": 55,
            "y": 29,
        },
        {
            "id": "c23",
            "name": "Lea",
            "testament": "OT",
            "era": "Patriarcal",
            "description": "Primera esposa de Jacob, madre de seis tribus de Israel.",
            "role": "Matriarca",
            "emoji": "👩",
            "x": 28,
            "y": 29,
        },
        {
            "id": "c8",
            "name": "José",
            "testament": "OT",
            "era": "Patriarcal",
            "description": "Vendido como esclavo, llegó a ser gobernante en Egipto.",
            "role": "Líder",
            "emoji": "🌾",
            "x": 48,
            "y": 35,
        },
        {
            "id": "c9",
            "name": "Moisés",
            "testament": "OT",
            "era": "Éxodo",
            "description": "Sacó a los israelitas de Egipto, recibió la Ley.",
            "role": "Profeta",
            "emoji": "🌊",
            "x": 40,
            "y": 42,
        },
        {
            "id": "c10",
            "name": "Aarón",
            "testament": "OT",
            "era": "Éxodo",
            "description": "Hermano de Moisés, primer Sumo Sacerdote.",
            "role": "Sacerdote",
            "emoji": "⚖️",
            "x": 55,
            "y": 42,
        },
        {
            "id": "c11",
            "name": "Josué",
            "testament": "OT",
            "era": "Conquista",
            "description": "Sucesor de Moisés, lideró a Israel a la Tierra Prometida.",
            "role": "Líder",
            "emoji": "🎺",
            "x": 40,
            "y": 49,
        },
        {
            "id": "c24",
            "name": "Débora",
            "testament": "OT",
            "era": "Jueces",
            "description": "Profetisa y jueza que lideró a Israel a la victoria.",
            "role": "Figura",
            "emoji": "⚔️",
            "x": 30,
            "y": 54,
        },
        {
            "id": "c31",
            "name": "Gedeón",
            "testament": "OT",
            "era": "Jueces",
            "description": "Juez que derrotó a los madianitas con solo 300 hombres.",
            "role": "Líder",
            "emoji": "🕯️",
            "x": 48,
            "y": 54,
        },
        {
            "id": "c25",
            "name": "Sansón",
            "testament": "OT",
            "era": "Jueces",
            "description": "Nazareo dotado de fuerza sobrenatural por Dios.",
            "role": "Figura",
            "emoji": "💪",
            "x": 65,
            "y": 54,
        },
        {
            "id": "c12",
            "name": "Rut",
            "testament": "OT",
            "era": "Jueces",
            "description": "Viuda moabita que mostró gran lealtad a su suegra.",
            "role": "Figura",
            "emoji": "🌾",
            "x": 48,
            "y": 60,
        },
        {
            "id": "c13",
            "name": "Samuel",
            "testament": "OT",
            "era": "Reino Unido",
            "description": "Último de los jueces, ungió a los primeros reyes.",
            "role": "Profeta",
            "emoji": "🛢️",
            "x": 48,
            "y": 66,
        },
        {
            "id": "c14",
            "name": "Saúl",
            "testament": "OT",
            "era": "Reino Unido",
            "description": "Primer rey de Israel, cuyo reinado terminó trágicamente.",
            "role": "Rey",
            "emoji": "👑",
            "x": 35,
            "y": 71,
        },
        {
            "id": "c15",
            "name": "David",
            "testament": "OT",
            "era": "Reino Unido",
            "description": "Segundo rey de Israel, hombre conforme al corazón de Dios.",
            "role": "Rey",
            "emoji": "🎶",
            "x": 50,
            "y": 71,
        },
        {
            "id": "c16",
            "name": "Salomón",
            "testament": "OT",
            "era": "Reino Unido",
            "description": "Hijo de David, construyó el primer templo, conocido por su sabiduría.",
            "role": "Rey",
            "emoji": "🏛️",
            "x": 50,
            "y": 78,
        },
        {
            "id": "c17",
            "name": "Elías",
            "testament": "OT",
            "era": "Reino Dividido",
            "description": "Gran profeta que desafió a los profetas de Baal.",
            "role": "Profeta",
            "emoji": "🔥",
            "x": 25,
            "y": 83,
        },
        {
            "id": "c26",
            "name": "Eliseo",
            "testament": "OT",
            "era": "Reino Dividido",
            "description": "Sucesor de Elías, realizó muchos milagros.",
            "role": "Profeta",
            "emoji": "🌿",
            "x": 35,
            "y": 83,
        },
        {
            "id": "c18",
            "name": "Isaías",
            "testament": "OT",
            "era": "Reino Dividido",
            "description": "Profeta mayor que profetizó la venida del Mesías.",
            "role": "Profeta",
            "emoji": "📜",
            "x": 55,
            "y": 83,
        },
        {
            "id": "c30",
            "name": "Jonás",
            "testament": "OT",
            "era": "Reino Dividido",
            "description": "Profeta que huyó de Dios y fue tragado por un gran pez.",
            "role": "Profeta",
            "emoji": "🐋",
            "x": 70,
            "y": 83,
        },
        {
            "id": "c27",
            "name": "Jeremías",
            "testament": "OT",
            "era": "Exilio",
            "description": "El profeta llorón, advirtió sobre la caída de Jerusalén.",
            "role": "Profeta",
            "emoji": "😢",
            "x": 30,
            "y": 90,
        },
        {
            "id": "c19",
            "name": "Daniel",
            "testament": "OT",
            "era": "Exilio",
            "description": "Prophet who remained faithful in Babylon.",
            "role": "Profeta",
            "emoji": "🦁",
            "x": 50,
            "y": 90,
        },
        {
            "id": "c28",
            "name": "Ezequiel",
            "testament": "OT",
            "era": "Exilio",
            "description": "Profeta del exilio, tuvo visiones del templo restaurado.",
            "role": "Profeta",
            "emoji": "🌀",
            "x": 70,
            "y": 90,
        },
        {
            "id": "c20",
            "name": "Ester",
            "testament": "OT",
            "era": "Post-Exilio",
            "description": "Reina judía de Persia que salvó a su pueblo.",
            "role": "Reina",
            "emoji": "👑",
            "x": 38,
            "y": 96,
        },
        {
            "id": "c29",
            "name": "Nehemías",
            "testament": "OT",
            "era": "Post-Exilio",
            "description": "Copero del rey persa que reconstruyó los muros de Jerusalén.",
            "role": "Líder",
            "emoji": "🧱",
            "x": 58,
            "y": 96,
        },
        {
            "id": "n1",
            "name": "María",
            "testament": "NT",
            "era": "Evangelios",
            "description": "Madre de Jesús.",
            "role": "Figura",
            "emoji": "👩\u200d🍼",
            "x": 40,
            "y": 7,
        },
        {
            "id": "n2",
            "name": "José",
            "testament": "NT",
            "era": "Evangelios",
            "description": "Padre terrenal de Jesús, carpintero.",
            "role": "Figura",
            "emoji": "🪚",
            "x": 55,
            "y": 7,
        },
        {
            "id": "n3",
            "name": "Juan el Bautista",
            "testament": "NT",
            "era": "Evangelios",
            "description": "Precursor de Cristo, bautizó a Jesús.",
            "role": "Profeta",
            "emoji": "💧",
            "x": 70,
            "y": 12,
        },
        {
            "id": "n4",
            "name": "Jesús",
            "testament": "NT",
            "era": "Evangelios",
            "description": "El Mesías, Hijo de Dios, Salvador del mundo.",
            "role": "Mesías",
            "emoji": "✝️",
            "x": 48,
            "y": 20,
        },
        {
            "id": "n5",
            "name": "Pedro",
            "testament": "NT",
            "era": "Iglesia Primitiva",
            "description": "Pescador convertido en apóstol, líder de la iglesia primitiva.",
            "role": "Apóstol",
            "emoji": "🗝️",
            "x": 25,
            "y": 30,
        },
        {
            "id": "n6",
            "name": "Juan",
            "testament": "NT",
            "era": "Iglesia Primitiva",
            "description": "El discípulo amado, autor de un Evangelio y el Apocalipsis.",
            "role": "Apóstol",
            "emoji": "🦅",
            "x": 48,
            "y": 30,
        },
        {
            "id": "n7",
            "name": "Santiago",
            "testament": "NT",
            "era": "Iglesia Primitiva",
            "description": "Hermano de Juan, primer apóstol en ser martirizado.",
            "role": "Apóstol",
            "emoji": "⚔️",
            "x": 70,
            "y": 30,
        },
        {
            "id": "n13",
            "name": "Andrés",
            "testament": "NT",
            "era": "Evangelios",
            "description": "Hermano de Pedro, uno de los primeros discípulos llamados.",
            "role": "Apóstol",
            "emoji": "🐟",
            "x": 15,
            "y": 36,
        },
        {
            "id": "n14",
            "name": "Mateo",
            "testament": "NT",
            "era": "Evangelios",
            "description": "Recaudador de impuestos convertido en apóstol y evangelista.",
            "role": "Apóstol",
            "emoji": "📝",
            "x": 30,
            "y": 42,
        },
        {
            "id": "n15",
            "name": "Tomás",
            "testament": "NT",
            "era": "Evangelios",
            "description": "Apóstol que dudó de la resurrección hasta ver a Jesús.",
            "role": "Apóstol",
            "emoji": "🤚",
            "x": 65,
            "y": 42,
        },
        {
            "id": "n11",
            "name": "María Magdalena",
            "testament": "NT",
            "era": "Evangelios",
            "description": "Seguidora de Jesús, primera en ver al Cristo resucitado.",
            "role": "Discípulo",
            "emoji": "🏺",
            "x": 48,
            "y": 48,
        },
        {
            "id": "n17",
            "name": "Lázaro",
            "testament": "NT",
            "era": "Evangelios",
            "description": "Amigo de Jesús, resucitado de entre los muertos.",
            "role": "Figura",
            "emoji": "⚰️",
            "x": 72,
            "y": 48,
        },
        {
            "id": "n18",
            "name": "Marta",
            "testament": "NT",
            "era": "Evangelios",
            "description": "Hermana de Lázaro, conocida por su servicio fiel.",
            "role": "Figura",
            "emoji": "🏠",
            "x": 82,
            "y": 42,
        },
        {
            "id": "n8",
            "name": "Pablo",
            "testament": "NT",
            "era": "Iglesia Primitiva",
            "description": "Apóstol de los gentiles, escribió muchas epístolas.",
            "role": "Apóstol",
            "emoji": "✉️",
            "x": 48,
            "y": 70,
        },
        {
            "id": "n9",
            "name": "Lucas",
            "testament": "NT",
            "era": "Iglesia Primitiva",
            "description": "Médico, autor de un Evangelio y Hechos.",
            "role": "Evangelista",
            "emoji": "🩺",
            "x": 30,
            "y": 76,
        },
        {
            "id": "n10",
            "name": "Timoteo",
            "testament": "NT",
            "era": "Iglesia Primitiva",
            "description": "Joven pastor guiado por Pablo.",
            "role": "Líder",
            "emoji": "📖",
            "x": 48,
            "y": 84,
        },
        {
            "id": "n16",
            "name": "Bernabé",
            "testament": "NT",
            "era": "Iglesia Primitiva",
            "description": "Compañero de Pablo en su primer viaje misionero.",
            "role": "Líder",
            "emoji": "🤝",
            "x": 65,
            "y": 76,
        },
        {
            "id": "n12",
            "name": "Esteban",
            "testament": "NT",
            "era": "Iglesia Primitiva",
            "description": "Primer mártir cristiano.",
            "role": "Diácono",
            "emoji": "🪨",
            "x": 48,
            "y": 60,
        },
    ]
    connections: list[Connection] = [
        {"source": "c1", "target": "c2", "type": "familia", "desc": "Esposo y Esposa"},
        {"source": "c1", "target": "c3", "type": "linaje", "desc": "Ancestro"},
        {"source": "c3", "target": "c4", "type": "linaje", "desc": "Línea genealógica"},
        {"source": "c4", "target": "c5", "type": "familia", "desc": "Esposo y Esposa"},
        {"source": "c4", "target": "c6", "type": "familia", "desc": "Padre e Hijo"},
        {"source": "c6", "target": "c21", "type": "familia", "desc": "Esposo y Esposa"},
        {"source": "c21", "target": "c7", "type": "familia", "desc": "Madre e Hijo"},
        {"source": "c6", "target": "c7", "type": "familia", "desc": "Padre e Hijo"},
        {"source": "c7", "target": "c22", "type": "familia", "desc": "Esposo y Esposa"},
        {"source": "c7", "target": "c23", "type": "familia", "desc": "Esposo y Esposa"},
        {"source": "c7", "target": "c8", "type": "familia", "desc": "Padre e Hijo"},
        {"source": "c22", "target": "c8", "type": "familia", "desc": "Madre e Hijo"},
        {
            "source": "c8",
            "target": "c9",
            "type": "linaje",
            "desc": "Los israelitas en Egipto",
        },
        {"source": "c9", "target": "c10", "type": "familia", "desc": "Hermanos"},
        {
            "source": "c9",
            "target": "c11",
            "type": "mentor",
            "desc": "Mentor al Sucesor",
        },
        {
            "source": "c24",
            "target": "c31",
            "type": "aliado",
            "desc": "Jueces de Israel",
        },
        {
            "source": "c25",
            "target": "c13",
            "type": "aliado",
            "desc": "Época de los Jueces",
        },
        {"source": "c12", "target": "c15", "type": "linaje", "desc": "Bisabuela"},
        {"source": "c13", "target": "c14", "type": "mentor", "desc": "Ungió al Rey"},
        {"source": "c13", "target": "c15", "type": "mentor", "desc": "Ungió al Rey"},
        {
            "source": "c14",
            "target": "c15",
            "type": "aliado",
            "desc": "Rey y su sucesor",
        },
        {"source": "c15", "target": "c16", "type": "familia", "desc": "Padre e Hijo"},
        {
            "source": "c17",
            "target": "c26",
            "type": "mentor",
            "desc": "Mentor y sucesor",
        },
        {
            "source": "c17",
            "target": "c9",
            "type": "aliado",
            "desc": "Aparecieron juntos en la Transfiguración",
        },
        {
            "source": "c27",
            "target": "c18",
            "type": "aliado",
            "desc": "Profetas de Judá",
        },
        {
            "source": "c30",
            "target": "c17",
            "type": "aliado",
            "desc": "Profetas del Reino del Norte",
        },
        {
            "source": "c19",
            "target": "c27",
            "type": "aliado",
            "desc": "Contemporáneos en el exilio",
        },
        {
            "source": "c19",
            "target": "c28",
            "type": "aliado",
            "desc": "Profetas del exilio en Babilonia",
        },
        {
            "source": "c20",
            "target": "c29",
            "type": "aliado",
            "desc": "Figuras del período persa",
        },
        {
            "source": "n1",
            "target": "n2",
            "type": "familia",
            "desc": "Prometidos/Esposos",
        },
        {"source": "n1", "target": "n4", "type": "familia", "desc": "Madre e Hijo"},
        {
            "source": "n3",
            "target": "n4",
            "type": "familia",
            "desc": "Primos / Precursor",
        },
        {
            "source": "n4",
            "target": "n5",
            "type": "mentor",
            "desc": "Maestro y Discípulo",
        },
        {
            "source": "n4",
            "target": "n6",
            "type": "mentor",
            "desc": "Maestro y Discípulo",
        },
        {
            "source": "n4",
            "target": "n7",
            "type": "mentor",
            "desc": "Maestro y Discípulo",
        },
        {
            "source": "n4",
            "target": "n13",
            "type": "mentor",
            "desc": "Maestro y Discípulo",
        },
        {
            "source": "n4",
            "target": "n14",
            "type": "mentor",
            "desc": "Maestro y Discípulo",
        },
        {
            "source": "n4",
            "target": "n15",
            "type": "mentor",
            "desc": "Maestro y Discípulo",
        },
        {
            "source": "n4",
            "target": "n11",
            "type": "mentor",
            "desc": "Maestro y Seguidora",
        },
        {"source": "n4", "target": "n17", "type": "aliado", "desc": "Amigo cercano"},
        {"source": "n6", "target": "n7", "type": "familia", "desc": "Hermanos"},
        {"source": "n5", "target": "n13", "type": "familia", "desc": "Hermanos"},
        {"source": "n17", "target": "n18", "type": "familia", "desc": "Hermanos"},
        {
            "source": "n8",
            "target": "n9",
            "type": "aliado",
            "desc": "Compañeros en el ministerio",
        },
        {
            "source": "n8",
            "target": "n10",
            "type": "mentor",
            "desc": "Padre e Hijo espiritual",
        },
        {
            "source": "n8",
            "target": "n16",
            "type": "aliado",
            "desc": "Compañeros misioneros",
        },
        {"source": "n14", "target": "n9", "type": "aliado", "desc": "Evangelistas"},
        {
            "source": "n16",
            "target": "n12",
            "type": "aliado",
            "desc": "Líderes de la iglesia en Jerusalén",
        },
        {
            "source": "n12",
            "target": "n8",
            "type": "aliado",
            "desc": "Pablo presenció su martirio",
        },
        {
            "source": "n12",
            "target": "n5",
            "type": "aliado",
            "desc": "Ambos líderes de la iglesia primitiva",
        },
        {
            "source": "c18",
            "target": "n4",
            "type": "profecía",
            "desc": "Profetizó al Siervo Sufriente",
        },
        {
            "source": "c15",
            "target": "n4",
            "type": "profecía",
            "desc": "Prometió trono eterno",
        },
        {
            "source": "c15",
            "target": "n4",
            "type": "linaje",
            "desc": "Linaje del Mesías",
        },
        {
            "source": "c9",
            "target": "n4",
            "type": "profecía",
            "desc": "Profetizó un Profeta como él",
        },
        {
            "source": "c4",
            "target": "n4",
            "type": "profecía",
            "desc": "Prometida bendición a todas las naciones",
        },
        {
            "source": "c19",
            "target": "n4",
            "type": "profecía",
            "desc": "Profetizó al Hijo del Hombre",
        },
        {
            "source": "c30",
            "target": "n4",
            "type": "profecía",
            "desc": "Señal de Jonás prefiguró la resurrección",
        },
        {
            "source": "c12",
            "target": "n4",
            "type": "linaje",
            "desc": "En el linaje del Mesías",
        },
        {"source": "n18", "target": "n4", "type": "aliado", "desc": "Seguidora fiel"},
    ]
    bible_books: list[BibleBook] = [
        {
            "id": "b1",
            "name": "Génesis",
            "abbr": "Gen",
            "testament": "OT",
            "category": "Pentateuco",
            "chapters": 50,
            "emoji": "🌍",
            "api_id": "GEN",
            "related_events": [
                "e1",
                "e2",
                "e3",
                "e4",
                "e5",
                "e6",
                "e7",
                "e8",
                "e9",
                "e10",
                "e11",
                "e12",
                "e13",
            ],
        },
        {
            "id": "b2",
            "name": "Éxodo",
            "abbr": "Exo",
            "testament": "OT",
            "category": "Pentateuco",
            "chapters": 40,
            "emoji": "🌊",
            "api_id": "EXO",
            "related_events": ["e14", "e15", "e16", "e17", "e18", "e19", "e20"],
        },
        {
            "id": "b3",
            "name": "Levítico",
            "abbr": "Lev",
            "testament": "OT",
            "category": "Pentateuco",
            "chapters": 27,
            "emoji": "⚖️",
            "api_id": "LEV",
            "related_events": [],
        },
        {
            "id": "b4",
            "name": "Números",
            "abbr": "Num",
            "testament": "OT",
            "category": "Pentateuco",
            "chapters": 36,
            "emoji": "🏕️",
            "api_id": "NUM",
            "related_events": ["e21"],
        },
        {
            "id": "b5",
            "name": "Deuteronomio",
            "abbr": "Deu",
            "testament": "OT",
            "category": "Pentateuco",
            "chapters": 34,
            "emoji": "📜",
            "api_id": "DEU",
            "related_events": [],
        },
        {
            "id": "b6",
            "name": "Josué",
            "abbr": "Jos",
            "testament": "OT",
            "category": "Históricos",
            "chapters": 24,
            "emoji": "🎺",
            "api_id": "JOS",
            "related_events": ["e22", "e23", "e24"],
        },
        {
            "id": "b7",
            "name": "Jueces",
            "abbr": "Jdg",
            "testament": "OT",
            "category": "Históricos",
            "chapters": 21,
            "emoji": "⚔️",
            "api_id": "JDG",
            "related_events": ["e26"],
        },
        {
            "id": "b8",
            "name": "Rut",
            "abbr": "Rut",
            "testament": "OT",
            "category": "Históricos",
            "chapters": 4,
            "emoji": "🌾",
            "api_id": "RUT",
            "related_events": ["e25"],
        },
        {
            "id": "b9",
            "name": "1 Samuel",
            "abbr": "1Sa",
            "testament": "OT",
            "category": "Históricos",
            "chapters": 31,
            "emoji": "👑",
            "api_id": "1SA",
            "related_events": ["e27", "e28", "e29"],
        },
        {
            "id": "b10",
            "name": "2 Samuel",
            "abbr": "2Sa",
            "testament": "OT",
            "category": "Históricos",
            "chapters": 24,
            "emoji": "👑",
            "api_id": "2SA",
            "related_events": ["e30", "e31"],
        },
        {
            "id": "b11",
            "name": "1 Reyes",
            "abbr": "1Ki",
            "testament": "OT",
            "category": "Históricos",
            "chapters": 22,
            "emoji": "🏛️",
            "api_id": "1KI",
            "related_events": ["e32", "e33", "e34", "e35"],
        },
        {
            "id": "b12",
            "name": "2 Reyes",
            "abbr": "2Ki",
            "testament": "OT",
            "category": "Históricos",
            "chapters": 25,
            "emoji": "📜",
            "api_id": "2KI",
            "related_events": ["e36", "e38", "e39"],
        },
        {
            "id": "b15",
            "name": "Esdras",
            "abbr": "Ezr",
            "testament": "OT",
            "category": "Históricos",
            "chapters": 10,
            "emoji": "🏗️",
            "api_id": "EZR",
            "related_events": ["e43", "e44"],
        },
        {
            "id": "b16",
            "name": "Nehemías",
            "abbr": "Neh",
            "testament": "OT",
            "category": "Históricos",
            "chapters": 13,
            "emoji": "🧱",
            "api_id": "NEH",
            "related_events": ["e46"],
        },
        {
            "id": "b17",
            "name": "Ester",
            "abbr": "Est",
            "testament": "OT",
            "category": "Históricos",
            "chapters": 10,
            "emoji": "👸",
            "api_id": "EST",
            "related_events": ["e45"],
        },
        {
            "id": "b18",
            "name": "Isaías",
            "abbr": "Isa",
            "testament": "OT",
            "category": "Profetas Mayores",
            "chapters": 66,
            "emoji": "👁️",
            "api_id": "ISA",
            "related_events": ["e37"],
        },
        {
            "id": "b19",
            "name": "Daniel",
            "abbr": "Dan",
            "testament": "OT",
            "category": "Profetas Mayores",
            "chapters": 12,
            "emoji": "🦁",
            "api_id": "DAN",
            "related_events": ["e40", "e41", "e42"],
        },
        {
            "id": "b40",
            "name": "Mateo",
            "abbr": "Mat",
            "testament": "NT",
            "category": "Evangelios",
            "chapters": 28,
            "emoji": "✨",
            "api_id": "MAT",
            "related_events": [
                "e50",
                "e52",
                "e53",
                "e54",
                "e55",
                "e57",
                "e59",
                "e60",
                "e61",
                "e62",
                "e63",
                "e64",
            ],
        },
        {
            "id": "b41",
            "name": "Marcos",
            "abbr": "Mrk",
            "testament": "NT",
            "category": "Evangelios",
            "chapters": 16,
            "emoji": "🦁",
            "api_id": "MRK",
            "related_events": [],
        },
        {
            "id": "b42",
            "name": "Lucas",
            "abbr": "Luk",
            "testament": "NT",
            "category": "Evangelios",
            "chapters": 24,
            "emoji": "🐂",
            "api_id": "LUK",
            "related_events": ["e48", "e49", "e51"],
        },
        {
            "id": "b43",
            "name": "Juan",
            "abbr": "Jhn",
            "testament": "NT",
            "category": "Evangelios",
            "chapters": 21,
            "emoji": "🦅",
            "api_id": "JHN",
            "related_events": ["e56", "e58"],
        },
        {
            "id": "b44",
            "name": "Hechos",
            "abbr": "Act",
            "testament": "NT",
            "category": "Hechos",
            "chapters": 28,
            "emoji": "🕊️",
            "api_id": "ACT",
            "related_events": ["e65", "e66", "e67", "e68", "e69"],
        },
        {
            "id": "b66",
            "name": "Apocalipsis",
            "abbr": "Rev",
            "testament": "NT",
            "category": "Profético",
            "chapters": 22,
            "emoji": "👁️",
            "api_id": "REV",
            "related_events": ["e72"],
        },
    ]
    events: list[BibleEvent] = [
        {
            "id": "e1",
            "title": "Creación del Mundo",
            "era": "Creación",
            "testament": "OT",
            "date_label": "~4000 a.C.",
            "description": "Dios crea los cielos y la tierra, culminando con la creación de la humanidad.",
            "scripture_ref": "Genesis 1-2",
            "emoji": "🌍",
            "characters_involved": ["c1", "c2"],
            "connected_events": ["e2"],
        },
        {
            "id": "e2",
            "title": "La Caída del Hombre",
            "era": "Creación",
            "testament": "OT",
            "date_label": "~4000 a.C.",
            "description": "Adán y Eva desobedecen a Dios al comer del fruto prohibido, introduciendo el pecado en el mundo.",
            "scripture_ref": "Genesis 3",
            "emoji": "🍎",
            "characters_involved": ["c1", "c2"],
            "connected_events": ["e3"],
        },
        {
            "id": "e3",
            "title": "Caín y Abel",
            "era": "Creación",
            "testament": "OT",
            "date_label": "~3900 a.C.",
            "description": "Caín asesina a su hermano Abel por celos.",
            "scripture_ref": "Genesis 4",
            "emoji": "🗡️",
            "characters_involved": ["c1", "c2"],
            "connected_events": [],
        },
        {
            "id": "e4",
            "title": "Enoc Camina con Dios",
            "era": "Creación",
            "testament": "OT",
            "date_label": "~3300 a.C.",
            "description": "Enoc vive una vida justa y es llevado por Dios sin experimentar la muerte.",
            "scripture_ref": "Genesis 5",
            "emoji": "🚶",
            "characters_involved": [],
            "connected_events": [],
        },
        {
            "id": "e5",
            "title": "El Gran Diluvio",
            "era": "Pre-Diluvio",
            "testament": "OT",
            "date_label": "~2400 a.C.",
            "description": "Dios envía un diluvio para limpiar la tierra, salvando solo a Noé y su familia en el arca.",
            "scripture_ref": "Genesis 6-9",
            "emoji": "🌊",
            "characters_involved": ["c3"],
            "connected_events": [],
        },
        {
            "id": "e6",
            "title": "Torre de Babel",
            "era": "Pre-Diluvio",
            "testament": "OT",
            "date_label": "~2200 a.C.",
            "description": "La humanidad intenta construir una torre hasta los cielos, resultando en la confusión de las lenguas.",
            "scripture_ref": "Genesis 11",
            "emoji": "🗼",
            "characters_involved": [],
            "connected_events": [],
        },
        {
            "id": "e7",
            "title": "Llamado de Abraham",
            "era": "Patriarcal",
            "testament": "OT",
            "date_label": "~2000 a.C.",
            "description": "Dios llama a Abraham a dejar su tierra natal y promete convertirlo en una gran nación.",
            "scripture_ref": "Genesis 12",
            "emoji": "⛺",
            "characters_involved": ["c4"],
            "connected_events": ["e8"],
        },
        {
            "id": "e8",
            "title": "Pacto con Abraham",
            "era": "Patriarcal",
            "testament": "OT",
            "date_label": "~1900 a.C.",
            "description": "Dios establece un pacto formal con Abraham y Sara.",
            "scripture_ref": "Genesis 15, 17",
            "emoji": "🤝",
            "characters_involved": ["c4", "c5"],
            "connected_events": [],
        },
        {
            "id": "e9",
            "title": "Destrucción de Sodoma",
            "era": "Patriarcal",
            "testament": "OT",
            "date_label": "~1900 a.C.",
            "description": "Dios destruye las malvadas ciudades de Sodoma y Gomorra.",
            "scripture_ref": "Genesis 19",
            "emoji": "🔥",
            "characters_involved": ["c4"],
            "connected_events": [],
        },
        {
            "id": "e10",
            "title": "Sacrificio de Isaac",
            "era": "Patriarcal",
            "testament": "OT",
            "date_label": "~1850 a.C.",
            "description": "Abraham es probado para sacrificar a su hijo Isaac, pero Dios provee un carnero.",
            "scripture_ref": "Genesis 22",
            "emoji": "🐏",
            "characters_involved": ["c4", "c6"],
            "connected_events": [],
        },
        {
            "id": "e11",
            "title": "La Escalera de Jacob",
            "era": "Patriarcal",
            "testament": "OT",
            "date_label": "~1800 a.C.",
            "description": "Jacob sueña con una escalera al cielo y más tarde lucha con Dios.",
            "scripture_ref": "Genesis 28, 32",
            "emoji": "🪜",
            "characters_involved": ["c7"],
            "connected_events": [],
        },
        {
            "id": "e12",
            "title": "José Vendido como Esclavo",
            "era": "Patriarcal",
            "testament": "OT",
            "date_label": "~1750 a.C.",
            "description": "José es traicionado por sus hermanos y vendido como esclavo en Egipto.",
            "scripture_ref": "Genesis 37",
            "emoji": "⛓️",
            "characters_involved": ["c7", "c8"],
            "connected_events": ["e13"],
        },
        {
            "id": "e13",
            "title": "José Gobierna Egipto",
            "era": "Patriarcal",
            "testament": "OT",
            "date_label": "~1700 a.C.",
            "description": "José asciende al poder en Egipto y salva a su familia del hambre.",
            "scripture_ref": "Genesis 41-45",
            "emoji": "🌾",
            "characters_involved": ["c8"],
            "connected_events": [],
        },
        {
            "id": "e14",
            "title": "Nacimiento de Moisés",
            "era": "Éxodo",
            "testament": "OT",
            "date_label": "~1526 a.C.",
            "description": "Moisés nace y es escondido en una canasta en el Nilo para escapar del decreto de Faraón.",
            "scripture_ref": "Exodus 2",
            "emoji": "🧺",
            "characters_involved": ["c9"],
            "connected_events": [],
        },
        {
            "id": "e15",
            "title": "La Zarza Ardiente",
            "era": "Éxodo",
            "testament": "OT",
            "date_label": "~1446 a.C.",
            "description": "Dios habla a Moisés desde una zarza ardiente, llamándolo a liberar a Israel.",
            "scripture_ref": "Exodus 3",
            "emoji": "🔥",
            "characters_involved": ["c9"],
            "connected_events": ["e16"],
        },
        {
            "id": "e16",
            "title": "Las Diez Plagas de Egipto",
            "era": "Éxodo",
            "testament": "OT",
            "date_label": "~1446 a.C.",
            "description": "Dios envía diez plagas sobre Egipto para obligar al Faraón a liberar a los israelitas.",
            "scripture_ref": "Exodus 7-12",
            "emoji": "🐸",
            "characters_involved": ["c9", "c10"],
            "connected_events": ["e17"],
        },
        {
            "id": "e17",
            "title": "La Pascua",
            "era": "Éxodo",
            "testament": "OT",
            "date_label": "~1446 a.C.",
            "description": "Los israelitas marcan sus puertas con la sangre del cordero para ser librados de la última plaga.",
            "scripture_ref": "Exodus 12",
            "emoji": "🚪",
            "characters_involved": ["c9"],
            "connected_events": ["e60"],
        },
        {
            "id": "e18",
            "title": "Cruce del Mar Rojo",
            "era": "Éxodo",
            "testament": "OT",
            "date_label": "~1446 a.C.",
            "description": "Moisés divide el Mar Rojo, permitiendo que Israel escape del ejército egipcio.",
            "scripture_ref": "Exodus 14",
            "emoji": "🌊",
            "characters_involved": ["c9"],
            "connected_events": [],
        },
        {
            "id": "e19",
            "title": "Los Diez Mandamientos",
            "era": "Éxodo",
            "testament": "OT",
            "date_label": "~1445 a.C.",
            "description": "Dios da a Moisés la ley en el Monte Sinaí.",
            "scripture_ref": "Exodus 20",
            "emoji": "📜",
            "characters_involved": ["c9"],
            "connected_events": [],
        },
        {
            "id": "e20",
            "title": "El Becerro de Oro",
            "era": "Éxodo",
            "testament": "OT",
            "date_label": "~1445 a.C.",
            "description": "Los israelitas construyen y adoran un becerro de oro mientras Moisés está en el Sinaí.",
            "scripture_ref": "Exodus 32",
            "emoji": "🐂",
            "characters_involved": ["c9", "c10"],
            "connected_events": [],
        },
        {
            "id": "e21",
            "title": "40 Años en el Desierto",
            "era": "Éxodo",
            "testament": "OT",
            "date_label": "~1445-1405 a.C.",
            "description": "Los israelitas vagan por el desierto durante cuarenta años debido a su incredulidad.",
            "scripture_ref": "Numbers 14",
            "emoji": "🏜️",
            "characters_involved": ["c9"],
            "connected_events": [],
        },
        {
            "id": "e22",
            "title": "Cruce del Jordán",
            "era": "Conquista",
            "testament": "OT",
            "date_label": "~1405 a.C.",
            "description": "Josué lidera a los israelitas a través del río Jordán hacia la Tierra Prometida.",
            "scripture_ref": "Joshua 3",
            "emoji": "🏞️",
            "characters_involved": ["c11"],
            "connected_events": ["e23"],
        },
        {
            "id": "e23",
            "title": "Caída de Jericó",
            "era": "Conquista",
            "testament": "OT",
            "date_label": "~1405 a.C.",
            "description": "Los muros de Jericó caen después de que los israelitas marchan alrededor de la ciudad.",
            "scripture_ref": "Joshua 6",
            "emoji": "🧱",
            "characters_involved": ["c11"],
            "connected_events": [],
        },
        {
            "id": "e24",
            "title": "El Sol se Detiene",
            "era": "Conquista",
            "testament": "OT",
            "date_label": "~1400 a.C.",
            "description": "Josué ordena que el sol se detenga durante una batalla.",
            "scripture_ref": "Joshua 10",
            "emoji": "☀️",
            "characters_involved": ["c11"],
            "connected_events": [],
        },
        {
            "id": "e25",
            "title": "Historia de Rut",
            "era": "Jueces",
            "testament": "OT",
            "date_label": "~1100 a.C.",
            "description": "Rut muestra lealtad a su suegra Noemí y se casa con Booz.",
            "scripture_ref": "Ruth 1-4",
            "emoji": "🌾",
            "characters_involved": ["c12"],
            "connected_events": [],
        },
        {
            "id": "e26",
            "title": "La Fuerza de Sansón",
            "era": "Jueces",
            "testament": "OT",
            "date_label": "~1070 a.C.",
            "description": "Sansón utiliza su inmensa fuerza para luchar contra los filisteos.",
            "scripture_ref": "Judges 13-16",
            "emoji": "💪",
            "characters_involved": [],
            "connected_events": [],
        },
        {
            "id": "e27",
            "title": "Llamado de Samuel",
            "era": "Jueces",
            "testament": "OT",
            "date_label": "~1050 a.C.",
            "description": "Dios llama al joven Samuel para ser profeta.",
            "scripture_ref": "1 Samuel 3",
            "emoji": "🗣️",
            "characters_involved": ["c13"],
            "connected_events": [],
        },
        {
            "id": "e28",
            "title": "Saúl Ungido Rey",
            "era": "Reino Unido",
            "testament": "OT",
            "date_label": "~1050 a.C.",
            "description": "Samuel unge a Saúl como el primer rey de Israel.",
            "scripture_ref": "1 Samuel 10",
            "emoji": "👑",
            "characters_involved": ["c13", "c14"],
            "connected_events": [],
        },
        {
            "id": "e29",
            "title": "David y Goliat",
            "era": "Reino Unido",
            "testament": "OT",
            "date_label": "~1025 a.C.",
            "description": "El joven David derrota al gigante campeón filisteo Goliat.",
            "scripture_ref": "1 Samuel 17",
            "emoji": "🪨",
            "characters_involved": ["c15"],
            "connected_events": [],
        },
        {
            "id": "e30",
            "title": "David se Convierte en Rey",
            "era": "Reino Unido",
            "testament": "OT",
            "date_label": "~1010 a.C.",
            "description": "David es nombrado rey sobre todo Israel.",
            "scripture_ref": "2 Samuel 5",
            "emoji": "👑",
            "characters_involved": ["c15"],
            "connected_events": [],
        },
        {
            "id": "e31",
            "title": "David y Betsabé",
            "era": "Reino Unido",
            "testament": "OT",
            "date_label": "~990 a.C.",
            "description": "David comete adulterio con Betsabé y enfrenta graves consecuencias.",
            "scripture_ref": "2 Samuel 11",
            "emoji": "💔",
            "characters_involved": ["c15"],
            "connected_events": [],
        },
        {
            "id": "e32",
            "title": "Salomón Construye el Templo",
            "era": "Reino Unido",
            "testament": "OT",
            "date_label": "~960 a.C.",
            "description": "El rey Salomón construye el primer templo permanente en Jerusalén.",
            "scripture_ref": "1 Kings 6",
            "emoji": "🏛️",
            "characters_involved": ["c16"],
            "connected_events": [],
        },
        {
            "id": "e33",
            "title": "La Sabiduría de Salomón",
            "era": "Reino Unido",
            "testament": "OT",
            "date_label": "~970 a.C.",
            "description": "Salomón pide sabiduría a Dios y juzga un caso difícil entre dos madres.",
            "scripture_ref": "1 Kings 3",
            "emoji": "⚖️",
            "characters_involved": ["c16"],
            "connected_events": [],
        },
        {
            "id": "e34",
            "title": "El Reino se Divide",
            "era": "Reino Dividido",
            "testament": "OT",
            "date_label": "~930 a.C.",
            "description": "Después de la muerte de Salomón, el reino se divide en Israel (Norte) y Judá (Sur).",
            "scripture_ref": "1 Kings 12",
            "emoji": "⚔️",
            "characters_involved": ["c16"],
            "connected_events": [],
        },
        {
            "id": "e35",
            "title": "Elías contra los Profetas de Baal",
            "era": "Reino Dividido",
            "testament": "OT",
            "date_label": "~860 a.C.",
            "description": "Elías desafía a los profetas de Baal en el Monte Carmelo y Dios envía fuego.",
            "scripture_ref": "1 Kings 18",
            "emoji": "🔥",
            "characters_involved": ["c17"],
            "connected_events": [],
        },
        {
            "id": "e36",
            "title": "Elías Llevado al Cielo",
            "era": "Reino Dividido",
            "testament": "OT",
            "date_label": "~850 a.C.",
            "description": "Elías es llevado al cielo en un torbellino.",
            "scripture_ref": "2 Kings 2",
            "emoji": "🌪️",
            "characters_involved": ["c17"],
            "connected_events": [],
        },
        {
            "id": "e37",
            "title": "Las Profecías de Isaías",
            "era": "Reino Dividido",
            "testament": "OT",
            "date_label": "~740 a.C.",
            "description": "Isaías ve el trono de Dios y profetiza sobre el Mesías venidero.",
            "scripture_ref": "Isaiah 6, 53",
            "emoji": "📜",
            "characters_involved": ["c18"],
            "connected_events": ["e62"],
        },
        {
            "id": "e38",
            "title": "Caída del Reino del Norte",
            "era": "Reino Dividido",
            "testament": "OT",
            "date_label": "722 a.C.",
            "description": "El imperio asirio conquista el reino del norte, Israel.",
            "scripture_ref": "2 Kings 17",
            "emoji": "🛡️",
            "characters_involved": [],
            "connected_events": [],
        },
        {
            "id": "e39",
            "title": "Caída de Jerusalén",
            "era": "Exilio",
            "testament": "OT",
            "date_label": "586 a.C.",
            "description": "Babilonia conquista Judá, destruye el templo y exilia al pueblo.",
            "scripture_ref": "2 Kings 25",
            "emoji": "🔥",
            "characters_involved": ["c19"],
            "connected_events": [],
        },
        {
            "id": "e40",
            "title": "Daniel en el Foso de los Leones",
            "era": "Exilio",
            "testament": "OT",
            "date_label": "~539 a.C.",
            "description": "Daniel es arrojado a un foso de leones por orar, pero Dios lo protege.",
            "scripture_ref": "Daniel 6",
            "emoji": "🦁",
            "characters_involved": ["c19"],
            "connected_events": [],
        },
        {
            "id": "e41",
            "title": "El Horno de Fuego",
            "era": "Exilio",
            "testament": "OT",
            "date_label": "~600 a.C.",
            "description": "Los amigos de Daniel son salvados de un horno ardiente.",
            "scripture_ref": "Daniel 3",
            "emoji": "🔥",
            "characters_involved": ["c19"],
            "connected_events": [],
        },
        {
            "id": "e42",
            "title": "Las Visiones de Daniel",
            "era": "Exilio",
            "testament": "OT",
            "date_label": "~550 a.C.",
            "description": "Daniel recibe visiones apocalípticas de futuros reinos y del Hijo del Hombre.",
            "scripture_ref": "Daniel 7-12",
            "emoji": "👁️",
            "characters_involved": ["c19"],
            "connected_events": [],
        },
        {
            "id": "e43",
            "title": "Regreso del Exilio",
            "era": "Post-Exilio",
            "testament": "OT",
            "date_label": "538 a.C.",
            "description": "Ciro de Persia permite que los judíos regresen a Jerusalén.",
            "scripture_ref": "Ezra 1",
            "emoji": "🚶",
            "characters_involved": [],
            "connected_events": ["e44"],
        },
        {
            "id": "e44",
            "title": "Reconstrucción del Templo",
            "era": "Post-Exilio",
            "testament": "OT",
            "date_label": "516 a.C.",
            "description": "Los exiliados que regresan reconstruyen el templo en Jerusalén.",
            "scripture_ref": "Ezra 3-6",
            "emoji": "🏗️",
            "characters_involved": [],
            "connected_events": [],
        },
        {
            "id": "e45",
            "title": "Ester Salva a su Pueblo",
            "era": "Post-Exilio",
            "testament": "OT",
            "date_label": "~470 a.C.",
            "description": "La reina Ester arriesga su vida para salvar al pueblo judío de un complot genocida.",
            "scripture_ref": "Esther 4-7",
            "emoji": "👑",
            "characters_involved": ["c20"],
            "connected_events": [],
        },
        {
            "id": "e46",
            "title": "Nehemías Reconstruye los Muros",
            "era": "Post-Exilio",
            "testament": "OT",
            "date_label": "445 a.C.",
            "description": "Nehemías lidera el esfuerzo para reconstruir los muros de Jerusalén.",
            "scripture_ref": "Nehemiah 2-6",
            "emoji": "🧱",
            "characters_involved": [],
            "connected_events": [],
        },
        {
            "id": "e47",
            "title": "Los Años de Silencio",
            "era": "Intertestamentario",
            "testament": "OT",
            "date_label": "~400-4 a.C.",
            "description": "Un período de 400 años sin profetas bíblicos registrados, terminando con Juan el Bautista.",
            "scripture_ref": "History",
            "emoji": "🤫",
            "characters_involved": [],
            "connected_events": [],
        },
        {
            "id": "e48",
            "title": "Anunciación a María",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~6 a.C.",
            "description": "El ángel Gabriel anuncia a María que dará a luz al Hijo de Dios.",
            "scripture_ref": "Luke 1",
            "emoji": "👼",
            "characters_involved": ["n1"],
            "connected_events": ["e49"],
        },
        {
            "id": "e49",
            "title": "Nacimiento de Jesús",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~5 a.C.",
            "description": "Jesús nace en un pesebre en Belén.",
            "scripture_ref": "Luke 2",
            "emoji": "✨",
            "characters_involved": ["n1", "n2", "n4"],
            "connected_events": [],
        },
        {
            "id": "e50",
            "title": "Huida a Egipto",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~4 a.C.",
            "description": "José y María huyen a Egipto para proteger a Jesús del rey Herodes.",
            "scripture_ref": "Matthew 2",
            "emoji": "ὂA",
            "characters_involved": ["n1", "n2", "n4"],
            "connected_events": [],
        },
        {
            "id": "e51",
            "title": "Jesús en el Templo a los 12",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~8 d.C.",
            "description": "El joven Jesús es encontrado debatiendo con los eruditos en el templo.",
            "scripture_ref": "Luke 2",
            "emoji": "📖",
            "characters_involved": ["n4"],
            "connected_events": [],
        },
        {
            "id": "e52",
            "title": "Bautismo de Jesús",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~27 d.C.",
            "description": "Jesús es bautizado por Juan, y el Espíritu Santo desciende como una paloma.",
            "scripture_ref": "Matthew 3",
            "emoji": "💧",
            "characters_involved": ["n3", "n4"],
            "connected_events": ["e53"],
        },
        {
            "id": "e53",
            "title": "Tentación en el Desierto",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~27 d.C.",
            "description": "Jesús ayuna durante 40 días y resiste con éxito las tentaciones de Satanás.",
            "scripture_ref": "Matthew 4",
            "emoji": "🏜️",
            "characters_involved": ["n4"],
            "connected_events": [],
        },
        {
            "id": "e54",
            "title": "Llamado de los Discípulos",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~27 d.C.",
            "description": "Jesús llama a pescadores como Pedro, Santiago y Juan para seguirle.",
            "scripture_ref": "Matthew 4",
            "emoji": "🎣",
            "characters_involved": ["n4", "n5", "n6", "n7"],
            "connected_events": [],
        },
        {
            "id": "e55",
            "title": "Sermón del Monte",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~28 d.C.",
            "description": "Jesús ofrece su enseñanza más famosa, incluyendo las Bienaventuranzas.",
            "scripture_ref": "Matthew 5-7",
            "emoji": "⛰️",
            "characters_involved": ["n4"],
            "connected_events": [],
        },
        {
            "id": "e56",
            "title": "Alimentación de los 5000",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~29 d.C.",
            "description": "Jesús alimenta milagrosamente a una multitud con cinco panes y dos peces.",
            "scripture_ref": "John 6",
            "emoji": "🍞",
            "characters_involved": ["n4"],
            "connected_events": [],
        },
        {
            "id": "e57",
            "title": "La Transfiguración",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~29 d.C.",
            "description": "Jesús se revela en gloria junto a Moisés y Elías.",
            "scripture_ref": "Matthew 17",
            "emoji": "✨",
            "characters_involved": ["n4", "n5", "n6", "n7", "c9", "c17"],
            "connected_events": [],
        },
        {
            "id": "e58",
            "title": "Resurrección de Lázaro",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~30 d.C.",
            "description": "Jesús resucita a Lázaro de entre los muertos, mostrando su poder sobre la muerte.",
            "scripture_ref": "John 11",
            "emoji": "⚰️",
            "characters_involved": ["n4"],
            "connected_events": [],
        },
        {
            "id": "e59",
            "title": "Entrada Triunfal",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~30 d.C.",
            "description": "Jesús entra en Jerusalén sobre un asno, recibido por multitudes.",
            "scripture_ref": "Matthew 21",
            "emoji": "🌿",
            "characters_involved": ["n4"],
            "connected_events": ["e60"],
        },
        {
            "id": "e60",
            "title": "La Última Cena",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~30 d.C.",
            "description": "Jesús comparte una última comida de Pascua con sus discípulos.",
            "scripture_ref": "Matthew 26",
            "emoji": "🍷",
            "characters_involved": ["n4", "n5", "n6", "n7"],
            "connected_events": ["e61"],
        },
        {
            "id": "e61",
            "title": "Huerto de Getsemaní",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~30 d.C.",
            "description": "Jesús ora en agonía antes de su arresto.",
            "scripture_ref": "Matthew 26",
            "emoji": "🌳",
            "characters_involved": ["n4", "n5", "n6"],
            "connected_events": ["e62"],
        },
        {
            "id": "e62",
            "title": "Juicio y Crucifixión",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~30 d.C.",
            "description": "Jesús es juzgado injustamente y crucificado, ofreciéndose como sacrificio por los pecados.",
            "scripture_ref": "Matthew 27",
            "emoji": "✝️",
            "characters_involved": ["n4"],
            "connected_events": ["e63"],
        },
        {
            "id": "e63",
            "title": "Resurrección",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~30 d.C.",
            "description": "Jesús resucita de entre los muertos al tercer día.",
            "scripture_ref": "Matthew 28",
            "emoji": "🌅",
            "characters_involved": ["n4", "n11"],
            "connected_events": ["e64"],
        },
        {
            "id": "e64",
            "title": "La Gran Comisión",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~30 d.C.",
            "description": "Jesús ordena a sus discípulos hacer discípulos en todas las naciones.",
            "scripture_ref": "Matthew 28",
            "emoji": "🌎",
            "characters_involved": ["n4", "n5", "n6"],
            "connected_events": ["e65"],
        },
        {
            "id": "e65",
            "title": "Ascensión",
            "era": "Evangelios",
            "testament": "NT",
            "date_label": "~30 d.C.",
            "description": "Jesús asciende al cielo cuarenta días después de su resurrección.",
            "scripture_ref": "Acts 1",
            "emoji": "☁️",
            "characters_involved": ["n4"],
            "connected_events": [],
        },
        {
            "id": "e66",
            "title": "Pentecostés",
            "era": "Iglesia Primitiva",
            "testament": "NT",
            "date_label": "~30 d.C.",
            "description": "El Espíritu Santo empodera a los creyentes, dando nacimiento a la iglesia primitiva.",
            "scripture_ref": "Acts 2",
            "emoji": "🔥",
            "characters_involved": ["n5"],
            "connected_events": [],
        },
        {
            "id": "e67",
            "title": "Lapidación de Esteban",
            "era": "Iglesia Primitiva",
            "testament": "NT",
            "date_label": "~34 d.C.",
            "description": "Esteban se convierte en el primer mártir cristiano.",
            "scripture_ref": "Acts 7",
            "emoji": "🪨",
            "characters_involved": ["n12"],
            "connected_events": [],
        },
        {
            "id": "e68",
            "title": "Conversión de Pablo",
            "era": "Iglesia Primitiva",
            "testament": "NT",
            "date_label": "~35 d.C.",
            "description": "Saulo se encuentra con el Cristo resucitado y se convierte en el Apóstol Pablo.",
            "scripture_ref": "Acts 9",
            "emoji": "⚡",
            "characters_involved": ["n8"],
            "connected_events": ["e69"],
        },
        {
            "id": "e69",
            "title": "Viajes Misioneros de Pablo",
            "era": "Iglesia Primitiva",
            "testament": "NT",
            "date_label": "~46-60 d.C.",
            "description": "Pablo viaja por el Imperio Romano difundiendo el Evangelio.",
            "scripture_ref": "Acts 13-20",
            "emoji": "⛵",
            "characters_involved": ["n8", "n9", "n10"],
            "connected_events": [],
        },
        {
            "id": "e70",
            "title": "Cartas de Pablo",
            "era": "Iglesia Primitiva",
            "testament": "NT",
            "date_label": "~50-67 d.C.",
            "description": "Pablo escribe epístolas para instruir y animar a las primeras iglesias.",
            "scripture_ref": "Various",
            "emoji": "✉️",
            "characters_involved": ["n8", "n10"],
            "connected_events": [],
        },
        {
            "id": "e71",
            "title": "Destrucción del Templo",
            "era": "Iglesia Primitiva",
            "testament": "NT",
            "date_label": "70 d.C.",
            "description": "Los romanos destruyen el Segundo Templo en Jerusalén.",
            "scripture_ref": "History",
            "emoji": "🔥",
            "characters_involved": [],
            "connected_events": [],
        },
        {
            "id": "e72",
            "title": "El Apocalipsis de Juan",
            "era": "Iglesia Primitiva",
            "testament": "NT",
            "date_label": "~95 d.C.",
            "description": "Juan recibe visiones de los últimos tiempos y de la victoria final de Cristo.",
            "scripture_ref": "Revelation 1-22",
            "emoji": "👁️",
            "characters_involved": ["n6"],
            "connected_events": [],
        },
    ]
    view_state: str = "overview"
    active_view: str = "map"
    selected_event_id: Optional[str] = None
    selected_character_id: Optional[str] = None
    hovered_character_id: Optional[str] = None
    unified_search_query: str = ""
    search_category: str = "Todos"
    search_focused: bool = False
    selected_book_id: Optional[str] = None
    book_scripture_text: str = ""
    book_scripture_loading: bool = False
    book_scripture_chapter: int = 1
    filter_role: str = "All"
    selected_era: str = "All"
    eras: list[str] = [
        "Todos",
        "Creación",
        "Pre-Diluvio",
        "Patriarcal",
        "Éxodo",
        "Conquista",
        "Jueces",
        "Reino Unido",
        "Reino Dividido",
        "Exilio",
        "Post-Exilio",
        "Evangelios",
        "Iglesia Primitiva",
    ]
    roles: list[str] = [
        "Todos",
        "Patriarca",
        "Matriarca",
        "Profeta",
        "Rey",
        "Reina",
        "Apóstol",
        "Líder",
        "Mesías",
        "Figura",
        "Discípulo",
        "Evangelista",
        "Sacerdote",
        "Diácono",
    ]
    legend_expanded: bool = True
    legend_has_auto_closed: bool = False
    api_bible_key: str = "XSgyxGRjoNebhxMNbJR2U"
    bible_id: str = "e3f420b9665abaeb-01"
    scripture_text: str = ""
    scripture_loading: bool = False
    scripture_reference: str = ""
    scripture_error: str = ""
    scripture_search_results: list[dict[str, str]] = []
    scripture_search_loading: bool = False
    scripture_search_query: str = ""
    selected_scripture_result: Optional[dict[str, str]] = None
    context_modal_open: bool = False
    context_chapter_text: str = ""
    context_chapter_loading: bool = False
    context_chapter_reference: str = ""
    context_chapter_id: str = ""

    @rx.event
    def toggle_legend(self):
        self.legend_expanded = not self.legend_expanded

    @rx.event
    async def auto_close_legend(self):
        if not self.legend_has_auto_closed:
            import asyncio

            await asyncio.sleep(4)
            self.legend_expanded = False
            self.legend_has_auto_closed = True

    @rx.var
    def ot_count(self) -> int:
        return len([c for c in self.characters if c["testament"] == "OT"])

    @rx.var
    def nt_count(self) -> int:
        return len([c for c in self.characters if c["testament"] == "NT"])

    @rx.var
    def cross_testament_prophecies(self) -> int:
        count = 0
        for conn in self.connections:
            if conn["type"] == "profecía":
                s = next(
                    (c for c in self.characters if c["id"] == conn["source"]), None
                )
                t = next(
                    (c for c in self.characters if c["id"] == conn["target"]), None
                )
                if s and t and (s["testament"] != t["testament"]):
                    count += 1
        return count

    @rx.event
    def set_view(self, view: str):
        self.view_state = view
        self.selected_character_id = None
        self.selected_event_id = None

    @rx.event
    def select_character(self, char_id: str):
        self.selected_character_id = char_id
        self.selected_event_id = None
        self.scripture_text = ""
        self.scripture_error = ""

    @rx.event
    def select_event(self, event_id: str):
        self.selected_event_id = event_id
        self.selected_character_id = None
        self.selected_book_id = None
        self.scripture_text = ""
        self.scripture_error = ""
        self.clear_search()

    @rx.event
    def select_book(self, book_id: str):
        self.selected_book_id = book_id
        self.selected_character_id = None
        self.selected_event_id = None
        self.book_scripture_chapter = 1
        self.book_scripture_text = ""
        self.clear_search()

    @rx.event
    def select_scripture_result(self, result: dict[str, str]):
        """Select a scripture search result and display it in the detail panel."""
        self.scripture_text = result.get("full_text", result.get("text", ""))
        self.scripture_reference = result.get("reference", "")
        self.scripture_error = ""
        self.scripture_loading = False
        self.selected_character_id = None
        self.selected_event_id = None
        self.selected_book_id = None
        self.selected_scripture_result = result
        self.clear_search()

    @rx.event
    def clear_selection(self):
        self.selected_character_id = None
        self.selected_event_id = None
        self.selected_book_id = None
        self.selected_scripture_result = None
        self.scripture_text = ""
        self.scripture_error = ""

    @rx.event
    def open_context_modal(self):
        """Open the full-chapter context modal for the current scripture result."""
        if not self.selected_scripture_result:
            return
        passage_id = self.selected_scripture_result.get("id", "")
        if not passage_id:
            return
        parts = passage_id.split(".")
        if len(parts) >= 2:
            chapter_id = f"{parts[0]}.{parts[1]}"
        else:
            chapter_id = passage_id
        self.context_chapter_id = chapter_id
        self.context_chapter_reference = self.selected_scripture_result.get(
            "reference", ""
        )
        self.context_modal_open = True
        return BibleState.fetch_context_chapter(chapter_id)

    @rx.event
    def close_context_modal(self):
        self.context_modal_open = False
        self.context_chapter_text = ""
        self.context_chapter_loading = False

    @rx.event(background=True)
    async def fetch_context_chapter(self, chapter_id: str):
        """Fetch the full chapter from API.Bible for context."""
        async with self:
            self.context_chapter_loading = True
            self.context_chapter_text = ""
        try:
            url = f"https://rest.api.bible/v1/bibles/{self.bible_id}/chapters/{chapter_id}"
            headers = {"api-key": self.api_bible_key}
            params = {"content-type": "text"}
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(requests.get, url, headers=headers, params=params),
            )
            if response.status_code == 200:
                data = response.json().get("data", {})
                content = data.get("content", "")
                reference = data.get("reference", chapter_id)
                async with self:
                    self.context_chapter_text = content
                    self.context_chapter_reference = reference
                    self.context_chapter_loading = False
            else:
                async with self:
                    self.context_chapter_text = (
                        f"Error al cargar el capítulo: {response.status_code}"
                    )
                    self.context_chapter_loading = False
        except Exception as e:
            import logging

            logging.exception("Error fetching context chapter")
            async with self:
                self.context_chapter_text = f"Error: {str(e)}"
                self.context_chapter_loading = False

    @rx.event
    def navigate_context_chapter(self, direction: int):
        """Navigate to previous or next chapter in the modal."""
        if not self.context_chapter_id:
            return
        parts = self.context_chapter_id.split(".")
        if len(parts) >= 2:
            book = parts[0]
            try:
                chapter_num = int(parts[1])
            except ValueError:
                return
            new_chapter = max(1, chapter_num + direction)
            new_id = f"{book}.{new_chapter}"
            self.context_chapter_id = new_id
            return BibleState.fetch_context_chapter(new_id)

    @rx.event
    def set_active_view(self, view: str):
        self.active_view = view
        self.clear_selection()

    @rx.event
    def set_hovered(self, char_id: str):
        self.hovered_character_id = char_id

    @rx.event
    def clear_hovered(self):
        self.hovered_character_id = None

    @rx.event(background=True)
    async def fetch_scripture(self, scripture_ref: str):
        async with self:
            self.scripture_loading = True
            self.scripture_error = ""
            self.scripture_text = ""
            self.scripture_reference = scripture_ref
        passage_id = SCRIPTURE_REFS.get(scripture_ref, "")
        if not passage_id:
            async with self:
                self.scripture_loading = False
                self.scripture_text = "No hay pasaje bíblico para este evento."
            return
        try:
            url = f"https://rest.api.bible/v1/bibles/{self.bible_id}/passages/{passage_id}"
            headers = {"api-key": self.api_bible_key}
            params = {
                "content-type": "text",
                "include-verse-numbers": True,
                "include-titles": False,
            }
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(requests.get, url, headers=headers, params=params),
            )
            if response.status_code == 200:
                data = response.json().get("data", {})
                content = data.get("content", "")
                async with self:
                    self.scripture_text = content
                    self.scripture_loading = False
            else:
                async with self:
                    self.scripture_error = f"Error: {response.text}"
                    self.scripture_loading = False
        except Exception as e:
            logging.exception("Unexpected error")
            async with self:
                self.scripture_error = f"Error: {str(e)}"
                self.scripture_loading = False

    @rx.event
    def update_unified_search(self, query: str):
        self.unified_search_query = query
        if len(query) >= 3 and self.search_category in ["Todos", "Escrituras"]:
            return BibleState.search_scripture_api(query)
        else:
            self.scripture_search_results = []

    @rx.event
    def set_search_category(self, cat: str):
        self.search_category = cat
        if len(self.unified_search_query) >= 3 and cat in ["Todos", "Escrituras"]:
            return BibleState.search_scripture_api(self.unified_search_query)
        elif cat not in ["Todos", "Escrituras"]:
            self.scripture_search_results = []

    @rx.event
    def set_search_focused(self, focused: bool):
        self.search_focused = focused

    @rx.event
    def clear_search(self):
        self.unified_search_query = ""
        self.search_focused = False
        self.scripture_search_results = []
        self.scripture_search_loading = False
        self.scripture_search_query = ""

    @rx.event(background=True)
    async def search_scripture_api(self, query: str):
        """Search API.Bible for verses/passages matching the query."""
        if len(query) < 3:
            async with self:
                self.scripture_search_results = []
                self.scripture_search_loading = False
            return
        async with self:
            self.scripture_search_loading = True
            self.scripture_search_query = query
        try:
            normalized = normalize_query(query)
            url = f"https://rest.api.bible/v1/bibles/{self.bible_id}/search"
            headers = {"api-key": self.api_bible_key}
            params = {
                "query": normalized,
                "limit": 5,
                "fuzziness": "AUTO",
                "sort": "relevance",
            }
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(requests.get, url, headers=headers, params=params),
            )
            async with self:
                if self.scripture_search_query != query:
                    return
            if response.status_code == 200:
                data = response.json().get("data", {})
                passages = data.get("passages", [])
                verses = data.get("verses", [])
                results = []
                if passages:
                    for p in passages[:5]:
                        content = strip_html(p.get("content", ""))
                        results.append(
                            {
                                "id": p.get("id", ""),
                                "reference": p.get("reference", ""),
                                "text": content[:200]
                                + ("..." if len(content) > 200 else ""),
                                "type": "passage",
                                "full_text": content,
                            }
                        )
                elif verses:
                    for v in verses[:8]:
                        results.append(
                            {
                                "id": v.get("id", ""),
                                "reference": v.get("reference", ""),
                                "text": v.get("text", "")[:200],
                                "type": "verse",
                                "full_text": v.get("text", ""),
                            }
                        )
                async with self:
                    if self.scripture_search_query == query:
                        self.scripture_search_results = results
                        self.scripture_search_loading = False
            else:
                async with self:
                    self.scripture_search_results = []
                    self.scripture_search_loading = False
        except Exception as e:
            logging.exception("Scripture search error")
            async with self:
                self.scripture_search_results = []
                self.scripture_search_loading = False

    @rx.event(background=True)
    async def fetch_book_chapter(self, book_api_id: str, chapter: int):
        async with self:
            self.book_scripture_loading = True
            self.book_scripture_text = ""
        try:
            chapter_id = f"{book_api_id}.{chapter}"
            url = f"https://rest.api.bible/v1/bibles/{self.bible_id}/chapters/{chapter_id}"
            headers = {"api-key": self.api_bible_key}
            params = {"content-type": "text"}
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(requests.get, url, headers=headers, params=params),
            )
            if response.status_code == 200:
                data = response.json().get("data", {})
                content = data.get("content", "")
                async with self:
                    self.book_scripture_text = content
                    self.book_scripture_loading = False
            else:
                async with self:
                    self.book_scripture_text = f"Error: {response.text}"
                    self.book_scripture_loading = False
        except Exception as e:
            logging.exception("Error fetching chapter")
            async with self:
                self.book_scripture_text = f"Error: {str(e)}"
                self.book_scripture_loading = False

    @rx.event
    def set_book_chapter(self, chapter: int):
        if not self.selected_book:
            return
        self.book_scripture_chapter = chapter
        return BibleState.fetch_book_chapter(
            BibleState.selected_book["api_id"], chapter
        )

    @rx.event
    def set_filter(self, role: str):
        self.filter_role = role
        self.selected_character_id = None

    @rx.event
    def set_era(self, era: str):
        if era == "Todos" or era == self.selected_era:
            self.selected_era = "All"
        else:
            self.selected_era = era
        self.selected_character_id = None

    @rx.var
    def visible_characters(self) -> list[Character]:
        if self.view_state == "old_testament":
            return [c for c in self.characters if c["testament"] == "OT"]
        elif self.view_state == "new_testament":
            return [c for c in self.characters if c["testament"] == "NT"]
        return self.characters

    @rx.var
    def matched_character_ids(self) -> list[str]:
        result = self.visible_characters
        if self.unified_search_query:
            q = self.unified_search_query.lower()
            result = [
                c
                for c in result
                if q in c["name"].lower() or q in c["description"].lower()
            ]
        if self.filter_role != "All":
            result = [c for c in result if c["role"] == self.filter_role]
        if self.selected_era != "All":
            result = [c for c in result if c["era"] == self.selected_era]
        return [c["id"] for c in result]

    @rx.var
    def is_filtering(self) -> bool:
        return (
            bool(self.unified_search_query)
            or self.filter_role != "All"
            or self.selected_era != "All"
        )

    @rx.var
    def search_results_characters(self) -> list[Character]:
        if len(self.unified_search_query) < 2:
            return []
        if self.search_category not in ["Todos", "Personajes"]:
            return []
        q = self.unified_search_query.lower()
        return [
            c
            for c in self.characters
            if q in c["name"].lower()
            or q in c["description"].lower()
            or q in c["role"].lower()
        ]

    @rx.var
    def search_results_events(self) -> list[BibleEvent]:
        if len(self.unified_search_query) < 2:
            return []
        if self.search_category not in ["Todos", "Eventos"]:
            return []
        q = self.unified_search_query.lower()
        return [
            e
            for e in self.events
            if q in e["title"].lower()
            or q in e["description"].lower()
            or q in e["date_label"].lower()
        ]

    @rx.var
    def search_results_books(self) -> list[BibleBook]:
        if len(self.unified_search_query) < 2:
            return []
        if self.search_category not in ["Todos", "Libros"]:
            return []
        q = self.unified_search_query.lower()
        return [
            b
            for b in self.bible_books
            if q in b["name"].lower()
            or q in b["abbr"].lower()
            or q in b["category"].lower()
        ]

    @rx.var
    def search_results_scriptures(self) -> list[dict[str, str]]:
        if len(self.unified_search_query) < 2:
            return []
        if self.search_category not in ["Todos", "Escrituras"]:
            return []
        q = self.unified_search_query.lower()
        results = []
        for ev in self.events:
            if q in ev["scripture_ref"].lower():
                results.append(
                    {
                        "id": ev["id"],
                        "title": ev["title"],
                        "scripture_ref": ev["scripture_ref"],
                        "emoji": "📖",
                        "type": "event_scripture",
                    }
                )
        return results

    @rx.var
    def total_search_results(self) -> int:
        return (
            len(self.search_results_characters)
            + len(self.search_results_events)
            + len(self.search_results_books)
            + len(self.search_results_scriptures)
            + len(self.scripture_search_results)
        )

    @rx.var
    def has_search_results(self) -> bool:
        return len(self.unified_search_query) >= 2 and self.total_search_results > 0

    @rx.var
    def selected_book(self) -> Optional[BibleBook]:
        if not self.selected_book_id:
            return None
        return next(
            (b for b in self.bible_books if b["id"] == self.selected_book_id), None
        )

    @rx.var
    def match_count(self) -> int:
        return len(self.matched_character_ids)

    @rx.var
    def selected_character(self) -> Optional[Character]:
        if not self.selected_character_id:
            return None
        for c in self.characters:
            if c["id"] == self.selected_character_id:
                return c
        return None

    @rx.var
    def selected_event(self) -> Optional[BibleEvent]:
        if not self.selected_event_id:
            return None
        for e in self.events:
            if e["id"] == self.selected_event_id:
                return e
        return None

    @rx.var
    def selected_event_characters(self) -> list[Character]:
        event = self.selected_event
        if not event:
            return []
        return [c for c in self.characters if c["id"] in event["characters_involved"]]

    @rx.var
    def selected_event_connected_details(self) -> list[BibleEvent]:
        event = self.selected_event
        if not event:
            return []
        return [e for e in self.events if e["id"] in event["connected_events"]]

    @rx.var
    def character_events(self) -> list[BibleEvent]:
        if not self.selected_character_id:
            return []
        return [
            e
            for e in self.events
            if self.selected_character_id in e["characters_involved"]
        ]

    @rx.var
    def has_cross_testament_connection(self) -> bool:
        event = self.selected_event
        if not event:
            return False
        for e in self.events:
            if e["id"] in event["connected_events"]:
                if e["testament"] != event["testament"]:
                    return True
        return False

    @rx.var
    def timeline_events_by_era(self) -> list[EraGroup]:
        groups = []
        era_colors = {
            "Creación": "text-green-800 bg-green-100 border-green-300",
            "Pre-Diluvio": "text-cyan-800 bg-cyan-100 border-cyan-300",
            "Patriarcal": "text-amber-800 bg-amber-100 border-amber-300",
            "Éxodo": "text-red-800 bg-red-100 border-red-300",
            "Conquista": "text-orange-800 bg-orange-100 border-orange-300",
            "Jueces": "text-stone-800 bg-stone-200 border-stone-400",
            "Reino Unido": "text-yellow-800 bg-yellow-100 border-yellow-400",
            "Reino Dividido": "text-yellow-900 bg-yellow-200 border-yellow-500",
            "Exilio": "text-purple-800 bg-purple-100 border-purple-300",
            "Post-Exilio": "text-indigo-800 bg-indigo-100 border-indigo-300",
            "Intertestamentario": "text-gray-600 bg-gray-100 border-gray-300",
            "Evangelios": "text-blue-800 bg-blue-100 border-blue-300",
            "Iglesia Primitiva": "text-teal-800 bg-teal-100 border-teal-300",
        }
        era_emojis = {
            "Creación": "🌍",
            "Pre-Diluvio": "🌊",
            "Patriarcal": "⛺",
            "Éxodo": "🏜️",
            "Conquista": "⚔️",
            "Jueces": "⚖️",
            "Reino Unido": "👑",
            "Reino Dividido": "💔",
            "Exilio": "⛓️",
            "Post-Exilio": "🧱",
            "Intertestamentario": "🤫",
            "Evangelios": "✨",
            "Iglesia Primitiva": "🕊️",
        }
        for era in self.eras:
            if era == "All":
                continue
            era_events = [e for e in self.events if e["era"] == era]
            if era_events:
                groups.append(
                    {
                        "era": era,
                        "color": era_colors.get(
                            era, "text-stone-800 bg-stone-100 border-stone-300"
                        ),
                        "emoji": era_emojis.get(era, "📅"),
                        "events": era_events,
                    }
                )
        return groups

    @rx.var
    def connection_lines(self) -> list[dict[str, str | float | bool]]:
        if self.view_state == "overview":
            return []
        visible_ids = {c["id"] for c in self.visible_characters}
        char_dict = {c["id"]: c for c in self.visible_characters}
        lines = []
        for i, conn in enumerate(self.connections):
            s = conn["source"]
            t = conn["target"]
            if s in visible_ids and t in visible_ids:
                is_active = False
                is_dimmed = False
                if self.selected_character_id:
                    if (
                        s == self.selected_character_id
                        or t == self.selected_character_id
                    ):
                        is_active = True
                    else:
                        is_dimmed = True
                elif self.hovered_character_id:
                    if s == self.hovered_character_id or t == self.hovered_character_id:
                        is_active = True
                    else:
                        is_dimmed = True
                lines.append(
                    {
                        "id": f"conn_{i}",
                        "x1": char_dict[s]["x"],
                        "y1": char_dict[s]["y"],
                        "x2": char_dict[t]["x"],
                        "y2": char_dict[t]["y"],
                        "type": conn["type"],
                        "is_active": is_active,
                        "is_dimmed": is_dimmed,
                    }
                )
        return lines

    @rx.var
    def selected_character_connections(self) -> list[dict[str, str]]:
        if not self.selected_character_id:
            return []
        char_conns = []
        for conn in self.connections:
            if conn["source"] == self.selected_character_id:
                target_name = next(
                    (c["name"] for c in self.characters if c["id"] == conn["target"]),
                    "Unknown",
                )
                char_conns.append(
                    {
                        "id": conn["target"],
                        "name": target_name,
                        "type": conn["type"],
                        "desc": conn["desc"],
                        "direction": "to",
                    }
                )
            elif conn["target"] == self.selected_character_id:
                source_name = next(
                    (c["name"] for c in self.characters if c["id"] == conn["source"]),
                    "Unknown",
                )
                char_conns.append(
                    {
                        "id": conn["source"],
                        "name": source_name,
                        "type": conn["type"],
                        "desc": conn["desc"],
                        "direction": "from",
                    }
                )
        return char_conns

    @rx.var
    def map_canvas_height(self) -> str:
        if self.view_state == "new_testament":
            return "1600px"
        return "2200px"