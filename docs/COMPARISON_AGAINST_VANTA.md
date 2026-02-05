# Vergelijking IMS vs. Vanta

Dit document biedt een gedetailleerde vergelijking tussen **IMS** (Integrated Management System - deze repository) en **Vanta**, de marktleider in geautomatiseerde compliance software.

Hoewel beide tools organisaties helpen bij het behalen van frameworks zoals ISO 27001 en SOC 2, verschillen ze fundamenteel in filosofie, doelgroep en technische aanpak.

## 1. Executive Summary

| Kenmerk | IMS (Deze Repo) | Vanta |
| :--- | :--- | :--- |
| **Type** | **Open Source / Self-Hosted** | **Closed Source SaaS** |
| **Primaire Doelgroep** | Enterprise, Overheid, SSC's & Organisaties met hoge privacy-eisen. | Cloud-native Startups & Scale-ups. |
| **Filosofie** | **"AI First & Data Sovereignty".** Controle over data, lokale AI, en procesondersteuning. | **"Continuous Compliance".** Automatisering van controles via API-koppelingen. |
| **Integraties** | **Enterprise ITSM & Architectuur:** ServiceNow, Topdesk, BlueDolphin, Proquro. | **Cloud Infra & SaaS:** AWS, GCP, Azure, GitHub, Google Workspace, Slack. |
| **AI Aanpak** | **Transparant & Lokaal:** Gebruik van Local LLM's (Mistral) voor data privacy. AI helpt *schrijven* en *analyseren*. | **Proprietary:** "Magic" features in de cloud. AI helpt voornamelijk bij vragenlijsten. |
| **Data Locatie** | On-premise / Eigen Cloud (Data verlaat de organisatie niet). | Vanta Cloud (VS/EU servers, maar data wordt verwerkt door derde partij). |

---

## 2. Diepte-analyse Vanta

**Wat is Vanta?**
Vanta is een SaaS-platform dat gespecialiseerd is in "Automated Evidence Collection". Het verbindt direct met je cloud-infrastructuur (bijv. AWS) en HR-systemen om continu te monitoren of instellingen correct staan (bijv. "Staat MFA aan?", "Zijn alle laptops versleuteld?").

**Sterke Punten:**
*   **Snelheid:** Voor een cloud-native startup (zonder legacy) kan Vanta binnen enkele weken leiden tot audit-readiness.
*   **Automated Monitors:** Honderden pre-built checks die continu draaien. Als een instelling wijzigt, krijg je direct een alert.
*   **Trust Report:** Een publieke pagina waar klanten live de security-status kunnen zien.

**Overwegingen:**
*   **SaaS-Only:** Gevoelige data (metadata van je infrastructuur, persoonsgegevens medewerkers) wordt gesynchroniseerd naar Vanta servers. Voor sommige overheidsinstellingen of strenge enterprises is dit een no-go.
*   **Cost:** Prijsmodel per medewerker kan snel oplopen voor grotere organisaties.
*   **Blackbox:** Je kunt de logica van de monitors niet aanpassen of inzien (closed source).
*   **Beperkte Enterprise Integraties:** Minder focus op traditionele on-premise tools of specifieke ITSM-processen (ServiceNow/Topdesk).

## 3. Diepte-analyse IMS

**Wat is IMS?**
IMS is een "AI First" GRC-platform dat ontworpen is om volledige controle te bieden over het compliance-proces. Het is niet alleen een monitor-tool, maar een compleet beheersysteem voor ISMS (Security), PIMS (Privacy) en BCMS (Continuïteit), met een focus op soevereiniteit en lokale AI-integratie.

**Sterke Punten:**
*   **Data Souvereiniteit:** Alles draait op de eigen infrastructuur. Er is geen vendor lock-in en geen data-lek naar externe AI-providers (dankzij Local LLM ondersteuning).
*   **Enterprise Integraties:** Out-of-the-box koppelingen met **Topdesk**, **ServiceNow**, **BlueDolphin** en **Proquro**. Dit maakt het geschikt voor hybride omgevingen waar niet alles in AWS draait.
*   **Brede Scope:** Naast security (ISO27001) diepe ondersteuning voor AVG/Privacy (Verwerkingsregister, DPIA's) en Business Continuity.
*   **AI Assistentie:** AI wordt gebruikt om beleid te genereren, risico's te analyseren en mappingen voor te stellen, niet alleen om vinkjes te zetten.

**Overwegingen:**
*   **Setup Tijd:** Vereist installatie en configuratie (Docker/Kubernetes), in tegenstelling tot "inloggen en koppelen" bij Vanta.
*   **Minder "Cloud Monitors":** IMS heeft minder out-of-the-box checks voor specifieke AWS-instellingen (zoals S3 bucket encryption) dan Vanta. De focus ligt meer op procesbeheersing.

## 4. Kernverschil: Benadering van Evidence

Het grootste verschil zit in *hoe* bewijslast wordt verzameld:

*   **Vanta (Technische Validatie):** Vanta kijkt naar de **staat** van een systeem.
    *   *Check:* "Is poort 22 open op AWS instance X?" -> *Nee?* -> *Pass.*
    *   *Geschikt voor:* Technische teams die hun cloud-omgeving beheren.

*   **IMS (Proces Validatie):** IMS kijkt naar het **proces** en de **registratie**.
    *   *Check:* "Is er een goedgekeurd wijzigingsverzoek in ServiceNow voor deze firewall change?" -> *Ja?* -> *Pass.*
    *   *Geschikt voor:* Organisaties met formele ITIL-processen (Change/Incident Management).

## 5. Conclusie

**Kies voor Vanta als:**
Je een moderne, cloud-native startup of scale-up bent die zo snel en pijnloos mogelijk een SOC 2 of ISO 27001 certificering wil halen, en je geen bezwaar hebt tegen het delen van metadata met een Amerikaanse SaaS-provider.

**Kies voor IMS als:**
Je een (overheids)organisatie, enterprise of SSC bent die:
1.  **Volledige controle** over data en AI vereist (geen SaaS).
2.  Werkt met **Enterprise Service Management** tools zoals Topdesk of ServiceNow.
3.  Een breed **geïntegreerd beeld** wil van Security, Privacy én Continuïteit.
4.  Niet wil betalen per medewerker, maar investeert in eigen beheer.
