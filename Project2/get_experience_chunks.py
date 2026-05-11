"""
---------------------------
Sarada Gummadi's experience, chunked into labelled topic areas.
Use get_chunks_for_topic() to retrieve relevant sections by keyword,
or inject EXPERIENCE_CHUNKS directly into an agent system prompt.
"""

EXPERIENCE_CHUNKS = {

    # ─────────────────────────────────────────────────────────────
    # 1. CAREER PROGRESSION & RECOGNITION
    # ─────────────────────────────────────────────────────────────
    "career_progression": {
        "label": "Career Progression & Recognition",
        "keywords": [
            "promotion", "career", "growth", "recognition", "leadership journey",
            "expert engineer", "title", "trajectory"
        ],
        "content": """
- Joined JPMorgan Chase in January 2016 as Associate in the Application Security team.
- Promoted to Senior Associate within one year for fast technical contribution.
- Promoted to Vice President (VP) in 2019 after leading a firm-wide CI/CD transformation 
  that delivered 2,000+ daily scans across 5,000+ applications.
- Selected for the Expert Engineer Programme in 2019 — JPMorgan's flagship technical 
  leadership cohort of only 100 high-performing technologists across the global firm.
- Promoted to Executive Director in 2022 following the delivery of a self-service 
  knowledge platform that reduced support effort by 50% and improved productivity by 35%.
- Progression from Associate to Executive Director across 6 years at the same firm, 
  driven entirely by delivery impact rather than tenure.
"""
    },

    # ─────────────────────────────────────────────────────────────
    # 2. APPLICATION SECURITY & CI/CD TRANSFORMATION (2016–2019)
    # ─────────────────────────────────────────────────────────────
    "application_security_cicd": {
        "label": "Application Security Engineering & CI/CD Transformation (2016–2019)",
        "keywords": [
            "application security", "blackduck", "open source scanning", "CI/CD",
            "scan performance", "pipeline", "devsecops", "shift left",
            "developer productivity", "scan time", "legacy system"
        ],
        "content": """
- Joined the Application Security team managing BlackDuck, an open source scanning tool.
- The legacy system ran on a fixed schedule, causing multi-hour delays that blocked 
  application teams from progressing with production deployments.
- When the firm moved to integrated CI/CD pipelines, completely redesigned the scanning 
  platform to support real-time, on-demand scans at scale.
- Redesign approach: 
    1. Exposed an API to trigger scans in real time (replacing scheduled batch runs).
    2. Optimised the vendor scanning tool to publish results within minutes.
    3. Introduced event-driven ETL to aggregate and transform scan results for reporting.
- Result: Reduced scan execution time from 8+ hours to under 15 minutes.
- Scale achieved: 2,000+ daily scans across 5,000+ applications firm-wide.
- This delivery required close collaboration with the CI/CD team, multiple stakeholders, 
  and senior leadership — earning visibility that led directly to VP promotion.
"""
    },

    # ─────────────────────────────────────────────────────────────
    # 3. AWS CLOUD SRE LEADERSHIP (2019–2022)
    # ─────────────────────────────────────────────────────────────
    "aws_sre_leadership": {
        "label": "AWS Cloud SRE Leadership — APAC (2019–2022)",
        "keywords": [
            "SRE", "site reliability", "AWS", "cloud operations", "platform reliability",
            "cloud adoption", "24/7", "production support", "APAC", "SME",
            "platform availability", "LOB", "application migration"
        ],
        "content": """
- Appointed to establish the APAC Cloud SRE function from inception, immediately after 
  the AWS platform reached General Availability — with no prior AWS experience.
- On day one, faced live customers at a cloud adoption event with no preparation time. 
  Within two months, mastered the platform and became the go-to SME for troubleshooting 
  across US, UK, and APAC application teams.
- An AWS consultant visiting Singapore explicitly noted that one LOB team was heavily 
  relying on the Singapore SRE team to resolve their issues.
- Led a global team running 24/7 operations supporting 1,000+ production applications.
- Identified flaws in the platform implementation and partnered with engineering teams 
  to fix them, improving platform capability and customer experience.
- Enabled migration and operational readiness for 1,000+ production applications on AWS 
  through hands-on technical leadership, guidance, and troubleshooting.
- Built the APAC SRE practice into a firm-wide reference model adopted by global teams.
"""
    },

    # ─────────────────────────────────────────────────────────────
    # 4. SELF-SERVICE & DEVELOPER PRODUCTIVITY TOOLS
    # ─────────────────────────────────────────────────────────────
    "self_service_and_productivity": {
        "label": "Self-Service Platforms & Developer Productivity",
        "keywords": [
            "self service", "knowledge platform", "ElasticSearch", "support tickets",
            "developer productivity", "automation", "GitHub Copilot", "AI-assisted",
            "test generation", "support reduction", "inner source", "knowledge base"
        ],
        "content": """
SELF-SERVICE KNOWLEDGE PLATFORM (SRE era, 2020–2021):
- Identified a pattern of repetitive support tickets as new customers onboarded to AWS.
- Proposed and built a self-service knowledge platform: ingested historical incidents, 
  platform knowledge documents, and FAQs; sanitised and indexed in ElasticSearch, 
  queryable by service type and issue description.
- Outcome: 50% reduction in manual support effort (ticket volume drop), 35% productivity 
  gain across engineering teams.
- Platform adopted globally — used by both customers and SRE team members firm-wide.

AI-ASSISTED TEST GENERATION (Compliance era, 2024–2025):
- Introduced GitHub Copilot agents to generate policy compliance test scripts 
  in a standardised format applicable across all cloud services.
- Previous effort: minimum one full day per service (writing feature files, glue code, 
  back-end configurations, validation).
- With GitHub Copilot: under 5 minutes for a full service's test scripts, achieving 
  80% accuracy with minimal developer effort for configuration updates.
- Tests are automatically registered with a centralised testing service which runs on 
  schedule, captures evidence, and publishes a dashboard for Cyber, Product, and 
  Engineering teams.
"""
    },

    # ─────────────────────────────────────────────────────────────
    # 5. CLOUD COST OPTIMISATION
    # ─────────────────────────────────────────────────────────────
    "cloud_cost_optimisation": {
        "label": "Cloud Cost Optimisation",
        "keywords": [
            "cost", "cost optimisation", "cloud spend", "EC2", "RDS", "lightswitch",
            "orphaned resources", "lifecycle", "compute scheduling", "cost reduction",
            "AWS cost", "Azure cost", "resource cleanup"
        ],
        "content": """
- Identified cost optimisation opportunities while running premium support for 10 LOB 
  application teams.
- Collaborated with the platform engineering team to build and enhance the Lightswitch 
  capability: allowed customers to automatically shut down EC2 and RDS instances during 
  off-hours and restart them at the start of operational hours.
- Guided application teams in adopting Lightswitch to reduce their cloud spend.
- Built self-service automation for orphaned resource cleanup — automatically identifying 
  and removing unused resources to avoid unnecessary costs, while meeting control requirements.
- Built self-service RDS password rotation/reset capability, reducing manual operational effort.
- Contributed to an estimated 20% reduction in overall cloud spend through landing zone 
  re-architecture, lifecycle management, and compute scheduling automation.
- Established centralised cloud asset governance across AWS and Azure, enabling identification 
  and remediation of 100,000+ non-compliant resources, reducing operational and regulatory 
  risk exposure.
"""
    },

    # ─────────────────────────────────────────────────────────────
    # 6. TEAM LEADERSHIP & STAKEHOLDER MANAGEMENT
    # ─────────────────────────────────────────────────────────────
    "team_leadership": {
        "label": "Team Leadership, Hiring & Stakeholder Management",
        "keywords": [
            "team", "hiring", "mentoring", "coaching", "leadership", "people management",
            "global team", "stakeholders", "org change", "reorg", "motivation",
            "distributed team", "cross-functional"
        ],
        "content": """
- Grew and led a globally distributed team of 15+ engineers across multiple time zones, 
  including hiring, mentoring, and coaching responsibilities.
- Led the team through 3+ major organisational restructures over 2022–2025, maintaining 
  delivery continuity and team motivation through repeated strategy pivots and leadership changes.
- When a peer became the direct manager following a reorg, maintained professional composure, 
  kept the team focused, and continued delivering against platform goals.
- Managed a premium support programme for 10 dedicated LOB customers/application teams, 
  helping each advance their cloud maturity and optimise usage.
- Enabled Windows workload support for a JPMorgan acquisition: identified platform gaps, 
  coordinated multiple feature teams, and contributed directly to platform capability — 
  receiving appreciation from all stakeholders involved.
- Consistently engaged Architecture, Cyber, Risk, and Engineering leadership across 
  cross-functional delivery — aligning diverse stakeholders under ambiguous requirements 
  and shifting priorities.
- Championed the team's contributions during periods of low visibility from senior leadership, 
  escalating to Product and Engineering management when platform investment was under-prioritised.
"""
    },

    # ─────────────────────────────────────────────────────────────
    # 7. AZURE PLATFORM ENGINEERING & CI/CD BUILD (2023–2024)
    # ─────────────────────────────────────────────────────────────
    "azure_platform_engineering": {
        "label": "Azure Platform Engineering & CI/CD Pipeline (2023–2024)",
        "keywords": [
            "Azure", "Azure platform", "CI/CD", "GitHub Actions", "Terraform Enterprise",
            "IaC", "infrastructure as code", "disconnected", "hybrid cloud",
            "Azure DevOps", "pipeline", "platform engineering"
        ],
        "content": """
- In May 2023, appointed to lead Azure platform enablement for the firm following 
  an organisational restructure — entirely new cross-functional stakeholder landscape.
- Initial strategy: disconnected Azure platform (no direct network connection to JPMorgan 
  network, only AD integration). Built the full CI/CD pipeline from scratch:
    - GitHub as SCM
    - GitHub Actions for CI/CD automation
    - Terraform Enterprise for IaC deployments
- Delivered the complete pipeline despite this being new territory for both the team 
  and the leader — motivated and guided the team through the learning curve.
- Coordinated alignment across Architecture, Security, Risk & Controls, and broader 
  Azure engineering teams to meet all control standards.
- In March 2024, strategy changed: Azure moved from disconnected to fully integrated 
  hybrid cloud alongside AWS. Previous work was deprecated. Led the team through 
  the demoralising transition — kept them focused and productive despite discarded effort.
- Challenged and redirected a high-risk vendor-led testing approach that relied on 
  unsupported Microsoft APIs — secured alignment on a sustainable alternative 
  without impacting delivery timelines.
"""
    },

    # ─────────────────────────────────────────────────────────────
    # 8. POLICY-AS-CODE & PLATFORM TESTING FRAMEWORK
    # ─────────────────────────────────────────────────────────────
    "policy_as_code_testing": {
        "label": "Policy-as-Code Testing Framework & CI/CD Governance",
        "keywords": [
            "policy as code", "testing framework", "CI/CD governance", "terraform module",
            "service pipeline", "artifactory", "central pipeline", "policy deployment",
            "Cyber approval", "compliance testing", "shift left compliance"
        ],
        "content": """
PROBLEM IDENTIFIED:
- The existing policy deployment pipeline was fragmented, unmaintainable, and unscalable:
    - Each service had its own repo; pipelines only packaged and published to Artifactory.
    - A central deployment pipeline handled all services — engineers had to manually 
      coordinate, causing cross-service conflicts and blockers when one service failed.
    - No per-service testing or validation capability in isolation.
    - Engineers had to deploy to a shared lower environment, validate manually, fix, 
      and repeat — a slow, conflict-prone cycle.

SOLUTION DESIGNED AND DELIVERED:
- Designed a Terraform module that individual service engineers deploy from their own 
  service pipeline to lower environments — enabling isolated testing and evidence 
  generation without impacting other teams.
- Once validated, the working artifact is published to the central repository and 
  the central deployment pipeline is updated with captured evidence.
- Cyber teams can confidently approve PR changes knowing full validation has already 
  occurred at the service level.
- Result: eliminated cross-service deployment conflicts, accelerated service engineer 
  productivity, and gave Cyber teams structured pre-approval assurance.
"""
    },

    # ─────────────────────────────────────────────────────────────
    # 9. CHAOS ENGINEERING & PLATFORM RESILIENCE (2024–2025)
    # ─────────────────────────────────────────────────────────────
    "chaos_engineering": {
        "label": "Chaos Engineering & Platform Resilience (Azure GA)",
        "keywords": [
            "chaos engineering", "chaos studio", "Gremlin", "game day", "resilience",
            "platform stability", "Azure GA", "permit to operate", "fault injection",
            "cyber resiliency", "platform availability", "SRE resilience"
        ],
        "content": """
- Identified the need for chaos engineering capability to validate Azure platform 
  resilience and meet Permit-to-Operate (PTO) requirements ahead of General Availability.
- Evaluated Azure Chaos Studio vs Gremlin (the firm's existing tool for AWS): 
  conducted a thorough pros/cons analysis, identified gaps, and engaged the firm's 
  Chaos Engineering team, Cyber Resiliency team, and Architecture team.
- Secured firm-wide agreement to adopt Azure Chaos Studio for the Azure platform.
- Delivered the full chaos engineering capability:
    - Enabled Chaos Studio with required security controls.
    - Built chaos testing scripts, documentation, and runbooks.
    - Shared knowledge with the broader Chaos Engineering LOB team, Azure Platform 
      Engineering team, and Platform SRE team.
- Led game day execution with comprehensive planning, cross-functional collaboration 
  across global teams in production, and produced evidence for multiple platform components.
- Identified design gaps during game days, shared findings and remediation proposals 
  with engineering teams — leading to measurable improvements in platform stability, 
  availability, and resilience.
- Outcome: met all firm-standard PTO control requirements; Azure platform marked as GA.
"""
    },

    # ─────────────────────────────────────────────────────────────
    # 10. CLOUD ASSET INVENTORY & DELTA FEED REDESIGN (2025)
    # ─────────────────────────────────────────────────────────────
    "cloud_asset_inventory": {
        "label": "Cloud Asset Inventory & Architecture Redesign (2025)",
        "keywords": [
            "asset inventory", "cloud assets", "system of record", "logic app",
            "function app", "Azure Resource Graph", "event hub", "delta feed",
            "configuration drift", "technology lifecycle", "reconciliation"
        ],
        "content": """
- Took ownership of the cloud asset inventory platform (handed over via reorg) — 
  responsible for capturing all cloud assets in the firm's system of record for 
  lifecycle management, configuration drift detection, and regulatory compliance.

LEGACY DESIGN PROBLEMS IDENTIFIED:
- Used Azure Logic Apps (limited to inline Node.js scripting) reading from Azure Resource 
  Graph and publishing to Event Hub.
- An on-prem application consumed from Event Hub and published to the system of record.
- Multiple integration points with no reconciliation — undetected data gaps.
- Published a full asset feed on every run — unscalable as the platform grows.

NEW DESIGN PROPOSED AND IMPLEMENTED:
- Replaced Logic Apps with Azure Function Apps (Python) for full processing capability 
  and long-term maintainability.
- Introduced a delta feed model: only assets changed since the last run are published, 
  dramatically reducing processing volume as the platform scales.
- Aligned the design with the AWS asset inventory pattern (for hybrid cloud consistency) 
  in collaboration with the Architecture team — approved and implemented.
- Thoroughly tested and deployed to lower environments before a further reorg required 
  handover to another team. Completed a full knowledge transfer; the new team agreed 
  to promote the design to production.
"""
    },

    # ─────────────────────────────────────────────────────────────
    # 11. CONTINUOUS COMPLIANCE ASSURANCE (2025)
    # ─────────────────────────────────────────────────────────────
    "continuous_compliance": {
        "label": "Continuous Compliance Assurance (2025)",
        "keywords": [
            "compliance", "continuous compliance", "control validation", "evidence",
            "permit to operate", "policy", "Cyber", "CTC", "automated compliance",
            "compliance dashboard", "assurance", "governance", "control requirements"
        ],
        "content": """
- Led initiative to establish a continuous compliance environment across the Azure platform:
    1. Provide pre-enablement evidence that all control requirements are met before 
       a service goes to production.
    2. Continuously validate deployed control policies against CTC (Controls, Technology 
       & Compliance) requirements on an ongoing schedule.
    3. Automatically surface gaps to CTC, Product, and Engineering teams when new 
       controls are introduced, enabling timely policy development and deployment.

- Embedded compliance validation directly into the policy deployment CI/CD pipeline 
  using the Terraform module approach (see Policy-as-Code section).

- Introduced GitHub Copilot-assisted test script generation:
    - Previous: 1 full day per service to write feature files, glue code, back-end 
      configurations, and validate.
    - After: under 5 minutes per service, achieving 80% accuracy with minimal 
      developer effort for configuration tuning.
    - Tests are standardised and reusable across all cloud services.

- Once test scripts are committed alongside policy files, they are registered with 
  a centralised testing service that runs on a schedule, captures timestamped evidence, 
  and publishes a real-time dashboard accessible to Cyber, Product, and Engineering teams.

- Outcome: ongoing, auditable compliance assurance without manual intervention — 
  aligned with firm Permit-to-Operate standards across 500+ policies.
"""
    },

}


