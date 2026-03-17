"""
Seed Data for IMS Development and Testing.
Run: python -m app.seed_data
"""
import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.core_models import (
    # Base
    Tenant, User, TenantUser,
    # Governance
    Standard, Requirement, Policy, PolicyState, FrameworkType,
    # Scope
    Scope, ScopeType, ClassificationLevel, AssetType,
    # Risk
    Risk, Measure, RiskLevel, Status, AttentionQuadrant, MitigationApproach,
    # Compliance
    ApplicabilityStatement, ImplementationStatus, CoverageType,
    # Assessment
    Assessment, AssessmentType, Finding, FindingSeverity, Evidence, CorrectiveAction,
    AssessmentQuestion, QuestionType, BIAThreshold,
    # Privacy
    ProcessingActivity, LegalBasis,
    # Continuity
    ContinuityPlan, ContinuityTest, AuditResult, PlanType, TestType,
    # RBAC
    UserScopeRole, Role,
    # Workflow
    WorkflowDefinition, WorkflowState, WorkflowTransition,
    # Organization Profile
    OrganizationProfile,
)


async def seed_database():
    """Seed the database with initial data."""
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session() as session:
        # =========================================================================
        # TENANT
        # =========================================================================
        tenant = Tenant(
            name="Demo Organisatie",
            slug="demo",
            display_name="Demo tenant voor ontwikkeling en testen",
            settings=json.dumps({"theme": "light", "locale": "nl"}),
            is_active=True,
        )
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
        print(f"Created tenant: {tenant.name} (ID: {tenant.id})")

        # =========================================================================
        # USERS
        # =========================================================================
        password_hash = get_password_hash(settings.DEFAULT_ADMIN_PASSWORD)

        users_data = [
            {"username": "admin", "email": "admin@demo.local", "full_name": "Systeem Beheerder", "is_superuser": True},
            {"username": "ciso", "email": "ciso@demo.local", "full_name": "Chief Information Security Officer", "is_superuser": False},
            {"username": "fg", "email": "fg@demo.local", "full_name": "Functionaris Gegevensbescherming", "is_superuser": False},
            {"username": "proceseigenaar", "email": "pe@demo.local", "full_name": "Proces Eigenaar", "is_superuser": False},
            {"username": "editor", "email": "editor@demo.local", "full_name": "Content Editor", "is_superuser": False},
            {"username": "coordinator", "email": "coordinator@demo.local", "full_name": "ISMS Coordinator", "is_superuser": False},
        ]

        users = []
        for user_data in users_data:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                is_superuser=user_data["is_superuser"],
                password_hash=password_hash,
                is_active=True,
            )
            session.add(user)
            users.append(user)

        # Commit all users to generate IDs
        await session.commit()

        # Create TenantUsers
        for i, user in enumerate(users):
            user_data = users_data[i]
            tenant_user = TenantUser(
                tenant_id=tenant.id,
                user_id=user.id,
                is_default=True,
            )
            session.add(tenant_user)

        await session.commit()
        print(f"Created {len(users)} users")


        # =========================================================================
        # STANDARDS (Frameworks)
        # =========================================================================
        standards_data = [
            {
                "name": "ISO 27001",
                "version": "2022",
                "framework_type": FrameworkType.ISO27001,
                "description": "Information security management systems",
                "requirements": [
                    {"code": "A.5.1", "title": "Policies for information security", "category": "Organizational Controls"},
                    {"code": "A.5.2", "title": "Information security roles and responsibilities", "category": "Organizational Controls"},
                    {"code": "A.5.7", "title": "Threat intelligence", "category": "Organizational Controls"},
                    {"code": "A.6.1", "title": "Screening", "category": "People Controls"},
                    {"code": "A.6.2", "title": "Terms and conditions of employment", "category": "People Controls"},
                    {"code": "A.7.1", "title": "Physical security perimeters", "category": "Physical Controls"},
                    {"code": "A.8.1", "title": "User endpoint devices", "category": "Technological Controls"},
                    {"code": "A.8.2", "title": "Privileged access rights", "category": "Technological Controls"},
                    {"code": "A.8.3", "title": "Information access restriction", "category": "Technological Controls"},
                    {"code": "A.8.8", "title": "Management of technical vulnerabilities", "category": "Technological Controls"},
                ],
            },
            {
                "name": "BIO",
                "version": "2.0",
                "framework_type": FrameworkType.BIO,
                "description": "Baseline Informatiebeveiliging Overheid",
                "requirements": [
                    {"code": "BIO.5.1", "title": "Beleid voor informatiebeveiliging", "category": "Beleid"},
                    {"code": "BIO.5.2", "title": "Organisatie van informatiebeveiliging", "category": "Organisatie"},
                    {"code": "BIO.6.1", "title": "Veilig personeel", "category": "Personeel"},
                    {"code": "BIO.8.1", "title": "Bedrijfsmiddelen beheer", "category": "Bedrijfsmiddelen"},
                    {"code": "BIO.9.1", "title": "Toegangsbeveiliging", "category": "Toegang"},
                ],
            },
        ]

        all_requirements = []
        for std_data in standards_data:
            standard = Standard(
                tenant_id=tenant.id,
                name=std_data["name"],
                version=std_data["version"],
                type=std_data["framework_type"],
                description=std_data["description"],
            )
            session.add(standard)
            await session.commit()
            await session.refresh(standard)

            for req_data in std_data["requirements"]:
                req = Requirement(
                    standard_id=standard.id,
                    code=req_data["code"],
                    title=req_data["title"],
                    description=req_data.get("description", req_data["title"]),
                    category=req_data["category"],
                )
                session.add(req)
                await session.commit()
                await session.refresh(req)
                all_requirements.append(req)

        print(f"Created {len(standards_data)} standards with {len(all_requirements)} requirements")

        # =========================================================================
        # SCOPES (Organization Hierarchy)
        # =========================================================================
        # Organization level
        org_scope = Scope(
            tenant_id=tenant.id,
            name="Demo Organisatie",
            type=ScopeType.ORGANIZATION,
            description="Hoofdorganisatie",
            is_active=True,
        )
        session.add(org_scope)
        await session.commit()
        await session.refresh(org_scope)

        # Clusters
        clusters_data = [
            {"name": "ICT", "description": "ICT Afdeling"},
            {"name": "Bedrijfsvoering", "description": "Bedrijfsvoering en Financiën"},
            {"name": "Dienstverlening", "description": "Publieke Dienstverlening"},
        ]

        clusters = []
        for cluster_data in clusters_data:
            cluster = Scope(
                tenant_id=tenant.id,
                name=cluster_data["name"],
                type=ScopeType.CLUSTER,
                description=cluster_data["description"],
                parent_id=org_scope.id,
                is_active=True,
            )
            session.add(cluster)
            await session.commit()
            await session.refresh(cluster)
            clusters.append(cluster)

        # Processes
        processes_data = [
            {"name": "Identiteitenbeheer", "parent": clusters[0], "cia": ("CONFIDENTIAL", "CONFIDENTIAL", "CONFIDENTIAL")},
            {"name": "Netwerkbeheer", "parent": clusters[0], "cia": ("INTERNAL", "CONFIDENTIAL", "CONFIDENTIAL")},
            {"name": "Financiële Administratie", "parent": clusters[1], "cia": ("CONFIDENTIAL", "CONFIDENTIAL", "INTERNAL")},
            {"name": "Vergunningverlening", "parent": clusters[2], "cia": ("INTERNAL", "CONFIDENTIAL", "INTERNAL")},
        ]

        processes = []
        for proc_data in processes_data:
            process = Scope(
                tenant_id=tenant.id,
                name=proc_data["name"],
                type=ScopeType.PROCESS,
                parent_id=proc_data["parent"].id,
                confidentiality_rating=ClassificationLevel[proc_data["cia"][0]],
                integrity_rating=ClassificationLevel[proc_data["cia"][1]],
                availability_rating=ClassificationLevel[proc_data["cia"][2]],
                rto_hours=4,
                rpo_hours=1,
                is_active=True,
            )
            session.add(process)
            await session.commit()
            await session.refresh(process)
            processes.append(process)

        print(f"Created scope hierarchy: 1 org, {len(clusters)} clusters, {len(processes)} processes")

        # =========================================================================
        # RISKS
        # =========================================================================
        risks_data = [
            {
                "title": "Ongeautoriseerde toegang tot systemen",
                "description": "Risico op ongeautoriseerde toegang door zwakke authenticatie",
                "inherent_likelihood": RiskLevel.HIGH,
                "inherent_impact": RiskLevel.CRITICAL,
                "quadrant": AttentionQuadrant.MITIGATE,
                "mitigation": MitigationApproach.REDUCE,
            },
            {
                "title": "Datalekken door menselijke fouten",
                "description": "Risico op datalekken door fouten van medewerkers",
                "inherent_likelihood": RiskLevel.MEDIUM,
                "inherent_impact": RiskLevel.HIGH,
                "quadrant": AttentionQuadrant.MITIGATE,
                "mitigation": MitigationApproach.REDUCE,
            },
            {
                "title": "Ransomware aanval",
                "description": "Risico op ransomware infectie en versleuteling van data",
                "inherent_likelihood": RiskLevel.MEDIUM,
                "inherent_impact": RiskLevel.CRITICAL,
                "quadrant": AttentionQuadrant.MITIGATE,
                "mitigation": MitigationApproach.REDUCE,
            },
            {
                "title": "Uitval kerninfrastructuur",
                "description": "Risico op langdurige uitval van kritieke systemen",
                "inherent_likelihood": RiskLevel.LOW,
                "inherent_impact": RiskLevel.HIGH,
                "quadrant": AttentionQuadrant.ASSURANCE,
                "mitigation": None,
            },
            {
                "title": "Verlies van specialistische kennis",
                "description": "Risico door vertrek van key personnel",
                "inherent_likelihood": RiskLevel.MEDIUM,
                "inherent_impact": RiskLevel.MEDIUM,
                "quadrant": AttentionQuadrant.MONITOR,
                "mitigation": None,
            },
            {
                "title": "Verouderde software componenten",
                "description": "Risico door gebruik van end-of-life software",
                "inherent_likelihood": RiskLevel.HIGH,
                "inherent_impact": RiskLevel.LOW,
                "quadrant": AttentionQuadrant.MONITOR,
                "mitigation": None,
            },
            {
                "title": "Minor compliance afwijking",
                "description": "Kleine afwijking van procedures zonder significante impact",
                "inherent_likelihood": RiskLevel.LOW,
                "inherent_impact": RiskLevel.LOW,
                "quadrant": AttentionQuadrant.ACCEPT,
                "mitigation": None,
                "accepted": True,
            },
        ]

        level_to_score = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        risks = []
        for i, risk_data in enumerate(risks_data):
            risk = Risk(
                tenant_id=tenant.id,
                scope_id=processes[i % len(processes)].id,
                title=risk_data["title"],
                description=risk_data["description"],
                inherent_likelihood=risk_data["inherent_likelihood"],
                inherent_impact=risk_data["inherent_impact"],
                inherent_risk_score=level_to_score[risk_data["inherent_likelihood"]] * level_to_score[risk_data["inherent_impact"]],
                residual_likelihood=risk_data["inherent_likelihood"],
                residual_impact=risk_data["inherent_impact"],
                residual_risk_score=level_to_score[risk_data["inherent_likelihood"]] * level_to_score[risk_data["inherent_impact"]],
                attention_quadrant=risk_data["quadrant"],
                mitigation_approach=risk_data.get("mitigation"),
                risk_accepted=risk_data.get("accepted", False),
                status=Status.ACTIVE,
            )
            session.add(risk)
            await session.commit()
            await session.refresh(risk)
            risks.append(risk)

        print(f"Created {len(risks)} risks")

        # =========================================================================
        # MEASURES (Controls)
        # =========================================================================
        measures_data = [
            {"title": "Multi-Factor Authenticatie", "description": "MFA voor alle toegang tot kritieke systemen", "effectiveness": 85},
            {"title": "Security Awareness Training", "description": "Periodieke training voor alle medewerkers", "effectiveness": 70},
            {"title": "Backup en Recovery", "description": "Dagelijkse backups met wekelijkse recovery tests", "effectiveness": 90},
            {"title": "Endpoint Protection", "description": "Anti-malware en EDR op alle endpoints", "effectiveness": 80},
            {"title": "Network Segmentation", "description": "Segmentatie van netwerk in security zones", "effectiveness": 75},
            {"title": "Patch Management", "description": "Maandelijkse patching cyclus", "effectiveness": 85},
            {"title": "Access Review", "description": "Kwartaal review van toegangsrechten", "effectiveness": 65},
        ]

        measures = []
        for measure_data in measures_data:
            measure = Measure(
                tenant_id=tenant.id,
                name=measure_data["title"],
                description=measure_data["description"],
                typical_effectiveness=measure_data["effectiveness"],
                is_active=True,
            )
            session.add(measure)
            await session.commit()
            await session.refresh(measure)
            measures.append(measure)

        # =========================================================================
        # POLICIES
        # =========================================================================
        policies_data = [
            {"title": "Informatiebeveiligingsbeleid", "state": PolicyState.PUBLISHED, "req_id": all_requirements[0].id},
            {"title": "Acceptabel Gebruik Beleid", "state": PolicyState.PUBLISHED, "req_id": None},
            {"title": "Toegangsbeheersingsbeleid", "state": PolicyState.APPROVED, "req_id": all_requirements[8].id},
            {"title": "Incident Response Beleid", "state": PolicyState.REVIEW, "req_id": None},
            {"title": "Business Continuity Beleid", "state": PolicyState.DRAFT, "req_id": None},
        ]

        for policy_data in policies_data:
            policy = Policy(
                tenant_id=tenant.id,
                scope_id=org_scope.id,
                title=policy_data["title"],
                content=f"Dit is de inhoud van {policy_data['title']}.",
                state=policy_data["state"],
                version=1,
                requirement_id=policy_data["req_id"],
                created_by_id=users[1].id,
                review_date=datetime.utcnow() + timedelta(days=365),
            )
            session.add(policy)
        await session.commit()
        print(f"Created {len(policies_data)} policies")

        # =========================================================================
        # STATEMENT OF APPLICABILITY
        # =========================================================================
        for i, req in enumerate(all_requirements[:10]):
            soa = ApplicabilityStatement(
                tenant_id=tenant.id,
                scope_id=org_scope.id,
                requirement_id=req.id,
                is_applicable=True,
                justification="Applicable to organization scope",
                implementation_status=ImplementationStatus.IMPLEMENTED if i < 5 else ImplementationStatus.IN_PROGRESS,
                coverage_type=CoverageType.NOT_COVERED,
                local_control_id=None,
            )
            session.add(soa)
        await session.commit()
        print(f"Created {min(10, len(all_requirements))} SoA entries")

        # =========================================================================
        # ASSESSMENTS
        # =========================================================================
        # --- BIA Thresholds (global defaults, tenant_id=NULL) ---
        bia_thresholds_data = [
            {"score": 1, "label": "Laag", "classification_level": "Public",
             "rto_hours": 168, "rpo_hours": 24, "mtpd_hours": 336,
             "rto_label": "< 1 week", "rpo_label": "< 24 uur",
             "plan_required": False, "plan_label": "Nee"},
            {"score": 2, "label": "Midden", "classification_level": "Internal",
             "rto_hours": 24, "rpo_hours": 4, "mtpd_hours": 72,
             "rto_label": "< 24 uur", "rpo_label": "< 4 uur",
             "plan_required": True, "plan_label": "Basis BCP"},
            {"score": 3, "label": "Hoog", "classification_level": "Confidential",
             "rto_hours": 4, "rpo_hours": 1, "mtpd_hours": 24,
             "rto_label": "< 4 uur", "rpo_label": "< 1 uur",
             "plan_required": True, "plan_label": "Uitgebreid BCP"},
            {"score": 4, "label": "Kritiek", "classification_level": "Secret",
             "rto_hours": 0, "rpo_hours": 0, "mtpd_hours": 4,
             "rto_label": "< 15 min", "rpo_label": "0 (geen verlies)",
             "plan_required": True, "plan_label": "Full DR Plan"},
        ]
        for t in bia_thresholds_data:
            session.add(BIAThreshold(tenant_id=None, **t))
        await session.commit()
        print(f"Created {len(bia_thresholds_data)} BIA thresholds")

        # --- BIA Questions (12 vragen, global) ---
        bia_questions_data = [
            # Sectie A: Vertrouwelijkheid & Integriteit (CIA)
            {"code": "BIA-Q1", "question_text": "Bevat dit proces/systeem persoonsgegevens of geheimhoudingsgevoelige informatie?",
             "category": "BIA-A", "section": "Vertrouwelijkheid", "order": 1,
             "guidance": "Denk aan BSN, medische gegevens, financiele data, bedrijfsgeheimen."},
            {"code": "BIA-Q2", "question_text": "Wat is de reputatieschade of boeterisico als deze data op straat ligt?",
             "category": "BIA-A", "section": "Vertrouwelijkheid", "order": 2,
             "guidance": "1=minimaal, 2=beperkt, 3=significant, 4=existentieel (AVG-boete, mediacrisis)."},
            {"code": "BIA-Q3", "question_text": "Hoe cruciaal is het dat de data 100% accuraat is?",
             "category": "BIA-A", "section": "Integriteit", "order": 3,
             "guidance": "Denk aan financiele transacties, medische dossiers, juridische besluiten."},
            {"code": "BIA-Q4", "question_text": "Wat is de impact als een onbevoegd persoon data ongemerkt wijzigt?",
             "category": "BIA-A", "section": "Integriteit", "order": 4,
             "guidance": "1=minimaal, 2=beperkt, 3=significant (verkeerde besluiten), 4=catastrofaal."},
            # Sectie B: Beschikbaarheid & Continuiteit (BCM)
            {"code": "BIA-Q5", "question_text": "Wat is de directe schade per uur/dag dat dit proces stilstaat?",
             "category": "BIA-B", "section": "Beschikbaarheid", "order": 5,
             "guidance": "1=verwaarloosbaar, 2=beperkt, 3=significant omzetverlies, 4=onacceptabel."},
            {"code": "BIA-Q6", "question_text": "Zijn er SLA's of wetten die een maximale downtime dicteren?",
             "category": "BIA-B", "section": "Beschikbaarheid", "order": 6,
             "guidance": "1=geen afspraken, 2=interne SLA, 3=externe SLA, 4=wettelijke verplichting."},
            {"code": "BIA-Q7", "question_text": "Hoeveel andere bedrijfsprocessen vallen stil als dit systeem stopt?",
             "category": "BIA-B", "section": "Beschikbaarheid", "order": 7,
             "guidance": "1=geen, 2=1-2 processen, 3=3-5 processen, 4=kritieke keten stopt."},
            {"code": "BIA-Q8", "question_text": "Hoe snel merken klanten dat de dienstverlening is onderbroken?",
             "category": "BIA-B", "section": "Beschikbaarheid", "order": 8,
             "guidance": "1=niet, 2=na dagen, 3=binnen uren, 4=direct."},
            # Sectie C: Dataverlies & Herstel (RPO/RTO modifier)
            {"code": "BIA-Q9", "question_text": "Is verloren data handmatig te herstellen?",
             "category": "BIA-C", "section": "Dataverlies", "order": 9,
             "guidance": "1=volledig herstelbaar, 2=deels herstelbaar, 3=moeilijk, 4=onmogelijk."},
            {"code": "BIA-Q10", "question_text": "Hoeveel nieuwe data wordt er per uur geproduceerd?",
             "category": "BIA-C", "section": "Dataverlies", "order": 10,
             "guidance": "1=weinig, 2=matig, 3=veel, 4=continu (real-time transacties)."},
            {"code": "BIA-Q11", "question_text": "Is er een kritiek herstelmoment waarop herstel binnen minuten essentieel is?",
             "category": "BIA-C", "section": "RTO modifier", "order": 11,
             "guidance": "1=nee, 2=binnen dagen, 3=binnen uren, 4=binnen minuten (RTO modifier)."},
            {"code": "BIA-Q12", "question_text": "Is er een workaround beschikbaar tijdens uitval?",
             "category": "BIA-C", "section": "RTO modifier", "order": 12,
             "guidance": "1=volledige workaround, 2=beperkte workaround, 3=minimale workaround, 4=geen workaround (RTO modifier)."},
        ]
        for q in bia_questions_data:
            session.add(AssessmentQuestion(
                tenant_id=None,
                question_type=QuestionType.SCALE_1_4,
                weight=1.0,
                is_active=True,
                **q,
            ))
        await session.commit()
        print(f"Created {len(bia_questions_data)} BIA questions")

        # --- Assessments ---
        assessment = Assessment(
            tenant_id=tenant.id,
            scope_id=processes[0].id,
            title="Q1 2024 Security Assessment",
            type=AssessmentType.AUDIT,
            status=Status.CLOSED,
            phase="Afgerond",
            start_date=datetime.utcnow() - timedelta(days=30),
            completed_date=datetime.utcnow() - timedelta(days=5),
            overall_result=AuditResult.PARTIAL,
            lead_assessor_id=users[1].id,
        )
        session.add(assessment)
        await session.commit()
        await session.refresh(assessment)

        # BIA assessment (draft)
        bia_assessment = Assessment(
            tenant_id=tenant.id,
            scope_id=processes[0].id,
            title="BIA - Personeelsadministratie",
            type=AssessmentType.BIA,
            status=Status.DRAFT,
            phase="Aangevraagd",
            lead_assessor_id=users[1].id,
        )
        session.add(bia_assessment)
        await session.commit()
        await session.refresh(bia_assessment)

        # Findings
        findings_data = [
            {"title": "Zwakke wachtwoorden gevonden", "severity": FindingSeverity.HIGH},
            {"title": "Verouderde SSL certificaten", "severity": FindingSeverity.MEDIUM},
            {"title": "Logging niet volledig", "severity": FindingSeverity.LOW},
        ]
        for finding_data in findings_data:
            finding = Finding(
                tenant_id=tenant.id,
                assessment_id=assessment.id,
                title=finding_data["title"],
                description=f"Details over {finding_data['title']}",
                severity=finding_data["severity"],
                status=Status.ACTIVE,
            )
            session.add(finding)
        await session.commit()
        print(f"Created 2 assessments with {len(findings_data)} findings")

        # =========================================================================
        # PROCESSING ACTIVITIES (PIMS)
        # =========================================================================
        processing_activities = [
            {
                "name": "Personeelsadministratie",
                "purpose": "Beheer van personeelsgegevens",
                "legal_basis": LegalBasis.CONTRACT,
            },
            {
                "name": "Vergunningregistratie",
                "purpose": "Registratie van vergunningaanvragen",
                "legal_basis": LegalBasis.PUBLIC_TASK,
            },
        ]
        for pa_data in processing_activities:
            pa = ProcessingActivity(
                tenant_id=tenant.id,
                scope_id=processes[0].id,
                name=pa_data["name"],
                purpose=pa_data["purpose"],
                legal_basis=pa_data["legal_basis"],
                data_subject_categories="Burgers, Medewerkers",
                personal_data_categories="Naam, Adres, BSN",
                retention_period="5 jaar",
            )
            session.add(pa)
        await session.commit()
        print(f"Created {len(processing_activities)} processing activities")

        # =========================================================================
        # CONTINUITY PLANS (BCMS)
        # =========================================================================
        bcp = ContinuityPlan(
            tenant_id=tenant.id,
            scope_id=processes[0].id,
            title="Business Continuity Plan - ICT",
            plan_type=PlanType.BCP,
            content="Uitgebreid plan voor continuïteit van ICT diensten",
            rto_hours=4,
            rpo_hours=1,
            mtpd_hours=24,
            version=1,
            status=PolicyState.APPROVED,
            owner_id=users[1].id,
        )
        session.add(bcp)
        await session.commit()
        await session.refresh(bcp)

        # Continuity Test
        test = ContinuityTest(
            tenant_id=tenant.id,
            plan_id=bcp.id,
            title="Tabletop Oefening Q1",
            test_type=TestType.TABLETOP,
            scheduled_date=datetime.utcnow() + timedelta(days=30),
            scenario="Test herstel van kritieke ICT-systemen na uitval",
        )
        session.add(test)
        await session.commit()
        print("Created 1 continuity plan with 1 scheduled test")

        # =========================================================================
        # USER SCOPE ROLES
        # =========================================================================
        # Admin → Beheerder on org scope
        admin_role = UserScopeRole(
            tenant_id=tenant.id,
            user_id=users[0].id,
            scope_id=org_scope.id,
            role=Role.BEHEERDER,
        )
        session.add(admin_role)

        # CISO → Toezichthouder + Coordinator on org scope (dual role)
        ciso_role = UserScopeRole(
            tenant_id=tenant.id,
            user_id=users[1].id,
            scope_id=org_scope.id,
            role=Role.TOEZICHTHOUDER,
        )
        session.add(ciso_role)

        ciso_coordinator_role = UserScopeRole(
            tenant_id=tenant.id,
            user_id=users[1].id,
            scope_id=org_scope.id,
            role=Role.COORDINATOR,
        )
        session.add(ciso_coordinator_role)

        # FG → Toezichthouder on org scope
        fg_role = UserScopeRole(
            tenant_id=tenant.id,
            user_id=users[2].id,
            scope_id=org_scope.id,
            role=Role.TOEZICHTHOUDER,
        )
        session.add(fg_role)

        # Process owner → Eigenaar on process scope
        pe_role = UserScopeRole(
            tenant_id=tenant.id,
            user_id=users[3].id,
            scope_id=processes[0].id,
            role=Role.EIGENAAR,
        )
        session.add(pe_role)

        # Editor → Medewerker on process scope
        editor_role = UserScopeRole(
            tenant_id=tenant.id,
            user_id=users[4].id,
            scope_id=processes[0].id,
            role=Role.MEDEWERKER,
        )
        session.add(editor_role)

        # Coordinator → Coordinator on org scope
        coordinator_role = UserScopeRole(
            tenant_id=tenant.id,
            user_id=users[5].id,
            scope_id=org_scope.id,
            role=Role.COORDINATOR,
        )
        session.add(coordinator_role)

        await session.commit()
        print("Created user scope roles")

        # =========================================================================
        # WORKFLOW DEFINITIONS
        # =========================================================================
        # Policy workflow
        policy_workflow = WorkflowDefinition(
            tenant_id=tenant.id,
            name="Policy Approval",
            description="Standard policy approval workflow",
            applicable_entity_types='["Policy"]',
            is_active=True,
        )
        session.add(policy_workflow)
        await session.commit()
        await session.refresh(policy_workflow)

        # Workflow states
        states_data = [
            {"name": "Draft", "is_initial": True, "is_final": False},
            {"name": "Review", "is_initial": False, "is_final": False},
            {"name": "Approved", "is_initial": False, "is_final": False},
            {"name": "Published", "is_initial": False, "is_final": True},
            {"name": "Archived", "is_initial": False, "is_final": True},
        ]
        states = []
        for i, state_data in enumerate(states_data):
            state = WorkflowState(
                workflow_id=policy_workflow.id,
                name=state_data["name"],
                is_initial=state_data["is_initial"],
                is_final=state_data["is_final"],
                order_index=i,
            )
            session.add(state)
            await session.commit()
            await session.refresh(state)
            states.append(state)

        # Workflow transitions
        transitions = [
            (0, 1, "Submit for Review"),
            (1, 2, "Approve"),
            (1, 0, "Reject"),
            (2, 3, "Publish"),
            (3, 4, "Archive"),
        ]
        for from_idx, to_idx, name in transitions:
            transition = WorkflowTransition(
                workflow_id=policy_workflow.id,
                from_state_id=states[from_idx].id,
                to_state_id=states[to_idx].id,
                name=name,
                required_role=Role.BEHEERDER.value if "Approve" in name else None,
            )
            session.add(transition)
        await session.commit()
        print(f"Created workflow with {len(states)} states and {len(transitions)} transitions")

        # =====================================================================
        # ORGANIZATION PROFILE (demo)
        # =====================================================================
        org_profile = OrganizationProfile(
            tenant_id=tenant.id,
            # Blok 1: Identiteit
            org_type="Gemeente",
            sector="Overheid",
            employee_count="201-500",
            location_count=3,
            geographic_scope="Regionaal",
            core_services="Burgerzaken, Vergunningen, Belastingen, Sociaal domein",
            # Blok 2: Governance
            existing_certifications=json.dumps(["DigiD TPM"]),
            applicable_frameworks=json.dumps(["BIO", "AVG"]),
            has_security_officer=True,
            has_dpo=True,
            governance_maturity="Basis",
            risk_appetite_availability="Laag",
            risk_appetite_integrity="Laag",
            risk_appetite_confidentiality="Midden",
            # Blok 3: IT-Landschap
            cloud_strategy="Hybrid",
            cloud_providers=json.dumps(["Azure", "On-premises datacenter"]),
            workstation_count="201-500",
            has_remote_work=True,
            has_byod=False,
            critical_systems="Zaaksysteem, BRP, BAG, Financieel systeem, E-mail",
            outsourced_it=True,
            primary_it_supplier="SSC-ICT",
            # Blok 4: Privacy
            processes_personal_data=True,
            data_subject_types=json.dumps(["Burgers", "Medewerkers", "Leveranciers"]),
            has_special_categories=True,
            international_transfers=False,
            processing_count_estimate="51-100",
            # Blok 5: Continuiteit
            has_bcp=False,
            has_incident_response_plan=True,
            max_tolerable_downtime="Dag",
            critical_process_count=5,
            key_dependencies="SSC-ICT, KPN, Microsoft Azure, Zaaksysteem-leverancier",
            # Blok 6: Mensen
            has_awareness_program=True,
            has_background_checks=True,
            training_frequency="Jaarlijks",
            # Meta
            wizard_completed=True,
            wizard_current_step=5,
        )
        session.add(org_profile)
        await session.commit()
        print("Created organization profile for demo tenant")

        print("\n" + "="*60)
        print("SEED DATA COMPLETE")
        print("="*60)
        print(f"Tenant: {tenant.name} (ID: {tenant.id})")
        print(f"Users: {len(users)}")
        print(f"Standards: {len(standards_data)}")
        print(f"Requirements: {len(all_requirements)}")
        print(f"Scopes: 1 org + {len(clusters)} clusters + {len(processes)} processes")
        print(f"Risks: {len(risks)}")
        print(f"Measures: {len(measures)}")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(seed_database())
