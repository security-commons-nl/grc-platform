# UI

> **Navigation aid.** Component inventory and prop signatures extracted via AST. Read the source files before adding props or modifying component logic.

**32 components** (react)

## Client Components

- **GebruikersPage** — `frontend\src\app\(protected)\admin\gebruikers\page.tsx`
- **TenantPage** — `frontend\src\app\(protected)\admin\tenant\page.tsx`
- **AssessmentsPage** — `frontend\src\app\(protected)\beheer\assessments\page.tsx`
- **BevindingenPage** — `frontend\src\app\(protected)\beheer\bevindingen\page.tsx`
- **BewijsPage** — `frontend\src\app\(protected)\beheer\bewijs\page.tsx`
- **ControlsPage** — `frontend\src\app\(protected)\beheer\controls\page.tsx`
- **IncidentenPage** — `frontend\src\app\(protected)\beheer\incidenten\page.tsx`
- **BeheerDashboardPage** — `frontend\src\app\(protected)\beheer\page.tsx`
- **RisicosPage** — `frontend\src\app\(protected)\beheer\risicos\page.tsx`
- **BesluitenPage** — `frontend\src\app\(protected)\inrichten\besluiten\page.tsx`
- **DocumentenPage** — `frontend\src\app\(protected)\inrichten\documenten\page.tsx`
- **InrichtenOverzichtPage** — `frontend\src\app\(protected)\inrichten\page.tsx`
- **StepDetailPage** — props: params — `frontend\src\app\(protected)\inrichten\[stepId]\page.tsx`
- **ProtectedLayout** — `frontend\src\app\(protected)\layout.tsx`
- **LoginPage** — `frontend\src\app\login\page.tsx`
- **RootPage** — `frontend\src\app\page.tsx`
- **ChatIsland** — props: stepNumber, executionId — `frontend\src\components\ai\chat-island.tsx`
- **ChatPanel** — props: conversation, onClose, onUpdate — `frontend\src\components\ai\chat-panel.tsx`
- **RiskMatrix** — props: mode, value — `frontend\src\components\beheer\risk-matrix.tsx`
- **DecisionLogTable** — props: decisions — `frontend\src\components\inrichten\decision-log-table.tsx`
- **DocumentVersionList** — props: documents — `frontend\src\components\inrichten\document-version-list.tsx`
- **StepCard** — props: step, execution, isBlocked, onClick — `frontend\src\components\inrichten\step-card.tsx`
- **StepProgressGrid** — props: steps, executions, dependencies — `frontend\src\components\inrichten\step-progress-grid.tsx`
- **Header** — props: title — `frontend\src\components\layout\header.tsx`
- **AuthProvider** — `frontend\src\providers\auth-provider.tsx`

## Components

- **RootLayout** — `frontend\src\app\layout.tsx`
- **PageWrapper** — props: title, description, actions — `frontend\src\components\layout\page-wrapper.tsx`
- **ScoreBar** — props: value, label, size — `frontend\src\components\shared\score-bar.tsx`
- **StatusBadge** — props: status — `frontend\src\components\shared\status-badge.tsx`
- **WaaromTooltip** — props: text — `frontend\src\components\shared\waarom-tooltip.tsx`
- **EmptyState** — props: icon, title, description, actionLabel, onAction — `frontend\src\components\ui\empty-state.tsx`
- **LoadingSkeleton** — props: className, lines — `frontend\src\components\ui\loading-skeleton.tsx`

---
_Back to [overview.md](./overview.md)_