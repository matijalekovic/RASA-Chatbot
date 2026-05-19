"""
Translation utilities for the 1PAX action server.

get_lang(tracker)              → language code ("FR", "ZH-HANS", "SR", …)
                                 or None when the user is writing English.

translate_response(text, lang) → English text translated to lang, or a
                                 localized fallback if translation is unavailable.

Usage in every action:
    from .translation import get_lang, translate_response
    from rasa_sdk.events import SlotSet

    def run(self, dispatcher, tracker, domain):
        lang = get_lang(tracker)
        ...
        dispatcher.utter_message(text=translate_response("Hello!", lang))
        return [SlotSet("language", lang), ...]   # persist across short follow-ups

Requires:  pip install langdetect
Env var:   GEMINI_API_KEY
"""

import json
import logging
import os
import re
import time
import socket
import urllib.error
import urllib.request
from typing import Optional

logger = logging.getLogger(__name__)

_GEMINI_MODEL = "gemini-2.5-flash-lite"
_GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{_GEMINI_MODEL}:generateContent"
)
_TRANSLATE_PROXY_URL = os.environ.get(
    "TRANSLATE_PROXY_URL",
    "http://127.0.0.1:5056/translate",
).strip()

try:
    from langdetect import detect, LangDetectException
    _LANGDETECT_OK = True
except ImportError:
    _LANGDETECT_OK = False


# ── Language name mapping for translation prompts ─────────────────────────────

_LANG_NAMES = {
    "FR":      "French",
    "ES":      "Spanish",
    "PT-PT":   "European Portuguese",
    "PT-BR":   "Brazilian Portuguese",
    "ZH-HANS": "Simplified Chinese",
    "ZH-HANT": "Traditional Chinese",
    "SR":      "Serbian using the Latin alphabet",
    "DE":      "German",
    "IT":      "Italian",
    "NL":      "Dutch",
    "PL":      "Polish",
    "JA":      "Japanese",
    "KO":      "Korean",
    "AR":      "Arabic",
}

# If a user explicitly selected a non-English language, never leak raw English
# when the translation backend is unavailable or returns an unusable result.
_TRANSLATION_FAILURE_TEXT = {
    "FR": "Désolé, la traduction est momentanément indisponible. Veuillez réessayer dans un instant.",
    "ES": "Lo siento, la traducción no está disponible en este momento. Inténtalo de nuevo en unos segundos.",
    "PT-PT": "Desculpe, a tradução está temporariamente indisponível. Tente novamente dentro de instantes.",
    "PT-BR": "Desculpe, a tradução está temporariamente indisponível. Tente novamente em instantes.",
    "ZH-HANS": "抱歉，翻译暂时不可用。请稍后再试。",
    "ZH-HANT": "抱歉，翻譯暫時不可用。請稍後再試。",
    "SR": "Izvinite, prevod trenutno nije dostupan. Pokušajte ponovo za trenutak.",
    "DE": "Entschuldigung, die Übersetzung ist momentan nicht verfügbar. Bitte versuchen Sie es gleich erneut.",
    "IT": "Spiacenti, la traduzione non è momentaneamente disponibile. Riprova tra poco.",
    "NL": "Sorry, vertaling is tijdelijk niet beschikbaar. Probeer het zo opnieuw.",
    "PL": "Przepraszamy, tłumaczenie jest chwilowo niedostępne. Spróbuj ponownie za moment.",
    "JA": "申し訳ありません。現在、翻訳を利用できません。少ししてからもう一度お試しください。",
    "KO": "죄송합니다. 현재 번역을 사용할 수 없습니다. 잠시 후 다시 시도해 주세요.",
    "AR": "عذرًا، الترجمة غير متاحة مؤقتًا. يُرجى المحاولة مرة أخرى بعد قليل.",
}

_ENGLISH_MARKERS = {
    " the ",
    " and ",
    " is ",
    " are ",
    " was ",
    " were ",
    " with ",
    " about ",
    " project",
    " airport",
    " design",
    " company",
    " team",
    " tell ",
    " show ",
    " who ",
    " where ",
    " when ",
    " how ",
    " would ",
    " what ",
}

