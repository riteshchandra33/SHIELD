import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "/home/user/SHIELD/resume/Ritesh_Somashekar_AI_ML_Engineer_GMU_Carelon.docx"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.left_margin = sec.right_margin = Inches(0.2)
sec.top_margin = Inches(0.25)
sec.bottom_margin = Inches(0.3)
TEXT_W = Inches(8.5 - 0.4)

st = doc.styles["Normal"]
st.font.name = "Calibri"
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(0)
st.paragraph_format.space_before = Pt(0)
st.paragraph_format.line_spacing = 1.0


def runs(p, text, size=11, italic=False):
    """Add text where **x** is bold and *x* is italic."""
    for part in re.split(r"(\*\*.+?\*\*|\*.+?\*)", text):
        if not part:
            continue
        bold = part.startswith("**")
        ital = italic or (part.startswith("*") and not bold)
        r = p.add_run(part.strip("*") if (bold or ital and part.startswith("*")) else part)
        r.bold, r.italic = bold, ital
        r.font.size = Pt(size)
    return p


def bottom_border(p):
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", "6"), ("space", "1"), ("color", "808080")):
        b.set(qn("w:" + k), v)
    bdr.append(b)
    pPr.append(bdr)


def centered(text, size, bold=True):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.bold, r.font.size = bold, Pt(size)
    return p


def heading(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    r.bold, r.font.size = True, Pt(14)
    bottom_border(p)


def bullet(text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Inches(0.33)
    pf.first_line_indent = Inches(-0.23)
    pf.tab_stops.add_tab_stop(Inches(0.33))
    pf.space_after = Pt(1)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run("•\t").font.size = Pt(11)
    runs(p, text)


def skill(label, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.1)
    p.paragraph_format.space_after = Pt(3)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    runs(p, f"**{label}:** {text}")


def job(company, role, right):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.tab_stops.add_tab_stop(TEXT_W - Inches(0.05), WD_TAB_ALIGNMENT.RIGHT)
    r = p.add_run(company + " ")
    r.bold, r.font.size = True, Pt(12)
    r = p.add_run("| ")
    r.bold = True
    r = p.add_run(role)
    r.bold = r.italic = True
    r = p.add_run("\t" + right)
    r.bold = True


# ---------------- Header ----------------
centered("Ritesh Somashekar", 18)
centered("AI & ML Engineer", 14)
LINKEDIN = "https://www.linkedin.com/in/ritesh-somashekar-0497aa182/"


def hyperlink(p, url, text, size):
    """Add a clickable link whose visible text stays readable to ATS parsers."""
    rid = p.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                           is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), rid)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    for tag, val in (("w:color", "0563C1"), ("w:u", "single"), ("w:sz", str(size * 2))):
        e = OxmlElement(tag)
        e.set(qn("w:val"), val)
        rpr.append(e)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    r.append(t)
    h.append(r)
    p._p.append(h)


p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Fairfax, VA | (571) 245-7770 | ").font.size = Pt(11)
hyperlink(p, "mailto:ritesh.chandra33@gmail.com", "ritesh.chandra33@gmail.com", 11)
p.add_run(" | ").font.size = Pt(11)
hyperlink(p, LINKEDIN, "LinkedIn", 11)

# ---------------- Summary ----------------
heading("PROFESSIONAL SUMMARY")
bullet("**AI & ML Engineer** with **5+ years** of experience growing from **data engineering** to **machine learning** and "
       "**Generative AI**, now building **RAG systems** and **LLM applications**; published at **ACM WSDM '26** and **IEEE PST 2026**.")
bullet("Built healthcare data and ML pipelines at **Carelon Global Solutions**, then led RAG data, retrieval, and validation work at "
       "**George Mason University** using **Python, Llama 3, LlamaIndex, ChromaDB, PyTorch,** and **AWS**.")
bullet("Proven results: **RAG recall@10 raised from 61% to 88%**, a **3.0% LLM hallucination rate**, **99.9% pipeline reliability**, "
       "and **60% faster model training**.")