# ─────────────────────────────────────────────────────────────────────────────
# TOPIC → CHUNK MAPPING
# For quick lookup when the agent or evaluator needs relevant sections.
# ─────────────────────────────────────────────────────────────────────────────

TOPIC_MAP = {
    "developer productivity":       ["self_service_and_productivity", "application_security_cicd", "policy_as_code_testing"],
    "productivity":                 ["self_service_and_productivity", "application_security_cicd"],
    "cost optimisation":            ["cloud_cost_optimisation"],
    "cloud cost":                   ["cloud_cost_optimisation"],
    "governance":                   ["continuous_compliance", "policy_as_code_testing", "cloud_cost_optimisation"],
    "compliance":                   ["continuous_compliance", "policy_as_code_testing", "chaos_engineering"],
    "cloud governance":             ["continuous_compliance", "policy_as_code_testing"],
    "largest system":               ["aws_sre_leadership", "team_leadership", "azure_platform_engineering"],
    "scale":                        ["aws_sre_leadership", "application_security_cicd"],
    "team management":              ["team_leadership"],
    "leadership":                   ["team_leadership", "career_progression"],
    "why hire you":                 ["career_progression", "team_leadership", "aws_sre_leadership"],
    "differentiator":               ["career_progression", "aws_sre_leadership", "chaos_engineering"],
    "AWS":                          ["aws_sre_leadership", "cloud_cost_optimisation"],
    "Azure":                        ["azure_platform_engineering", "chaos_engineering", "cloud_asset_inventory", "continuous_compliance"],
    "CI/CD":                        ["application_security_cicd", "azure_platform_engineering", "policy_as_code_testing"],
    "SRE":                          ["aws_sre_leadership", "chaos_engineering"],
    "resilience":                   ["chaos_engineering"],
    "chaos engineering":            ["chaos_engineering"],
    "AI":                           ["self_service_and_productivity"],
    "GitHub Copilot":               ["self_service_and_productivity"],
    "career progression":           ["career_progression"],
    "background":                   ["career_progression", "aws_sre_leadership", "application_security_cicd"],
}