_SR_WEEKDAYS = {
    "Mon": "Pon",
    "Tue": "Uto",
    "Wed": "Sre",
    "Thu": "Čet",
    "Fri": "Pet",
    "Sat": "Sub",
    "Sun": "Ned",
}

_SR_MONTHS = {
    "Jan": "jan",
    "Feb": "feb",
    "Mar": "mar",
    "Apr": "apr",
    "May": "maj",
    "Jun": "jun",
    "Jul": "jul",
    "Aug": "avg",
    "Sep": "sep",
    "Oct": "okt",
    "Nov": "nov",
    "Dec": "dec",
}

# Entity name set by TranslationComponent in the NLU pipeline
_LANG_ENTITY = "__lang__"

# Fallback: langdetect code → our language code
_LANGDETECT_MAP: dict = {
    "es":    "ES",
    "fr":    "FR",
    "zh-cn": "ZH-HANS",
    "zh-tw": "ZH-HANT",
    "zh":    "ZH-HANS",
    "pt":    "PT-PT",
    "sr":    "SR",
    "hr":    "SR",
    "bs":    "SR",
}


def get_lang(tracker) -> Optional[str]:
    """
    Return the language code for the current user turn, or None for English.

    Priority:
      1. UI metadata      — lang code sent by the frontend with every message
      2. __lang__ entity  — set by TranslationComponent during NLU
      3. language slot    — persisted from a previous turn
      4. langdetect       — last-resort fallback
    """
    latest_text = (tracker.latest_message.get("text") or "").strip()
    lang = (tracker.latest_message.get("metadata") or {}).get("lang")
    if lang:
        return lang

    for entity in tracker.latest_message.get("entities", []):
        if entity.get("entity") == _LANG_ENTITY:
            if _looks_like_english(latest_text):
                continue
            return entity["value"]

    slot = tracker.get_slot("language")
    if slot:
        return slot

    if _LANGDETECT_OK:
        text = latest_text
        if len(text) >= 4 and not _looks_like_english(text):
            try:
                raw = detect(text)
                return _LANGDETECT_MAP.get(raw)
            except Exception:
                pass

    return None


def _ascii_lower(text: str) -> str:
    return text.casefold()


def _looks_like_english(text: str) -> bool:
    normalized = f" {_ascii_lower(text)} "
    if any(marker in normalized for marker in _ENGLISH_MARKERS):
        return True
    words = [word.strip(".,!?;:()[]{}'\"") for word in normalized.split()]
    common = {
        "a",
        "an",
        "do",
        "does",
        "did",
        "can",
        "could",
        "would",
        "should",
        "me",
        "you",
        "your",
        "it",
        "its",
    }
    return sum(1 for word in words if word in common) >= 2


