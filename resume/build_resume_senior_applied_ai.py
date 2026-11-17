"""Builds the AI & ML Engineer resume (Resume 2 layout) tuned for a Senior Applied AI Engineer role."""
import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "/home/user/SHIELD/resume/Ritesh_Somashekar_AI_ML_Engineer_Senior_Applied_AI.docx"
LINK_BLUE = RGBColor(0x05, 0x63, 0xC1)

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.left_margin = sec.right_margin = Inches(0.28)
sec.top_margin = Inches(0.4)
sec.bottom_margin = Inches(0.35)
TEXT_W = Inches(8.5 - 0.56)

st = doc.styles["Normal"]
st.font.name = "Calibri"
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(0)
st.paragraph_format.space_before = Pt(0)
st.paragraph_format.line_spacing = 1.0


def runs(p, text, size=11):
    """Add text where **x** is bold and *x* is italic."""
    for part in re.split(r"(\*\*.+?\*\*|\*.+?\*)", text):
        if not part:
            continue
        bold = part.startswith("**")
        ital = part.startswith("*") and not bold
        r = p.add_run(part.strip("*") if (bold or ital) else part)
        r.bold, r.italic = bold, ital
        r.font.size = Pt(size)
    return p


def bottom_border(p):
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", "8"), ("space", "1"), ("color", "000000")):
        b.set(qn("w:" + k), v)
    bdr.append(b)
    pPr.insert(0, bdr)


def centered(text, size):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.bold, r.font.size = True, Pt(size)


def heading(text):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.bold, r.font.size = True, Pt(14)
    bottom_border(p)


def bullet(text, after=3, spacing=1.0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing = spacing
    pf.left_indent = Inches(0.25)
    pf.first_line_indent = Inches(-0.25)
    pf.tab_stops.add_tab_stop(Inches(0.25))
    pf.space_after = Pt(after)
    p.add_run("•\t")
    runs(p, text)


def skill(label, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    runs(p, f"**{label}:** {text}")


def job(left, right):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.tab_stops.add_tab_stop(TEXT_W, WD_TAB_ALIGNMENT.RIGHT)
    r = p.add_run(f"{left}\t{right}")
    r.bold, r.font.size = True, Pt(12.5)


LINKEDIN = "https://www.linkedin.com/in/ritesh-somashekar-0497aa182"


def hyperlink(p, url, text):
    """Clickable link whose visible text stays readable to ATS parsers."""
    rid = p.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                           is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), rid)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    for tag, val in (("w:color", "0563C1"), ("w:u", "single")):
        e = OxmlElement(tag)
        e.set(qn("w:val"), val)
        rpr.append(e)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    r.append(t)
    h.append(r)
    p._p.append(h)


# ---------------- Header ----------------
centered("Ritesh Somashekar", 18)
centered("AI & ML Engineer", 14)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Fairfax, VA | ")
hyperlink(p, "mailto:ritesh.chandra33@gmail.com", "ritesh.chandra33@gmail.com")
p.add_run(" | (571) 245-7770 | ")
hyperlink(p, LINKEDIN, "LinkedIn")

# ---------------- Summary ----------------
heading("PROFESSIONAL SUMMARY")
bullet("**AI/ML Engineer** with **6+ years** progressing from **data engineering** to **production AI**, building **Generative AI, RAG, "
       "and agentic systems** with **Python, Spark, PyTorch,** and **LangChain**; published at **ACM WSDM '26** and **IEEE PST 2026**.", 3, 1.15)
bullet("Proven impact: **RAG recall from 61% to 88%**, **LLM hallucinations cut from 9.5% to 3.0%** with **guardrails**, **93% "
       "automation accuracy** from a **multi-agent workflow**, and **deployment cycles cut 79%**.", 3, 1.15)
bullet("Specialized in **multi-agent and agentic workflows**, **AI evaluation and guardrails**, **LoRA/PEFT fine-tuning**, **MLflow, "
       "Docker, Kubernetes,** and **CI/CD**, shipping AI features from requirements to production.", 3, 1.15)