# ---------------- Skills ----------------
heading("TECHNICAL SKILLS")
skill("Programming", "Python, SQL, R, Java")
skill("Generative AI & RAG", "Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), LlamaIndex, Prompt Engineering, "
      "Embeddings, Vector Databases (ChromaDB, pgvector, FAISS), Llama 3, Ollama, Agentic AI, LoRA/PEFT")
skill("LLM Evaluation", "RAGAS, Recall@K, Hallucination Detection, Guardrails, Ablation Studies, A/B Testing")
skill("Machine Learning & NLP", "PyTorch, TensorFlow, Scikit-learn, Hugging Face Transformers, BERT, XGBoost, LightGBM, SHAP, "
      "Anomaly Detection, Time Series Forecasting")
skill("MLOps", "MLflow, Docker, Kubernetes, FastAPI, CI/CD (Jenkins), Git, DVC")
skill("Data Engineering", "Apache Airflow, Apache Spark, PySpark, Kafka, Databricks, Snowflake, Delta Lake, Hadoop, SQL Server, MongoDB")
skill("Cloud & BI", "AWS (S3, Lambda, Glue, SageMaker, SQS), Azure, Tableau, Power BI")

# ---------------- Education ----------------
heading("EDUCATION")
for line in ["**Master's in Data Analytics and Engineering** | George Mason University, Fairfax, VA, USA | GPA: 3.93/4.0",
             "**Bachelor's in Information Science and Engineering** | Visvesvaraya Technological University, Bengaluru, India"]:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.1)
    p.paragraph_format.space_after = Pt(3)
    runs(p, line)

# ---------------- Experience ----------------
# Each bullet follows STAR: situation/task -> action (with tools) -> measurable result.
heading("PROFESSIONAL EXPERIENCE")
job("George Mason University", "AI & ML Research Associate", "Fairfax, VA | August 2024 - Present")
for b in [
    "To scale 9-1-1 call-taker training beyond instructor role-play, co-developed **SHIELD** with **Fairfax County DPSC**, an "
    "**LLM-agent** platform that simulates calls and coaches trainees in real time; published at **ACM WSDM '26**.",
    "To generate safe training calls without commercial APIs, co-developed **MATE-911**, a **RAG** system on **Llama 3.1 8B** that "
    "achieved **0.81 protocol F1** and a **3.0% hallucination rate**; published at **IEEE PST 2026**.",
    "Facing unstructured, abbreviation-heavy call records, led the **RAG knowledge base and data pipeline** (OCR, cleaning, "
    "chunking) for **160 gold-standard scenarios**, cutting hallucinations from **13.0% to 3.0%**.",
    "To ground generation in verified protocols, built the **retrieval layer** with **Sentence Transformers** embeddings, "
    "**ChromaDB**, and metadata-filtered **top-K retrieval**, raising the pass rate from **49.7% to 97.6%**.",
    "To support live training sessions, engineered **prompt and context assembly** for **Llama 3.1 8B (Ollama)**, delivering "
    "responses in under **1 second** for text and **1.3 seconds** for voice.",
    "To keep unsafe content away from trainees, led the **validation layer** with **ontology-based guardrails** and **NLI "
    "hallucination checks** against NENA protocols, lowering hallucinations from **9.5% to 3.0%**.",
    "To speed up literature search, built a **RAG research assistant** with **LlamaIndex, pgvector,** and **FAISS**, raising "
    "**recall@10 from 61% to 88%** (RAGAS-evaluated) for **40+ researchers** at **190 ms p95** latency.",
    "To make model decisions explainable, applied **SHAP** to intent classification and behavioral **anomaly detection** models, "
    "tuning **LightGBM** alert thresholds to cut false positives by **25%**.",
    "To run LLMs on limited hardware, fine-tuned **Llama 3** with **LoRA/PEFT** and **quantization-aware training**, shrinking "
    "models by **40%** while staying within **3%** of full-precision accuracy.",
    "To move prototypes into production, set up **MLflow** tracking, **FastAPI** services, **Docker**, and **CI/CD**, cutting "
    "release cycles from **2 weeks to 5 days** with **A/B testing**.",
    "To study community coping during disasters, applied **graph analytics** and **ensemble models** on the **ORC Hopper HPC "
    "cluster**, forecasting trends with an **RMSE of 0.89**.",
]:
    bullet(b)

