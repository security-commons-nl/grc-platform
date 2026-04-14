# Dependency Graph

## Most Imported Files (change these carefully)

- `frontend\src\lib\hooks\use-api.ts` — imported by **4** files
- `frontend\src\components\inrichten\step-card.tsx` — imported by **1** files
- `frontend\src\components\ui\button.tsx` — imported by **1** files
- `frontend\src\lib\auth.ts` — imported by **1** files
- `frontend\src\lib\constants.ts` — imported by **1** files
- `frontend\src\lib\api-types.ts` — imported by **1** files

## Import Map (who imports what)

- `frontend\src\lib\hooks\use-api.ts` ← `frontend\src\lib\hooks\use-controls.ts`, `frontend\src\lib\hooks\use-risks.ts`, `frontend\src\lib\hooks\use-scores.ts`, `frontend\src\lib\hooks\use-steps.ts`
- `frontend\src\components\inrichten\step-card.tsx` ← `frontend\src\components\inrichten\step-progress-grid.tsx`
- `frontend\src\components\ui\button.tsx` ← `frontend\src\components\ui\empty-state.tsx`
- `frontend\src\lib\auth.ts` ← `frontend\src\lib\api-client.ts`
- `frontend\src\lib\constants.ts` ← `frontend\src\lib\api-client.ts`
- `frontend\src\lib\api-types.ts` ← `frontend\src\lib\auth.ts`