# ---------------- Skills ----------------
heading("TECHNICAL SKILLS")
skill("Agentic AI & LLMs", "Multi-Agent Workflows, Agentic AI, LLM Agents, Retrieval-Augmented Generation (RAG), Prompt Engineering, "
      "Structured Outputs, Transformers, LoRA/PEFT Fine-Tuning, RLHF, Direct Preference Optimization (DPO)")
skill("AI Evaluation & Guardrails", "LLM Evaluation, RAGAS, A/B Testing, Hallucination Detection, AI Guardrails, Ontology-Based "
      "Validation, Ablation Studies, Model Monitoring")
skill("Languages & Frameworks", "Python, SQL, PyTorch, TensorFlow, Scikit-learn, Hugging Face Transformers, LangChain, LlamaIndex, "
      "XGBoost, LightGBM, Pandas, NumPy, Deep Learning, NLP, Anomaly Detection")
skill("Big Data & Spark", "Apache Spark, PySpark, Apache Kafka, Apache Flink, Apache Airflow, Databricks, dbt, ETL/ELT Pipelines, Hadoop")
skill("MLOps & CI/CD", "Docker, Kubernetes, CI/CD Pipelines, GitHub Actions, MLflow, Kubeflow, Experiment Tracking, Model Serving "
      "(FastAPI, Flask), Terraform")
skill("Cloud Platforms", "AWS (SageMaker, S3, Lambda, EventBridge, SQS, CloudWatch, EC2, Glue, EKS), Azure (Azure ML, Azure OpenAI, "
      "Data Factory), Snowflake")
skill("Vector Search & Tools", "FAISS, pgvector, Pinecone, ChromaDB, Git, Linux/Unix, Jupyter, REST APIs, Jira, ELK Stack")

# ---------------- Experience ----------------
heading("PROFESSIONAL EXPERIENCE")
job("Apple | AI/ML Engineer", "CA | May 2025 - Present")
for b in [
    "Engineered real-time data pipelines using **Apache Spark, Flink,** and **Kafka** to ingest and preprocess customer support and "
    "interaction data, feeding downstream NLP models and improving pipeline **throughput by 26%**.",
    "Built **RAG-based retrieval systems** using **LangChain**, embedding models, and **vector databases (FAISS)** to ground **GPT-4, "
    "Claude,** and **Gemini** outputs in verified sources, boosting response **accuracy by 16%** for customer-facing queries.",
    "Fine-tuned **transformer models** with **PyTorch** and **AXLearn**, applying **LoRA, PEFT,** and **knowledge distillation** for "
    "intent classification and ticket routing, cutting model size **36%** while holding **87%+ task accuracy**.",
    "Shipped **production LLM applications** for customer service automation using **prompt engineering**, **structured outputs**, and "
    "**output guardrails**, reducing hallucination rate **19%** and average response latency **20%**.",
    "Designed an **AI evaluation framework** with **A/B testing** to benchmark LLM output quality pre/post-deployment, informing prompt "
    "and retrieval tuning decisions across **cross-functional** product teams.",
    "Automated **CI/CD** release workflows with **MLflow, Docker,** and **GitHub Actions**, and applied **Differential Privacy** and "
    "**Federated Learning** for on-device personalization.",
]:
    bullet(b)

job("George Mason University | Graduate Research Assistant (Applied ML)", "VA | August 2024 - Present")
for b in [
    "Co-developed **SHIELD** (published at **ACM WSDM '26**), a conversational AI platform built with Fairfax County's 9-1-1 center "
    "where **LLM agents** simulate emergency calls and coach trainees with real-time feedback.",
    "Co-developed **MATE-911** (published at **IEEE PST 2026**), a **RAG** system on **Llama 3.1 8B**, and led its **guardrails** and "
    "validation layer, cutting hallucinations from **9.5% to 3.0%** at **0.81 protocol F1**.",
    "Built a **multi-agent** ticket workflow on **AWS (Lambda, EventBridge, SQS, S3, CloudWatch)** where **SecureGPT** and **LLaMA** "
    "agents categorize, track SLAs, and escalate Jira tickets, reaching **93% automation accuracy** and **70%** faster triage.",
    "Built a biomedical data pipeline with **Python, SQL, AWS S3,** and **DVC** curating **30K+ publications**, and fine-tuned "
    "**BioBERT** with **PEFT/LoRA** and **Optuna**, improving NER F1 by **18 points** over spaCy.",
    "Developed and deployed a **RAG** research assistant with **LlamaIndex, pgvector, FAISS, FastAPI,** and **Docker**, raising "
    "**recall@10 from 61% to 88%** for **40+ researchers** at about **190ms p95 latency**.",
    "Established reproducible evaluation with **MLflow, DVC, RAGAS,** and **Git-based CI/CD**, cutting iteration cycles from **3 "
    "days to 16 hours**, with protocols adopted by **two follow-on LLM studies**.",
]:
    bullet(b)

