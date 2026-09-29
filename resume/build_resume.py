import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "/home/user/SHIELD/resume/Ritesh_Somashekar_Python_UI_Developer.docx"

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
    """Add text where **x** is bold."""
    for i, part in enumerate(re.split(r"\*\*(.+?)\*\*", text)):
        if part:
            r = p.add_run(part)
            r.bold = i % 2 == 1
            r.italic = italic
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
centered("Python/UI Developer", 14)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Fairfax, VA | (571) 245-7770 | ").font.size = Pt(12)
r = p.add_run("ritesh.chandra33@gmail.com")
r.font.size, r.font.underline = Pt(12), True
r.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
p.add_run(" | LinkedIn").font.size = Pt(12)

# ---------------- Summary ----------------
heading("PROFESSIONAL SUMMARY")
bullet("**Python/UI Developer** with **6+ years** of experience enhancing and modernizing enterprise platforms, building "
       "**modern, scalable web user interfaces**, **distributed data-processing pipelines**, and **containerized applications** "
       "using **Python, Java, React, and FastAPI**. Proven expertise in **access control and authorization (OAuth 2.0, RBAC)**, "
       "**job queuing and scheduling**, and **workflow orchestration (Apache Airflow)**.")
bullet("Strong background in **profiling and optimizing long-running compute workloads** with **Apache Spark and PySpark**, "
       "defining **performance metrics and statistics**, and refactoring orchestration logic to improve **execution efficiency "
       "and throughput**. Experienced in **Docker, Kubernetes, and CI/CD pipelines** on **AWS** and **Azure**, delivering secure, "
       "**HIPAA-compliant** systems.")
bullet("Demonstrated success in **redesigning UI architecture** to improve **information hierarchy, usability, consistency, and "
       "layout** across functional modules. Adept at **technical design discussions, code reviews, and technical documentation**, "
       "collaborating effectively across engineering, product, and research teams.")

# ---------------- Skills ----------------
heading("TECHNICAL SKILLS")
skill("Programming & Scripting", "Python (pandas, NumPy, asyncio), Java, JavaScript, TypeScript, SQL (PostgreSQL, Oracle), Bash")
skill("Web UI & Frontend", "React, HTML5, CSS3, Responsive Design, Component Libraries, Design Systems, Figma, "
      "Accessibility (WCAG), Data Visualization (Plotly, Power BI, Tableau)")
skill("Backend, APIs & Security", "FastAPI, Flask, RESTful Microservices, API Versioning, OAuth 2.0, JWT, "
      "Role-Based Access Control (RBAC), Authentication & Authorization")
skill("Job Scheduling & Orchestration", "Apache Airflow (DAGs), Celery, Job Queuing & Prioritization, Concurrent Execution, "
      "Kafka, Redis, Event-Driven Workflows")
skill("Containerization & DevOps", "Docker, Kubernetes, Jenkins, CI/CD, Git, DVC, MLflow")
skill("Distributed Processing & Performance", "Apache Spark, PySpark, Hadoop, Hive, ETL Pipelines, Profiling (cProfile), "
      "Performance Metrics, Throughput Optimization")
skill("Cloud & Databases", "AWS (S3, EC2, Lambda, Glue, RDS, SageMaker), Azure (Stream Analytics, Data Services), "
      "MongoDB, Snowflake, Delta Lake")
skill("ML & Analytics", "PyTorch, scikit-learn, HuggingFace Transformers, BERT/BioBERT, Optuna")

# ---------------- Education ----------------
heading("EDUCATION")
for line in ["**Master’s in Data Analytics and Engineering** | George Mason University, Fairfax, VA, USA.",
             "**Bachelor’s in Information Science and Engineering** | Visvesvaraya Technological University, Bengaluru, Karnataka, India."]:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.1)
    p.paragraph_format.space_after = Pt(3)
    runs(p, line)

