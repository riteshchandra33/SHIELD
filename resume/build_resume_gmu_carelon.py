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
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Fairfax, VA | (571) 245-7770 | ").font.size = Pt(12)
r = p.add_run("ritesh.chandra33@gmail.com")
r.font.size, r.font.underline = Pt(12), True
r.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
p.add_run(" | LinkedIn").font.size = Pt(12)

# ---------------- Summary ----------------
heading("PROFESSIONAL SUMMARY")
bullet("**AI & Machine Learning Engineer** with **5+ years** of experience building **LLM and RAG systems**, **NLP models**, and "
       "**enterprise data pipelines** across healthcare and public-safety domains. Published researcher (**ACM WSDM ’26**, **IEEE PST 2026**) with "
       "hands-on expertise in **Llama 3, ChromaDB, Hugging Face, PyTorch, and Scikit-learn**, and in **hallucination detection, "
       "ontology-based validation, and LLM evaluation**.")
bullet("Strong background in **data engineering** with **Apache Airflow, Spark/PySpark, Snowflake, and Databricks**, and **cloud "
       "pipelines on AWS (S3, Lambda, Athena, Glue, SageMaker)** and **Azure**, with a focus on **HIPAA-compliant** healthcare data. "
       "Experienced in **MLOps** using **MLflow, Docker, Kubernetes, FastAPI,** and **CI/CD pipelines**.")
bullet("Demonstrated impact, including a **0.81 protocol F1 with a 3.0% hallucination rate** for RAG-generated scenarios, **99.9% "
       "pipeline reliability**, **74% higher data accuracy**, and **60% faster model training**. Adept at collaborating with "
       "researchers, public agencies, and business stakeholders to deliver **end-to-end AI solutions** from research to production.")

# ---------------- Skills ----------------
heading("TECHNICAL SKILLS")
skill("Programming & Scripting", "Python (NumPy, pandas, scikit-learn, PyTorch, TensorFlow), SQL, R, Scala, Java, Bash")
skill("Generative AI & LLMs", "Llama 3/3.1, Ollama, Retrieval-Augmented Generation (RAG), Prompt Engineering, Agentic AI, "
      "Vector Databases (ChromaDB, FAISS), Sentence Transformers, LoRA, Quantization-Aware Training (QAT)")
skill("LLM Evaluation & Safety", "Hallucination Detection, Ontology-Based Validation, NLI-Based Validation, Semantic Similarity "
      "Scoring, Ablation Studies, Protocol F1, Confidence Scoring")
skill("Machine Learning & NLP", "Supervised & Unsupervised Learning, Transformers, BERT, BioBERT, Hugging Face, XGBoost, LightGBM, "
      "Graph Analytics, Ensemble Models, Time Series Forecasting, Anomaly Detection, Feature Engineering, Model Explainability (SHAP)")
skill("MLOps & ML Infrastructure", "MLflow, Docker, Kubernetes, Jenkins, CI/CD, FastAPI, Git, DVC, Model Deployment")
skill("Data Engineering & Big Data", "Apache Airflow, Apache Spark, PySpark, Kafka, Databricks, Snowflake, Delta Lake, Hadoop, Hive, "
      "Sqoop, Informatica PowerCenter, Precisely Data360, SQL Server, MySQL, MongoDB")
skill("Cloud Platforms", "AWS (S3, Lambda, Athena, Glue, SageMaker, SQS), Azure (Data Services, Stream Analytics)")
skill("Data Analysis & Visualization", "Tableau, Power BI (DAX), Excel (VBA, Formulas), Statistical Analysis, Data Lineage")

# ---------------- Education ----------------
heading("EDUCATION")
for line in ["**Master’s in Data Analytics and Engineering** | George Mason University, Fairfax, VA, USA | GPA: 3.93/4.0",
             "**Bachelor’s in Information Science and Engineering** | Visvesvaraya Technological University, Bengaluru, Karnataka, India."]:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.1)
    p.paragraph_format.space_after = Pt(3)
    runs(p, line)