def _gemini_call(
    prompt: str,
    system_instruction: str,
    timeout: float = 5.0,
    attempts: int = 1,
) -> Optional[str]:
    """POST to Gemini REST; return the text or None on any error."""
    api_key = (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )
    if not api_key:
        return None

    for attempt in range(max(1, attempts)):
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {"temperature": 0.1},
        }
        req = urllib.request.Request(
            f"{_GEMINI_URL}?key={api_key}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read())
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (
            TimeoutError,
            socket.timeout,
            urllib.error.URLError,
            urllib.error.HTTPError,
            OSError,
            KeyError,
            IndexError,
            ValueError,
        ) as exc:
            logger.warning(f"Gemini REST call failed on attempt {attempt + 1}: {exc}")
            if attempt < attempts - 1:
                time.sleep(0.25 * (attempt + 1))
    return None


def _normalized_lang(lang: Optional[str]) -> str:
    return (lang or "").strip().upper()


def _translation_failure_text(lang: Optional[str]) -> str:
    normalized = _normalized_lang(lang)
    if normalized in _TRANSLATION_FAILURE_TEXT:
        return _TRANSLATION_FAILURE_TEXT[normalized]
    if normalized.startswith("PT"):
        return _TRANSLATION_FAILURE_TEXT["PT-PT"]
    if normalized.startswith("ZH"):
        return _TRANSLATION_FAILURE_TEXT["ZH-HANS"]
    return _TRANSLATION_FAILURE_TEXT.get(
        normalized,
        "Traduction temporairement indisponible. Veuillez réessayer dans un instant.",
    )


def _sr_24h_time(hour_text: str, minute_text: str, period: str) -> str:
    hour = int(hour_text)
    minute = int(minute_text)
    normalized_period = period.upper()
    if normalized_period == "PM" and hour < 12:
        hour += 12
    elif normalized_period == "AM" and hour == 12:
        hour = 0
    return f"{hour:02d}:{minute:02d}"


def _sr_slot_label(label: str) -> str:
    match = re.match(
        r"^(?P<weekday>[A-Z][a-z]{2}),\s+"
        r"(?P<month>[A-Z][a-z]{2})\s+"
        r"(?P<day>\d{1,2})\s+at\s+"
        r"(?P<hour>\d{1,2}):(?P<minute>\d{2})\s+"
        r"(?P<period>AM|PM)$",
        label.strip(),
    )
    if not match:
        return label

    weekday = _SR_WEEKDAYS.get(match.group("weekday"), match.group("weekday"))
    month = _SR_MONTHS.get(match.group("month"), match.group("month"))
    time_value = _sr_24h_time(
        match.group("hour"),
        match.group("minute"),
        match.group("period"),
    )
    return f"{weekday}, {int(match.group('day'))}. {month} u {time_value}"


def _sr_booking_translation(text: str) -> Optional[str]:
    if text == (
        "Of course. I can help schedule a meeting with 1PAX. What name "
        "should I put on the invite?"
    ):
        return (
            "Naravno. Mogu da pomognem da zakažemo sastanak sa 1PAX. "
            "Koje ime da stavim na pozivnicu?"
        )

    thanks_match = re.match(
        r"^Thanks, (?P<name>.+)\. What email address should Calendly send the invitation to\?$",
        text,
    )
    if thanks_match:
        return (
            f"Hvala, {thanks_match.group('name')}. Na koju email adresu Calendly "
            "treba da pošalje pozivnicu?"
        )

    if text == (
        "Great. When would you like to meet? You can say *tomorrow "
        "afternoon*, *next Tuesday morning*, or *any time next week*."
    ):
        return (
            "Odlično. Kada biste želeli da se nađemo? Možete reći "
            "*sutra popodne*, *sledećeg utorka pre podne*, ili "
            "*bilo kada sledeće nedelje*."
        )

    if text == (
        "What is the purpose of the meeting? A short note is enough, for "
        "example: project consultation, partnership, proposal, careers, "
        "press, or a general introduction."
    ):
        return (
            "Koja je svrha sastanka? Dovoljna je kratka napomena, na primer: "
            "konsultacija o projektu, partnerstvo, predlog, karijera, štampa "
            "ili opšte upoznavanje."
        )

    if text.startswith("I found these available times ("):
        lines = text.splitlines()
        header = re.match(r"^I found these available times \((?P<tz>.+)\):$", lines[0])
        if not header:
            return None
        translated_lines = [
            f"Pronašao sam sledeće slobodne termine ({header.group('tz')}):"
        ]
        for line in lines[1:]:
            slot_match = re.match(r"^(?P<num>\d+)\.\s+\*\*(?P<label>.+)\*\*$", line)
            if slot_match:
                translated_lines.append(
                    f"{slot_match.group('num')}. **{_sr_slot_label(slot_match.group('label'))}**"
                )
            elif not line.strip():
                translated_lines.append("")
            elif line == "Reply with a number, or tell me a different day/time.":
                translated_lines.append(
                    "Odgovorite brojem, ili mi recite drugi dan/vreme."
                )
            else:
                translated_lines.append(line)
        return "\n".join(translated_lines)

    confirm_match = re.match(
        r"^Perfect\. Should I book \*\*(?P<label>.+)\*\* for \*\*(?P<name>.+)\*\* "
        r"at \*\*(?P<email>.+)\*\*\?\s*(?:Purpose: \*\*(?P<purpose>.+)\*\*\s*)?"
        r"Reply yes to confirm, or no to cancel\.$",
        text,
    )
    if confirm_match:
        purpose = confirm_match.group("purpose")
        purpose_line = f"\n\nSvrha: **{purpose}**" if purpose else ""
        return (
            f"Savršeno. Da li da zakažem **{_sr_slot_label(confirm_match.group('label'))}** "
            f"za **{confirm_match.group('name')}** na **{confirm_match.group('email')}**? "
            f"{purpose_line}\n\n"
            "Odgovorite da za potvrdu, ili ne za otkazivanje."
        )

    def _sr_booking_success_line(line: str) -> Optional[str]:
        booked_match = re.match(r"^You're booked: \*\*(?P<label>.+)\*\*\.$", line)
        if booked_match:
            return f"Zakazano je: **{_sr_slot_label(booked_match.group('label'))}**."

        invitation_match = re.match(
            r"^Calendly will send the invitation to \*\*(?P<email>.+)\*\*\.$",
            line,
        )
        if invitation_match:
            return f"Calendly će poslati pozivnicu na **{invitation_match.group('email')}**."

        purpose_match = re.match(r"^Purpose: \*\*(?P<purpose>.+)\*\*\.$", line)
        if purpose_match:
            return f"Svrha: **{purpose_match.group('purpose')}**."

        link_match = re.match(r"^\[(?P<label>Reschedule|Cancel)\]\((?P<url>.+)\)$", line)
        if link_match:
            label = "Promeni termin" if link_match.group("label") == "Reschedule" else "Otkaži"
            return f"[{label}]({link_match.group('url')})"

        return None

    if text.startswith("You're booked:"):
        translated_blocks = []
        for block in text.split("\n\n"):
            translated_blocks.append(_sr_booking_success_line(block) or block)
        return "\n\n".join(translated_blocks)

    fallback_intro = (
        "Calendly needs the final confirmation on its booking page for this "
        "meeting. I prepared a pre-filled link with your details:"
    )

    def _sr_booking_fallback_block(block: str) -> Optional[str]:
        if block == fallback_intro:
            return (
                "Calendly zahteva konačnu potvrdu na svojoj stranici za zakazivanje. "
                "Pripremio sam unapred popunjen link sa vašim podacima:"
            )

        if block.startswith("[Finish booking in Calendly]("):
            return block.replace(
                "[Finish booking in Calendly]",
                "[Završite zakazivanje u Calendlyju]",
                1,
            )

        choose = re.match(r"^Choose \*\*(?P<label>.+)\*\* if it is still available\.$", block)
        if choose:
            return (
                f"Izaberite **{_sr_slot_label(choose.group('label'))}** "
                "ako je termin i dalje dostupan."
            )

        labeled = re.match(r"^(?P<label>Name|Email|Purpose): \*\*(?P<value>.+)\*\*$", block)
        if labeled:
            labels = {"Name": "Ime", "Email": "Email", "Purpose": "Svrha"}
            return f"{labels[labeled.group('label')]}: **{labeled.group('value')}**"

        return None

    if text.startswith(fallback_intro):
        return "\n\n".join(
            _sr_booking_fallback_block(block) or block for block in text.split("\n\n")
        )

    exact = {
        "No problem. I will leave the meeting scheduling there.": (
            "Nema problema. Zaustaviću zakazivanje sastanka ovde."
        ),
        "I did not catch which time you wanted. Please reply with one of the numbers, or tell me another day/time.": (
            "Nisam razumeo koji termin želite. Odgovorite jednim od brojeva, "
            "ili mi recite drugi dan/vreme."
        ),
        "Please reply yes to book that time, or no to cancel.": (
            "Odgovorite da za zakazivanje tog termina, ili ne za otkazivanje."
        ),
        "I lost the selected time. Let me show the available slots again.": (
            "Izgubio sam izabrani termin. Prikazaću slobodne termine ponovo."
        ),
        "Calendly could not complete the booking right now. Please choose another time, or try again shortly.": (
            "Calendly trenutno ne može da završi zakazivanje. Izaberite drugi "
            "termin ili pokušajte ponovo uskoro."
        ),
        "I could not find open Calendly times in that window. Try another option, like *tomorrow morning* or *next week*.": (
            "Nisam pronašao slobodne Calendly termine u tom periodu. Probajte "
            "drugu opciju, na primer *sutra pre podne* ili *sledeće nedelje*."
        ),
        "I could not find times in that exact part of the day, but these nearby options are open.": (
            "Nisam pronašao termine baš u tom delu dana, ali ovi obližnji "
            "termini su slobodni."
        ),
    }
    if text in exact:
        return exact[text]

    if text == "Name:":
        return "Ime:"
    if text == "Email:":
        return "Email:"
    if text == "Purpose:":
        return "Svrha:"

    if text.startswith("[Finish booking in Calendly]("):
        return text.replace("[Finish booking in Calendly]", "[Završite zakazivanje u Calendlyju]", 1)

    choose_match = re.match(r"^Choose \*\*(?P<label>.+)\*\* if it is still available\.$", text)
    if choose_match:
        return (
            f"Izaberite **{_sr_slot_label(choose_match.group('label'))}** "
            "ako je termin i dalje dostupan."
        )

    labeled_match = re.match(r"^(?P<label>Name|Email|Purpose): \*\*(?P<value>.+)\*\*$", text)
    if labeled_match:
        labels = {"Name": "Ime", "Email": "Email", "Purpose": "Svrha"}
        return f"{labels[labeled_match.group('label')]}: **{labeled_match.group('value')}**"

    if text.startswith("Calendly could not be reached right now. Please try again shortly."):
        return (
            "Calendly trenutno nije dostupan. Pokušajte ponovo uskoro."
        )

    return None


def _static_translation(text: str, lang: Optional[str]) -> Optional[str]:
    normalized = _normalized_lang(lang)
    if normalized == "SR":
        booking = _sr_booking_translation(text)
        if booking:
            return booking
        if (
            text.startswith("**1. Airports & Railstations**")
            and "**8. BIM Project Management**" in text
        ):
            return (
                "**1. Aerodromi i železničke stanice** — Programiranje terminala, dizajn protoka, "
                "BHS izvodljivost, multimodalni čvorovi, protivpožarna sigurnost i dizajn stanica.\n\n"
                "**2. Urbanizam i master plan** — Strategija razvoja, planiranje aerodromskog grada, "
                "simulacija saobraćaja, faziranje izgradnje i bezbednosne revizije.\n\n"
                "**3. Inovacije i patenti** — Patentirani sistemi kolica i nameštaja, licenciranje, "
                "savetovanje o putničkom iskustvu i komercijalno uvođenje vlasničkih inovacija.\n\n"
                "**4. Budućnost mobilnosti** — Dizajn vertiportova i eVTOL objekata, urbani čvorovi "
                "mobilnosti, MaaS integracija i savetovanje za pametne gradove.\n\n"
                "**5. Kontrolni tornjevi i prateći objekti** — Izbor lokacije ATCT-a, analiza vidljivosti, "
                "opremanje kontrolne sobe i dizajn pratećih objekata.\n\n"
                "**6. Enterijer i maloprodaja** — Smernice za putničko iskustvo, komercijalna strategija, "
                "maloprodajni koncept \"Crvena nit\", signalizacija i dizajn nameštaja.\n\n"
                "**7. Rad i život** — Kancelarije, ambasade, objekti mešovite namene, tržni centri, "
                "odmarališta i projekti urbane regeneracije.\n\n"
                "**8. BIM upravljanje projektima** — Revit modelovanje, detekcija kolizija, digitalni blizanci, "
                "BIM savetovanje i isporuka radnih paketa."
            )
        if (
            text.startswith("**Leadership**\nMabel Miranda")
            and "**Collaborators**" in text
        ):
            return (
                "**Rukovodstvo**\n"
                "Mabel Miranda · CEO i osnivač  |  Ali Fawaz · frakcioni CFO  |  "
                "Fabiola Espinoza · poslovni razvoj  |  Bashan Yang · Šangaj i vizualizacija  |  "
                "Carla Miranda · komunikacije i inovacije\n\n"
                "**Arhitekte** (13)\n"
                "Claudia Cornejo · Hanh Nguyen · Pedro Martins Branco · Marija Stevanovic · Boris Stojnic · "
                "Diego Alonso Ampuero · Marko Soskic · Renzo Roncalla · Kevin Guzman · Yeniffer Cordero · "
                "Wendy Florian · Deysi Nuñez · Maria Fernanda Bojorquez\n\n"
                "**Specijalisti**\n"
                "Tiago Cobrado · arhitektonski tehnolog  |  Matija Leković · AI i digitalni specijalista\n\n"
                "**Operacije studija**\n"
                "Andreja Zrnovic · dizajn i komunikacije  |  Olenka Tamara · administrativni asistent\n\n"
                "**Saradnici**\n"
                "Helene Henriot · planer aerodroma  |  Christos Panagos · arhitekta i stručnjak za 3D vizualizaciju"
            )
        exact = {
            (
                "**1PAX offers eight core service areas**, spanning the full lifecycle of "
                "mobility infrastructure and architectural projects:"
            ): (
                "**1PAX nudi osam ključnih oblasti usluga**, koje pokrivaju ceo životni ciklus "
                "infrastrukture mobilnosti i arhitektonskih projekata:"
            ),
            (
                "**The 1PAX team** brings together architects, planners, engineers, BIM specialists, "
                "visualization experts, and innovators — based in Paris, Belgrade, Shanghai, Barcelona, and Lima."
            ): (
                "**1PAX tim** okuplja arhitekte, planere, inženjere, BIM stručnjake, "
                "eksperte za vizualizaciju i inovatore — sa bazama u Parizu, Beogradu, "
                "Šangaju, Barseloni i Limi."
            ),
            (
                "Want to know more about a specific person or group? Ask — for example: "
                "*\"Tell me about Mabel Miranda\"*, *\"Who are the architects?\"*, or *\"Who handles BIM?\"*"
            ): (
                "Želite da saznate više o određenoj osobi ili grupi? Pitajte, na primer: "
                "*\"Recite mi nešto o Mabel Mirandi\"*, *\"Ko su arhitekte?\"*, ili *\"Ko vodi BIM?\"*"
            ),
        }
        return exact.get(text)
    return None


def _looks_untranslated(source: str, translated: str, lang: Optional[str]) -> bool:
    normalized = _normalized_lang(lang)
    if not normalized or normalized.startswith("EN"):
        return False

    source_clean = " ".join(source.split()).casefold()
    translated_clean = " ".join(translated.split()).casefold()
    if not source_clean or not translated_clean:
        return True
    if source_clean == translated_clean and any(marker in f" {source_clean} " for marker in _ENGLISH_MARKERS):
        return True
    return False


def _proxy_translate_response(text: str, lang: str) -> Optional[str]:
    """Use the local translation proxy when the action server needs output translation."""
    if not _TRANSLATE_PROXY_URL:
        return None

    body = {
        "text": text,
        "target_lang": lang,
    }
    req = urllib.request.Request(
        _TRANSLATE_PROXY_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=12.0) as resp:
            result = json.loads(resp.read())
    except (
        TimeoutError,
        socket.timeout,
        urllib.error.URLError,
        urllib.error.HTTPError,
        OSError,
        KeyError,
        ValueError,
    ) as exc:
        logger.warning("Local translation proxy unavailable: %s", exc)
        return None

    if result.get("translation_failed") or not result.get("translation_enabled", True):
        return None
    translated = (result.get("text") or "").strip()
    if translated and not _looks_untranslated(text, translated, lang):
        return translated
    return None


def translate_response(text: str, lang: Optional[str]) -> str:
    """
    Translate an English response string to the target language.
    Returns the original text unchanged when lang is None/English. For selected
    non-English languages, fail closed with a localized fallback instead of
    leaking English if the translation backend is unavailable.
    Gemini preserves Markdown (*bold*, _italic_, bullet lists).
    """
    normalized = _normalized_lang(lang)
    if not normalized or normalized.startswith("EN"):
        return text

    static = _static_translation(text, normalized)
    if static:
        return static

    translated = _proxy_translate_response(text, normalized)
    if translated:
        return translated

    lang_name = _LANG_NAMES.get(normalized, normalized)
    translated = _gemini_call(
        prompt=f"Translate to {lang_name}: {text}",
        system_instruction=(
            "You are a translator. Output ONLY the translated text. "
            "Preserve all Markdown formatting exactly (bold **, bullets •, hyphens -, etc.). "
            "Preserve Markdown links and URLs exactly; translate link labels only. "
            "No explanations, no quotes, no notes."
        ),
        timeout=8.0,
        attempts=1,
    )
    if translated and not _looks_untranslated(text, translated, normalized):
        return translated

    logger.error("Response translation unavailable for %s; suppressing English fallback.", normalized)
    return _translation_failure_text(normalized)