job("Accenture | Machine Learning Engineer", "India | September 2020 - July 2023")
for b in [
    "Designed a **Generative AI** customer support solution leveraging **NLP, Azure OpenAI LLMs,** and **RAG architecture** for a retail "
    "client, handling **15K+ daily queries** across web and mobile platforms while improving automated query resolution.",
    "Engineered scalable data pipelines using **PySpark** and **Databricks** to process **500GB+** of structured and unstructured data, "
    "accelerating feature engineering workflows and reducing processing time by **45%** for downstream ML applications.",
    "Integrated **RAG** workflows with **LangChain**, vector embeddings, and **Pinecone**, reducing customer response resolution time "
    "by **38%** and increasing support ticket deflection by **25%**.",
    "Developed predictive ML models using **Python, Scikit-learn,** and **XGBoost** for demand forecasting across **10+ product "
    "categories**, delivering a **22% improvement in forecast accuracy** through feature optimization and model tuning.",
    "Orchestrated scalable production workflows using **MLOps** frameworks with **Docker, Kubernetes, MLflow,** and **AWS SageMaker**, "
    "accelerating the model deployment lifecycle from **2 weeks to 3 days**.",
    "Established continuous **model monitoring**, **drift detection**, and automated retraining pipelines to maintain **95%+ "
    "production accuracy** over **12 months**, delivering reliable AI solutions adopted by **200+ end users**.",
]:
    bullet(b)

job("Honeywell | Data Engineer", "India | January 2019 - September 2020")
for b in [
    "Engineered **ETL/ELT pipelines** for industrial IoT analytics using **Python, PySpark,** and **Apache Spark**, ingesting telemetry "
    "from **8+ source systems** via REST APIs and processing **2M+ records daily** into **Azure Data Lake**.",
    "Automated batch data workflows with **Azure Data Factory** and **Apache Airflow**, implementing source-to-target mapping and "
    "monitoring across **15+ daily jobs**, cutting issue detection time to **under 15 minutes**.",
    "Implemented **data quality frameworks**, including null checks, duplicate detection, schema validation, and anomaly detection, "
    "reducing downstream reporting errors by **40%** across **3 plant sites**.",
    "Designed a **dimensional data warehouse** using **star schema** for asset uptime and operational KPIs, cutting report turnaround "
    "time by **60%** across **5 operational teams**.",
    "Built reusable **SQL Server** transformation logic using **dbt** for data cleansing, normalization, joins, and reconciliation, "
    "improving data prep efficiency by **35%**.",
    "Managed production deployments using **Git, CI/CD,** and Linux shell scripting, archived raw telemetry in **AWS S3**, and "
    "partnered with Power BI developers on **3 on-time dashboard releases**.",
]:
    bullet(b)

# ---------------- Education ----------------
heading("EDUCATION")
for degree, school in [("Masters in Data Analytics and Engineering,", "George Mason University - Fairfax, VA, USA."),
                       ("Bachelors in Information Science and Engineering,",
                        "Visvesvaraya Technological University - Bengaluru, Karnataka, India.")]:
    for text, bold in ((degree, True), (school, False)):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        if bold:
            p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = bold

doc.core_properties.author = "Ritesh Somashekar"
doc.core_properties.title = "Ritesh Somashekar - AI & ML Engineer Resume"
doc.core_properties.keywords = "AI Engineer, Applied AI, Agentic AI, Multi-Agent, Guardrails, AI Evaluation, Python, Spark, CI/CD, LLM"
doc.save(OUT)
print("saved", OUT)
