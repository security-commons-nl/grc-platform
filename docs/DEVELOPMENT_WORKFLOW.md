# Werkwijze Beheer en Ontwikkeling

Dit document beschrijft de werkwijze voor beheer en ontwikkeling van het IMS project.

## Versiebeheer Principes

### Elke wijziging wordt gecommit

**Regel:** Elke wijziging aan code of documentatie wordt direct gecommit en gepusht naar de remote repository.

**Werkwijze:**
1. Wijziging maken (Edit/Write)
2. `git add` - gewijzigde bestanden stagen
3. `git commit` - met beschrijvende commit message
4. `git push` - direct naar remote pushen

**Rationale:**
- Volledige traceerbaarheid van alle wijzigingen
- Geen verlies van werk bij lokale problemen
- Directe synchronisatie met remote repository
- Kleine, atomaire commits zijn makkelijker te reviewen en te reverten

### Commit Message Conventies

Gebruik conventionele commit messages:
- `feat:` - nieuwe functionaliteit
- `fix:` - bugfix
- `docs:` - documentatie wijzigingen
- `refactor:` - code refactoring zonder functionele wijziging
- `style:` - formatting, whitespace
- `test:` - toevoegen of aanpassen van tests
- `chore:` - overige taken (dependencies, config)

### Branch Strategie

- `main` - stabiele hoofdbranch
- Feature branches voor grotere wijzigingen (optioneel)

## AI-Assisted Development

Bij gebruik van Claude Code (of vergelijkbare AI tools):
- AI commit en pusht elke wijziging automatisch
- Gebruiker behoudt controle via code review op remote
- Kleine commits maken rollback eenvoudig indien nodig