# ---------------- Experience ----------------
heading("PROFESSIONAL EXPERIENCE")
job("George Mason University", "UI/UX Developer", "Fairfax, VA | August 2024 – Present")
for b in [
    "Modernized the UI architecture of a **multi-user research analytics dashboard** using **React** and **Python (FastAPI)**, "
    "redesigning **information hierarchy, navigation, and layout** across functional modules to improve usability and consistency.",
    "Built a reusable **component library and design system** (typography, spacing, interaction states) applying **responsive "
    "design** and **accessibility (WCAG)** practices, standardizing UI patterns across all dashboard views.",
    "Implemented **role-based access control (RBAC)** and token-based **authorization** on **FastAPI** endpoints, securing "
    "multi-user access to datasets, models, and results by role and project.",
    "Designed a **job queuing and scheduling** layer for long-running processing jobs over **30K+ documents**, supporting "
    "**concurrent execution, prioritization**, and real-time job-status tracking surfaced in the UI.",
    "Profiled and optimized end-to-end **run-processing pipelines** using **Python, PyTorch, MLflow, and Optuna**, cutting iteration "
    "cycles from **3 days to under 18 hours** and serving predictions to the UI with **sub-200ms latency**.",
    "Streamlined data-preparation workflows with **Pandas** and **Scikit-learn**, standardizing **15GB** of structured and "
    "unstructured data across 6 datasets and reducing preparation time by **30%**.",
    "Containerized services with **Docker** and automated releases through **CI/CD** pipelines, reducing release cycles from "
    "**2 weeks to 5 days** and enabling **A/B testing** of UI and model variants.",
    "Led **design and code reviews** using **Git** and **DVC**, and authored **technical documentation** and engineering best "
    "practices, reducing onboarding time for new contributors to **under 2 days**.",
]:
    bullet(b)

job("Carelon Global Solutions", "Python Developer (Client: Accenture)", "India | January 2019 – July 2023")
for b in [
    "Engineered **access control and authorization** for enterprise **RESTful microservices** using **OAuth 2.0**, role-based "
    "permissions, and **API versioning**, securing **HIPAA-compliant** healthcare data exchange for a U.S. healthcare client.",
    "Orchestrated end-to-end workflows with **Apache Airflow DAGs** for data ingestion, transformation, and model retraining; "
    "refactored **scheduling and dependency logic** to support **concurrent execution and prioritization**, reducing manual effort by **25%**.",
    "Profiled and optimized large-scale **distributed processing workloads** by migrating from **Hive to Apache Spark/PySpark**, "
    "tuning partitioning and job execution to significantly reduce processing time and increase throughput.",
    "Built scalable **ETL pipelines** using **PySpark** and **AWS (S3, Glue, SageMaker)** with **Delta Lake**, improving data "
    "reliability by **30%** across ingestion and processing stages.",
    "Containerized and deployed Python services using **Docker, Kubernetes, and Jenkins CI/CD**, improving system uptime by "
    "**20%** and enabling real-time EHR integration via **REST APIs**.",
    "Developed real-time monitoring pipelines and **interactive Power BI dashboards** on **Azure Stream Analytics**, surfacing "
    "**performance metrics and statistics** that reduced unplanned downtime by **20%**.",
    "Delivered Python NLP services using **BERT** and **BioBERT** for clinical entity extraction, achieving **80% accuracy** and "
    "reducing document processing time by **55%**.",
    "Designed **MongoDB** data models and **Python/Java** validation scripts (UDFs) for high-throughput, fault-tolerant "
    "pipelines, improving data quality and consistency.",
    "Collaborated with Data Engineering, Product, and **Accenture** client stakeholders in **technical design discussions and code "
    "reviews** to define use cases, KPIs, and delivery roadmaps, reducing project turnaround time by **15%**.",
]:
    bullet(b)

doc.core_properties.author = "Ritesh Somashekar"
doc.save(OUT)
print("saved", OUT)
