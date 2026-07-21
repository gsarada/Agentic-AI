company_prompt = """You are an expert corporate communications AI agent. Your task is to generate 4 distinct knowledge base documents for a fictitious AI/ML company named "Aethel AI". Each document must be output in clean Markdown format. 

Here are the specifications for the 4 documents:

1. **about.md**: Focus on the company's founding vision, mission statement, and core AI/ML technology focus (e.g., decentralized neural networks, enterprise LLM orchestration).
2. **overview.md**: Provide a high-level business summary, industry verticals served, market positioning, and a brief timeline of company milestones.
3. **culture.md**: Detail the company's vision, mission statements, core values, remote-first/hybrid philosophy, commitment to ethical AI, and internal engineering culture (e.g., hackathons, open-source contributions).
4. **careers.md**: Describe the hiring philosophy, standard benefits, growth paths for AI researchers and engineers, and a general pitch on why top talent joins Aethel AI.

Use professional, forward-thinking, and authentic corporate language. Ensure clear headings, bullet points, and consistent branding across all four files. Deliver the output as 4 separate Markdown files. Use the file management tools to write the files to 'company' folder"""

products_prompt = """You are a Principal Technical Product Manager AI agent at "Aethel AI". Your task is to generate exactly 10 separate Markdown documents, one for each of the company's core AI/ML products. 

The suite of 10 products should cover a realistic AI ecosystem (e.g., MLops pipelines, data labeling automation, synthetic data generators, LLM guardrails, edge AI deployment, etc.).

For each of the 10 documents (named `<productname>.md`), you must use the following standard Markdown template:

# Product Name: [Insert Fictitious Name]
## SKU/ID: [AE-PROD-XXX]
---
### 1. Product Overview
[2-3 sentences explaining what the product does and the core problem it solves.]

### 2. Key Features & Capabilities
* **Feature 1:** [Description]
* **Feature 2:** [Description]
* **Feature 3:** [Description]

### 3. Target Audience & Use Cases
* **Ideal Customer Profile:** [e.g., Enterprise Data Science Teams]
* **Primary Use Case:** [Detailed scenario]

### 4. Technical Architecture Notes
[Briefly mention underlying ML frameworks, deployment models like SaaS/On-Prem, or API structure.]

### 5. Pricing
The pricing tiers or flat price applicable

Ensure each product feels distinct, technically plausible, and highly innovative. Generate all 10 documents. Use file tool to write the files into 'products' folder"""

employees_prompt = """You are a People Operations AI agent at "Aethel AI". Your task is to generate a comprehensive internal employee directory consisting of exactly 25 distinct employee profile documents.

Mix the roles realistically across the company: ~13 in Engineering/AI Research, ~5 in Product/Design, ~5 in Sales/Marketing/Growth, and ~2 in HR/Operations/Leadership.

For each employee document <employee full name>.md, use the following Markdown structure:

[Full Name]
## Summary: 
**Date of Birth:** [DD-MMM-YYYY] 
**Department:** [Department Name] 
**Job Title:** [Job Title] 
** Current Salary:** [Salary]
---
### Career Progression
[A list of different roles and responsibilities carried out progressively during the entire career at the company.]

### Core Skills & Technologies
* [Skill 1 / e.g., PyTorch, Rust, MLOps]
* [Skill 2 / e.g., Prompt Engineering, Kubernetes]
* [Skill 3 / e.g., Cross-functional Leadership]

### Compensation History
[A year wise record of Base salary and bonus Example **2005** - Base Salary: $135,000, Bonus: $20,000]

### Annual Performance History
[ A list of performance evaluation records upto 30 words in each year most recent to older capturing year, rating and feedback]

### Other HR Notes
Volunteering activities
Certifications
Focus groups
Achievements or recognitions

Ensure diverse names, realistic career backgrounds, and varying seniority levels (Junior, Senior, Staff, Director). Generate 25 separate files <employee full name>.md in 'employees' folder using your file tool"""

contract_prompt = """You are a Corporate Legal Counsel AI agent specializing in technology and AI enterprise procurement. 
Your task is to generate 10 distinct, highly realistic legal contract summaries and metadata sheets for "Aethel AI" in Markdown format (named `<contract_name>.md`) in contracts folder.

The 15 contracts should be a mix of:
* 5 x Enterprise Customer SaaS/MLA (Master License Agreements)
* 5 x Vendor/Cloud Infrastructure Agreements (e.g., compute/GPU clusters, data providers)
* 5 x NDAs / Partnership / AI Research Collaboration Agreements

For each contract, generate a Markdown document using this exact template:

# Contract Reference: [e.g., AE-CON-2026-001]
**Contract Type:** [e.g., Enterprise Master License Agreement]
**Counterparty:** [Fictitious Company Name, e.g., NexusCorp Logistics]
**Effective Date:** [Date in 2025/2026] | **Expiration Date:** [Date]
---
### 1. Executive Summary
[Brief overview of the scope of work, seats licensed, or compute power provisioned.]

### 2. Financial Terms & Value
* **Total Contract Value (TCV):** [$XX,XXX - $X,XXX,XXX]
* **Payment Terms:** [e.g., Net 30, Annual Upfront]

### 3. Key AI/Data Clauses
* **Data Ownership:** [Specify if counterparty retains data data ownership or if Aethel AI can use it for model training.]
* **IP Rights:** [Details on who owns derivative models or fine-tuned weights.]

### 4. Support
* **Onboarding:** [Specify any onboarding support agreed]
* **Technical Support:** [Support contract details including contact details, SLAs, FAQ, User guides]

### 4. Termination & Liability
[Standard high-level legal guardrails regarding data breaches or SLA failures.]

Generate all 15 contract documents sequentially, ensuring varied financial figures, realistic counterparty names, and legally plausible AI data clauses.
Write the files to 'contracts' folder using your file tools"""


gentest_prompt = """
You are an expert synthetic dataset generator for RAG systems. Your task is to generate a high-quality evaluation dataset based *only* on the provided text appended below. Write the generated test dataset to test<i>.jsonl using your file management tools.

## Output Format
Output your response strictly as raw JSONL (one JSON object per line) directly in your chat response. Do NOT use markdown code blocks (no ```), do NOT write introductory or concluding text, and do NOT include blank lines.

Each line must match this exact schema:
{"question": "...", "keywords": ["...", "..."], "reference_answer": "...", "category": "..."}

## Generation Rules

### 1. Questions & Answers
*   **Source strictly**: Use only facts explicitly stated in the document. No hallucinations or outside knowledge.
*   **No duplicates**: Ensure each question has a unique semantic intent.
*   **Answer completeness**: The `reference_answer` must be fully detailed, factually exact, and entirely self-contained. 
*   **Keywords**: Provide 2 to 3 high-value retrieval terms (names, dates, acronyms, or specific concepts) per question.

### 2. Categories
Assign exactly one of these categories to each object:
*   **`direct_fact`**: Single lookup from one location.
*   **`temporal`**: Timelines, dates, sequencing, or durations.
*   **`comparative`**: Compares entities, values, or features.
*   **`holistic`**: Summaries or high-level overviews of sections.
*   **`spanning`**: Combines facts from multiple independent parts of the text.
*   **`relationship`**: Explores dependencies, hierarchies, or cause-and-effect.

### 3. Diversity Mix
Generate a balanced variety across all categories, ensuring deep coverage of the entire document. Maximize the number of unique evaluation examples the text can reasonably support.

The document content is added below. No need to read from any file.
---
DOCUMENT CONTENT:
[DOCUMENT_TEXT]

"""
