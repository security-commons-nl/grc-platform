"""EU AI Act risicoclassificatie-helper (verordening 2024/1689).

Suggereert een risicoclassificatie op basis van system_type en een korte
beschrijving van het gebruiksdoel. Output is **advies** — de uiteindelijke
classificatie blijft een verantwoordelijkheid van de organisatie en moet
door een menselijke beoordelaar worden bevestigd (zie AI HITL-checkpoints).

Regels gebaseerd op:
- EU AI Act art. 5 (verboden praktijken)
- EU AI Act bijlage III (hoog-risico gebruikssituaties)
- EU AI Act art. 50 (transparantie-eisen voor beperkt risico)

Deze classifier doet expliciet GEEN LLM-call — de regels zijn deterministisch
en uitlegbaar zodat de suggestie zelf auditeerbaar is.
"""

from dataclasses import dataclass
from typing import Literal


RiskLevel = Literal["unacceptable", "high", "limited", "minimal", "not_classified"]


@dataclass(frozen=True)
class ClassificationSuggestion:
    suggested_risk: RiskLevel
    reasoning: str
    triggered_by: list[str]  # welke regels dit advies trokken


# ─────────────────────────────────────────────────────────────────────────
# Keyword-indicatoren per risicocategorie. Bewust simpel — wijzig vooral
# de keywords (niet de logica) als verdere domeinen toegevoegd moeten.
# ─────────────────────────────────────────────────────────────────────────

UNACCEPTABLE_KEYWORDS = [
    # Art. 5(1)(a) — subliminaal manipuleren
    "subliminaal", "manipulatie van gedrag", "psychologische manipulatie",
    # Art. 5(1)(b) — kwetsbaarheden uitbuiten
    "uitbuit kwetsbaarheid", "uitbuit minderjarig",
    # Art. 5(1)(c) — social scoring
    "social score", "burgerscore", "social credit",
    # Art. 5(1)(d) — realtime gezichtsherkenning openbare ruimte
    "realtime gezichtsherkenning openbare", "live facial recognition",
    # Art. 5(1)(e) — predictive policing op individu-niveau
    "predictive policing op individu",
]

HIGH_RISK_KEYWORDS = [
    # Bijlage III(1) — kritieke infrastructuur
    "kritieke infrastructuur", "energienet", "drinkwater", "verkeersregeling",
    # Bijlage III(2) — onderwijs (toelating, beoordeling)
    "toelating opleiding", "examen beoordeling", "studievoortgang automatisch",
    # Bijlage III(3) — werkgelegenheid (sollicitatie, performance)
    "werving", "sollicitant", "ontslagbeslissing", "performance management automatisch",
    # Bijlage III(4) — toegang tot essentiële diensten (uitkering, krediet)
    "uitkering toekennen", "bijstand beslissing", "krediet beoordeling",
    "kredietwaardigheid", "fraude detectie uitkering",
    # Bijlage III(5) — rechtshandhaving
    "risico-analyse strafrecht", "polygrap", "bewijswaarde",
    # Bijlage III(6) — migratie en asiel
    "asielaanvraag", "visumbeoordeling", "grenscontrole automatisch",
    # Bijlage III(7) — rechtspraak
    "rechterlijk advies", "uitspraak ondersteuning",
    # Bijlage III(8) — democratisch proces
    "verkiezingsbeïnvloeding", "kiesgedrag",
]

LIMITED_RISK_KEYWORDS = [
    # Art. 50 — transparantie-eisen
    "chatbot", "klantcontact", "deepfake", "synthetische media",
    "emotieherkenning",  # in non-werkplek context = limited; werkplek = high
    "biometrische categorisatie",
]


# System-type ↔ default risico (initiële inschatting vóór keyword-check)
SYSTEM_TYPE_DEFAULTS: dict[str, RiskLevel] = {
    "chatbot": "limited",            # Art. 50 transparantie-eis
    "content_generation": "limited", # Art. 50 transparantie-eis (synthetische content)
    "decision_support": "limited",   # afhankelijk van domein — vaak high
    "classification": "limited",     # afhankelijk van toepassing
    "monitoring": "limited",
    "automation": "minimal",
    "other": "not_classified",
}


def suggest_risk(
    system_type: str,
    description: str = "",
    use_case: str = "",
) -> ClassificationSuggestion:
    """Suggereer een EU AI Act-risicocategorie op basis van keyword-matching.

    Args:
        system_type: een van de SYSTEM_TYPE_DEFAULTS keys
        description: vrije tekst — wordt gescand op risico-indicatoren
        use_case: vrije tekst — beoogd gebruiksdoel

    Returns:
        ClassificationSuggestion met advies + uitleg + welke regels triggerden
    """
    combined_text = f"{description} {use_case}".lower()
    triggered = []

    # 1. Onaanvaardbaar risico — overstemt alles
    for kw in UNACCEPTABLE_KEYWORDS:
        if kw in combined_text:
            triggered.append(f"unacceptable: '{kw}'")
    if triggered:
        return ClassificationSuggestion(
            suggested_risk="unacceptable",
            reasoning=(
                "Het beschreven gebruik valt onder EU AI Act art. 5 (verboden "
                "praktijken). Dit systeem mag in de EU niet worden ingezet. "
                "Heroverweeg het gebruiksdoel of staak de inzet."
            ),
            triggered_by=triggered,
        )

    # 2. Hoog risico — bijlage III
    for kw in HIGH_RISK_KEYWORDS:
        if kw in combined_text:
            triggered.append(f"high: '{kw}'")
    if triggered:
        return ClassificationSuggestion(
            suggested_risk="high",
            reasoning=(
                "Het beschreven gebruik valt mogelijk onder bijlage III van de "
                "EU AI Act (hoog-risicogebruik). Conformiteitsbeoordeling "
                "vereist vóór ingebruikname; menselijk toezicht verplicht "
                "(art. 14); registratie in de EU AI-database."
            ),
            triggered_by=triggered,
        )

    # 3. Beperkt risico — transparantie-eisen
    for kw in LIMITED_RISK_KEYWORDS:
        if kw in combined_text:
            triggered.append(f"limited: '{kw}'")
    if triggered:
        return ClassificationSuggestion(
            suggested_risk="limited",
            reasoning=(
                "Het systeem heeft transparantie-eisen op grond van art. 50 "
                "EU AI Act (informeer gebruikers dat ze met AI interacteren "
                "of dat content synthetisch is)."
            ),
            triggered_by=triggered,
        )

    # 4. Fallback op system_type default
    default = SYSTEM_TYPE_DEFAULTS.get(system_type, "not_classified")
    if default == "not_classified":
        reasoning = (
            "Onvoldoende informatie om automatisch te classificeren. Beoordeel "
            "handmatig op basis van bijlage III EU AI Act en de criteria in "
            "docs/eu-ai-act-classification.md."
        )
        triggered.append(f"system_type='{system_type}' has no default mapping")
    else:
        reasoning = (
            f"Geen specifieke risico-indicatoren in beschrijving gevonden. "
            f"Default-classificatie voor system_type='{system_type}' is "
            f"'{default}'. Verifieer handmatig of dit klopt voor het concrete "
            f"gebruiksdoel."
        )
        triggered.append(f"default for system_type='{system_type}'")

    return ClassificationSuggestion(
        suggested_risk=default,
        reasoning=reasoning,
        triggered_by=triggered,
    )