job("Carelon Global Solutions (Elevance Health)", "Machine Learning Engineer", "Bengaluru, India | May 2022 - August 2023")
for b in [
    "To automate clinical text review, built **BERT/BioBERT** entity-extraction models on unstructured medical notes, reaching "
    "**80% accuracy** and cutting processing time by **55%**.",
    "To improve prediction quality, tuned **Scikit-learn** and **XGBoost** models through feature engineering and hyperparameter "
    "search, raising accuracy by **8%** and cutting training time by **15%**.",
    "To serve models reliably, containerized inference services with **Docker, Kubernetes,** and **Jenkins CI/CD**, improving "
    "uptime by **20%** and enabling real-time EHR integration via **REST APIs**.",
    "To speed up model training, built ingestion of **400K+ XML/JSON healthcare records** into **Snowflake** and **Databricks**, "
    "accelerating training by **60%** and cutting preprocessing time by **70%**.",
    "To fix inaccurate provider data feeding ML models, automated daily **NPPES** ingestion in **Python**, improving data accuracy "
    "by **74%** and reducing processing overhead by **60%**.",
    "To support ML at scale, designed **20+ ETL pipelines** with **Airflow, PySpark,** and **AWS (S3, Lambda, Glue)**, raising "
    "throughput by **70%** and reaching **99.9% reliability** under **HIPAA**.",
]:
    bullet(b)

job("Carelon Global Solutions (Elevance Health)", "Data Engineer", "Bengaluru, India | October 2020 - April 2022")
for b in [
    "To reduce manual claims reconciliation, redesigned **claims-balancing ETL workflows** in **Python** and **SQL**, cutting "
    "operational overhead by **60%**.",
    "To eliminate costly invoice errors, automated **medical invoice processing** pipelines with rule-based classification, "
    "reducing manual errors by **70%**.",
    "To give business teams faster insights, delivered self-service **Tableau** and **Power BI** reporting pipelines, cutting "
    "reporting latency by **40%**.",
    "To handle growing data volumes, migrated **Hive** and **Hadoop** workloads to **Apache Spark** and **Azure Data Services**, "
    "improving processing speed and scalability.",
]:
    bullet(b)

# ---------------- Projects ----------------
heading("PROJECTS")
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(2)
runs(p, "**Agentic AI Ticket Automation System** | SecureGPT, LLaMA, AWS SQS, JIRA")
bullet("To cut security-ticket triage time, built an **agentic AI** system with **SecureGPT** and **LLaMA** on **AWS SQS** that "
       "classifies threats and auto-creates **JIRA** tickets, reaching **93% accuracy** and **70%** faster triage.")

# ---------------- Publications ----------------
heading("PUBLICATIONS")
for pub in [
    "R. S. Nayaka, **R. Somashekar**, K. B. Laskey, L. Wells II, H. Purohit. \"SHIELD: A Framework for Online Conversational AI "
    "System for Self-Regulated Learning at Emergency Communications Centers.\" *ACM WSDM '26*. doi:10.1145/3773966.3779411",
    "R. S. Nayaka, **R. Somashekar**, H. Purohit. \"MATE-911: Multimodal AI-powered Training Environment for Next-Generation "
    "911 Dispatcher Preparedness.\" *IEEE PST 2026*.",
]:
    bullet(pub)

doc.core_properties.author = "Ritesh Somashekar"
doc.core_properties.title = "Ritesh Somashekar - AI & ML Engineer Resume"
doc.core_properties.keywords = "AI Engineer, Machine Learning Engineer, RAG, LLM, Generative AI, Data Engineer"
doc.save(OUT)
print("saved", OUT)