# ---------------- Experience ----------------
heading("PROFESSIONAL EXPERIENCE")
job("George Mason University", "Graduate Research Assistant (AI/ML)", "Fairfax, VA | August 2024 – Present")
for b in [
    "Co-developed **SHIELD**, an online conversational AI training platform for 9-1-1 call-takers built with **Fairfax County "
    "DPSC**, using **LLM agents** to generate call scenarios from CAD data, deliver **real-time metacognitive nudges**, and produce "
    "post-call reflection analytics; published at **ACM WSDM ’26**.",
    "**Led the data pipeline for both SHIELD and MATE-911** in **Python**, covering OCR parsing, abbreviation expansion, "
    "completeness checks, segmentation, standardization, and **ChromaDB** embedding of **160 gold-standard emergency scenarios** "
    "across accident, fire, medical, and alarm incidents.",
    "**Led the validation layer for both platforms**, building a **911 ontology validator** derived from **NENA** standards and "
    "DPSC procedures that combines rule-based and **LLM-based semantic checks** for unsafe content, protocol compliance, and "
    "**hallucination detection**, with PASS/REVIEW/FAIL confidence scoring and an **85% cosine-similarity** quality gate.",
    "Co-developed **MATE-911** (published at **IEEE PST 2026**), a multimodal **RAG** system using **Llama 3.1 8B (Ollama)**, **ChromaDB**, and **all-mpnet-base-v2** "
    "embeddings to generate protocol-grounded voice and text scenarios on commodity hardware, achieving **0.81 protocol F1**, a "
    "**3.0% hallucination rate**, a **97.6% pass rate**, and **sub-2-second latency**.",
    "Ran **ablation studies** showing RAG retrieval drives scenario quality (**F1 0.81 vs. 0.59** without it) and ontology "
    "validation acts as a safety guardrail, cutting hallucinations from **9.5% to 3.0%**.",
    "Built real-time **trace-log analytics** (event streams, Task Completion Rate, Average Field Latency, goal-alignment scoring) "
    "that feed an instructor **performance dashboard** for adaptive feedback.",
    "Applied **graph-based analytics** and **ensemble models** to large-scale disaster datasets on the **ORC Hopper HPC cluster** to "
    "forecast community coping trends with an **RMSE of 0.89**, visualizing findings in **R** and **Tableau**.",
    "Implemented **model explainability** using **SHAP** to surface the drivers behind ensemble-model predictions, supporting "
    "model governance, risk assessment, and documentation for research stakeholders.",
    "Fine-tuned **Llama 3** and transformer models using **LoRA/PEFT** and **Quantization-Aware Training (QAT)**, reducing model "
    "size by **40%** while keeping accuracy within **3%** of full-precision benchmarks.",
    "Established **MLflow** experiment tracking and model registry for LLM and RAG experiments, logging parameters, prompts, and "
    "evaluation metrics to make every run reproducible and comparable across model versions.",
    "Took models from **proof of concept to production** by serving them through **FastAPI** and **Docker** with **CI/CD**, reducing "
    "release cycles from **2 weeks to 5 days** and enabling **A/B testing** and pre/post-deployment evaluation of model versions.",
]:
    bullet(b)

job("Carelon Global Solutions (Elevance Health)", "Data Engineer",
    "Bengaluru, India | May 2022 – August 2023")
for b in [
    "Designed and managed **20+ enterprise ETL pipelines**, boosting data throughput by **70%** and ensuring high availability for "
    "downstream AI/BI applications.",
    "Automated workflows with **Apache Airflow, Python,** and **AWS (S3, Lambda, Athena)**, achieving **99.9% pipeline "
    "reliability** with end-to-end lineage tracking.",
    "Built a daily ingestion workflow from **NPPES** repositories, improving data accuracy by **74%** and cutting processing "
    "overhead by **60%**.",
    "Engineered ingestion pipelines for **400K+ XML/JSON healthcare records** into **Snowflake** and **Databricks**, accelerating "
    "model training by **60%** and reducing preprocessing time by **70%**.",
    "Built NLP models using **BERT** and **BioBERT** for clinical entity extraction from unstructured medical text, achieving "
    "**80% accuracy** and reducing processing time by **55%**.",
    "Built scalable **PySpark** ETL on **AWS (Glue, SageMaker)** with **Delta Lake**, improving data reliability by **30%** under "
    "**HIPAA**, and improved **Scikit-learn/XGBoost** models, increasing accuracy by **8%** and cutting training time by **15%**.",
    "Containerized ML inference services with **Docker, Kubernetes,** and **Jenkins CI/CD**, improving system uptime by **20%** "
    "and enabling real-time EHR integration via **REST APIs**.",
    "Delivered self-service BI pipelines integrating **Tableau, Power BI,** and SQL-based models, reducing reporting latency by "
    "**40%** and enabling anomaly detection for healthcare analytics.",
]:
    bullet(b)

job("Carelon Global Solutions (Elevance Health)", "Associate Data Analyst", "Bengaluru, India | October 2020 – April 2022")
for b in [
    "Partnered with stakeholders on the **Seven Plus Locations** project to align ETL pipelines with business KPIs, improving "
    "claims data accuracy and driving cost savings.",
    "Redesigned **claims-balancing ETL workflows**, improving provider insights and reducing operational overhead by **60%**.",
    "Automated **medical invoice processing** pipelines, cutting manual errors by **70%** and improving the reliability of "
    "financial reporting.",
    "Migrated large-scale processing workloads from **Hive** to **Apache Spark/PySpark**, and moved **Sqoop/Hadoop** ingestion to "
    "**Azure Data Services**, improving performance, scalability, and pipeline efficiency.",
    "Developed **RESTful microservices** with **OAuth 2.0** and API versioning, and designed **MongoDB** data models with "
    "**Python/Java** validation scripts (UDFs) to improve data quality and consistency.",
]:
    bullet(b)

# ---------------- Publications ----------------
heading("PUBLICATIONS")
for pub in [
    "R. S. Nayaka, **R. Somashekar**, K. B. Laskey, L. Wells II, and H. Purohit. “SHIELD: A Framework for Online Conversational AI "
    "System for Self-Regulated Learning at Emergency Communications Centers.” In *Proceedings of the 19th ACM International "
    "Conference on Web Search and Data Mining (WSDM ’26)*, Boise, ID, 2026. doi:10.1145/3773966.3779411",
    "R. S. Nayaka, **R. Somashekar**, and H. Purohit. “MATE-911: Multimodal AI-powered Training Environment for Next-Generation "
    "911 Dispatcher Preparedness.” In *IEEE PST Conference*, 2026.",
]:
    bullet(pub)

doc.core_properties.author = "Ritesh Somashekar"
doc.save(OUT)
print("saved", OUT)