def get_chunks_for_topic(topic: str, max_chunks: int = 3) -> str:
    """
    Returns formatted experience chunks relevant to a given topic string.
    Falls back to all chunks if no keyword match is found.

    Usage:
        context = get_chunks_for_topic("developer productivity")
        # inject context into agent system prompt
    """
    topic_lower = topic.lower()

    # Find best matching keys
    matched_chunk_keys = []
    for keyword, chunk_keys in TOPIC_MAP.items():
        if keyword.lower() in topic_lower:
            for key in chunk_keys:
                if key not in matched_chunk_keys:
                    matched_chunk_keys.append(key)

    # Fallback: return all chunks
    if not matched_chunk_keys:
        matched_chunk_keys = list(EXPERIENCE_CHUNKS.keys())

    selected = matched_chunk_keys[:max_chunks]

    output = []
    for key in selected:
        chunk = EXPERIENCE_CHUNKS[key]
        output.append(f"### {chunk['label']}\n{chunk['content'].strip()}")

    return "\n\n".join(output)


def get_all_chunks_formatted() -> str:
    """
    Returns all experience chunks as a single formatted string.
    Use this when injecting full context into the agent system prompt.
    """
    output = []
    for chunk in EXPERIENCE_CHUNKS.values():
        output.append(f"### {chunk['label']}\n{chunk['content'].strip()}")
    return "\n\n".join(output)
