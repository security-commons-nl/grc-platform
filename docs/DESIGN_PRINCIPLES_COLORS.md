# IMS Kleurprincipes - Deadline Visualisatie

## Kernprincipe

**Alle deadlines in het platform volgen hetzelfde kleurensysteem:**

| Status | Kleur | Conditie |
|--------|-------|----------|
| OK / Normaal | Groen of geen kleur | Meer dan 30 dagen tot deadline |
| Nadert | **Oranje** | Minder dan 30 dagen tot deadline |
| Verlopen | **Rood** | Deadline is gepasseerd |

## Waarom dit principe?

1. **Consistentie** - Gebruikers leren één systeem, toepasbaar overal
2. **Snelle herkenning** - Oranje = actie nodig, Rood = te laat
3. **Prioritering** - Dashboard kan items sorteren op urgentie
4. **Proactief** - 30 dagen geeft voldoende tijd om te reageren

## Toepassing per Entity

### Beleid (Policy)
| Veld | Beschrijving |
|------|--------------|
| `review_date` | Wanneer beleid herzien moet worden |
| `expiration_date` | Wanneer beleid verloopt |

**Logica:**
- Oranje: `review_date` of `expiration_date` binnen 30 dagen
- Rood: `review_date` of `expiration_date` is verstreken

### Risico's (Risk)
| Veld | Beschrijving |
|------|--------------|
| `next_review_date` | Volgende geplande risico-review |

**Logica:**
- Oranje: `next_review_date` binnen 30 dagen
- Rood: `next_review_date` is verstreken

### Maatregelen (Measure)
| Veld | Beschrijving |
|------|--------------|
| `deadline` | Implementatie deadline |
| `last_tested` + testfrequentie | Wanneer opnieuw testen |

**Logica:**
- Oranje: `deadline` binnen 30 dagen
- Rood: `deadline` is verstreken en status != "Implemented"

### Assessments
| Veld | Beschrijving |
|------|--------------|
| `planned_end_date` | Geplande einddatum |
| `deadline` | Harde deadline |

**Logica:**
- Oranje: `planned_end_date` of `deadline` binnen 30 dagen
- Rood: Deadline verstreken en status != "Completed"

### Corrigerende Acties (CorrectiveAction)
| Veld | Beschrijving |
|------|--------------|
| `deadline` | Deadline voor afronding |

**Logica:**
- Oranje: `deadline` binnen 30 dagen
- Rood: `deadline` verstreken en status != "Completed"

### Bevindingen (Finding)
| Veld | Beschrijving |
|------|--------------|
| `due_date` | Wanneer opgelost moet zijn |

**Logica:**
- Oranje: `due_date` binnen 30 dagen
- Rood: `due_date` verstreken en status != "Resolved"

### Uitzonderingen (Exception/Waiver)
| Veld | Beschrijving |
|------|--------------|
| `expiration_date` | Wanneer uitzondering verloopt |

**Logica:**
- Oranje: `expiration_date` binnen 30 dagen
- Rood: `expiration_date` verstreken (uitzondering niet meer geldig!)

### Leveranciers (Supplier/Scope)
| Veld | Beschrijving |
|------|--------------|
| `contract_end_date` | Wanneer contract afloopt |

**Logica:**
- Oranje: `contract_end_date` binnen 30 dagen
- Rood: Contract verlopen zonder verlenging

### Verwerkingsactiviteiten (ProcessingActivity - AVG)
| Veld | Beschrijving |
|------|--------------|
| `next_review_date` | Volgende DPIA/review |
| `retention_period` | Data moet vernietigd worden |

### Continuiteitsplannen (ContinuityPlan)
| Veld | Beschrijving |
|------|--------------|
| `next_review_date` | Volgende review |
| `next_test_date` | Volgende test |

## Implementatie in Frontend

### Utility Functie
```python
from datetime import datetime, timedelta

def get_deadline_status(deadline_date: datetime | None) -> str:
    """
    Returns: 'normal', 'warning', 'danger'
    """
    if not deadline_date:
        return 'normal'

    now = datetime.utcnow()
    days_until = (deadline_date - now).days

    if days_until < 0:
        return 'danger'  # Rood - verlopen
    elif days_until <= 30:
        return 'warning'  # Oranje - nadert
    else:
        return 'normal'  # Groen/neutraal
```

### Reflex Component
```python
def deadline_badge(date_value: rx.Var, label: str = "") -> rx.Component:
    """Badge die automatisch kleurt op basis van deadline."""
    return rx.cond(
        date_value,
        rx.match(
            get_deadline_status_var(date_value),
            ("danger", rx.badge(label, color_scheme="red", variant="solid")),
            ("warning", rx.badge(label, color_scheme="orange", variant="solid")),
            rx.badge(label, color_scheme="green", variant="soft"),
        ),
        rx.fragment(),  # Geen badge als geen datum
    )
```

### CSS Klassen
```css
.deadline-normal { }  /* Geen speciale styling */
.deadline-warning {
    background-color: var(--orange-a3);
    border-left: 3px solid var(--orange-9);
}
.deadline-danger {
    background-color: var(--red-a3);
    border-left: 3px solid var(--red-9);
}
```

## Dashboard Integratie

### "Actie Vereist" Widget
Het dashboard toont een overzicht van alle items die aandacht nodig hebben:

```
┌─────────────────────────────────────────────┐
│ ⚠️ Actie Vereist                            │
├─────────────────────────────────────────────┤
│ 🔴 3 items verlopen                         │
│    • Beleid "Toegangsbeheer" (5 dagen)      │
│    • Risk Review "IT-infra" (2 dagen)       │
│    • Assessment DPIA (10 dagen)             │
├─────────────────────────────────────────────┤
│ 🟠 7 items naderen deadline                 │
│    • Beleid "Privacy" (12 dagen)            │
│    • Maatregel M-042 (18 dagen)             │
│    • ...meer                                │
└─────────────────────────────────────────────┘
```

### Sortering
Items worden gesorteerd op urgentie:
1. Rood (verlopen) - meest urgent bovenaan
2. Oranje (< 30 dagen)
3. Normaal

## Configuratie (Toekomstig)

In een latere fase kan de 30-dagen drempel configureerbaar worden per tenant:

```python
class TenantSettings:
    deadline_warning_days: int = 30  # Default 30 dagen
    deadline_critical_days: int = 7   # Extra urgentie bij < 7 dagen?
```

## Gerelateerde Modellen

Het `ReviewSchedule` model ondersteunt dit systeem al:
- `next_review: datetime` - De deadline
- `reminder_days_before: int = 14` - Extra herinnering
- `frequency_months: int` - Automatische herberekening

## Notificaties (Toekomstig)

Het `Notification` model kan automatisch notificaties sturen:
- 30 dagen vooraf: "Beleid X nadert review datum"
- Op deadline: "Beleid X review is vandaag"
- Na deadline: "Beleid X review is verlopen"
