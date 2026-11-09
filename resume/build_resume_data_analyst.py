import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "/home/user/SHIELD/resume/Ritesh_Somashekar_Data_Analyst.docx"

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
    p.paragraph_format.keep_with_next = True
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
    p.paragraph_format.keep_with_next = True
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


LINKEDIN = "https://www.linkedin.com/in/ritesh-somashekar-0497aa182"


def hyperlink(p, url, text, size):
    """Clickable link whose visible text stays readable to ATS parsers."""
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


# ---------------- Header ----------------
centered("Ritesh Somashekar", 18)
centered("Data Analyst | SQL, Python & AI-Powered Analytics", 14)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Fairfax, VA | (571) 245-7770 | ").font.size = Pt(12)
hyperlink(p, "mailto:ritesh.chandra33@gmail.com", "ritesh.chandra33@gmail.com", 12)
p.add_run(" | ").font.size = Pt(12)
hyperlink(p, LINKEDIN, "LinkedIn", 12)

# ---------------- Summary ----------------
heading("PROFESSIONAL SUMMARY")
bullet("**Data Analyst** with experience collecting, cleaning, and transforming large, complex datasets into decision-ready insights "
       "across technology, healthcare, academic research, and industrial domains. Strong in **Python, SQL, R, Pandas, Spark,** "
       "and **statistical analysis**.")
bullet("Skilled in integrating disparate sources, establishing **data quality standards**, measuring KPIs, testing hypotheses, "
       "identifying trends and anomalies, and evaluating models through statistical metrics and **A/B testing**. Built reproducible "
       "**ETL and analytics workflows** on AWS and Azure.")
bullet("Delivers **reports, dashboards, and presentations** in **Tableau** and **Power BI**, translating findings into clear "
       "recommendations for stakeholders and senior management, and applies **machine learning, NLP, LLMs, and RAG** to analytical workflows.")

# ---------------- Skills ----------------
heading("TECHNICAL SKILLS")
skill("Data Analytics & Programming", "**SQL (PostgreSQL, Oracle)**, **Python**, **R**, Pandas, NumPy, Scikit-learn, Exploratory "
      "Data Analysis, Data Cleaning, Data Wrangling, Statistical Analysis, Trend Analysis")
skill("Data Integration & Quality", "ETL/ELT, Apache Spark, PySpark, Airflow, Kafka, Delta Lake, Data Modeling, **Data Quality "
      "Standards**, Data Validation, Data Warehousing, Snowflake")
skill("Visualization & Reporting", "**Power BI**, **Tableau**, Excel, Dashboard Development, Business Reporting, Executive "
      "Presentations, Data Storytelling")
skill("AI/ML & Generative AI", "Machine Learning, NLP, BERT, BioBERT, Llama 3, GPT-4, Hugging Face, **RAG**, Vector Embeddings, "
      "FAISS, LightGBM, XGBoost, PyTorch, TensorFlow")
skill("Experimentation & Platforms", "Hypothesis Testing, A/B Testing, KPI Analysis, Anomaly Detection, MLflow, Git, GitHub, DVC, "
      "AWS (S3, Glue, SageMaker, EMR), Azure (Synapse, Databricks), FastAPI, REST APIs, Docker")

# ---------------- Education ----------------
heading("EDUCATION")
for line in ["**Master's in Data Analytics and Engineering** | George Mason University, Fairfax, VA, USA",
             "**Bachelor's in Information Science and Engineering** | Visvesvaraya Technological University, Bengaluru, Karnataka, India"]:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.1)
    p.paragraph_format.space_after = Pt(3)
    runs(p, line)

# ---------------- Experience ----------------
heading("PROFESSIONAL EXPERIENCE")
job("George Mason University", "Graduate Research Assistant (Applied ML)", "Fairfax, VA | August 2024 - Present")
for b in [
    "Developed NLP information extraction pipelines using **Python**, BioBERT, and Hugging Face to process **30,000 academic** "
    "documents, improving entity recognition **F1-score by 18%** over spaCy baselines.",
    "Collected, cleaned, and standardized **15GB** of structured and unstructured data across six datasets using Pandas and "
    "Scikit-learn, defining validation checks that reduced preparation time by **30%**.",
    "Analyzed large-scale disaster datasets with **Python, R,** and **Tableau**, applying statistical and ensemble models to forecast "
    "community coping trends with an **RMSE of 0.89** and presenting findings to research stakeholders.",
    "Performed feature engineering, model comparisons, and **statistical evaluation** to identify trends and patterns and assess "
    "the reliability of machine learning outputs for research applications.",
    "Built reproducible **Python** and MLflow experimentation pipelines with Optuna, reducing model iteration cycles from three "
    "days to **under 18 hours**.",
    "Deployed analytical inference APIs using **FastAPI and Docker** with **sub-200ms response latency**, supporting a multi-user "
    "research dashboard.",
    "Collaborated with research teams using Git and DVC to document analysis methods, track experiments, and maintain consistent "
    "evaluation benchmarks and reproducible workflows.",
    "Designed large-scale analytical and feature engineering pipelines using **Python**, Apache Spark, and **AWS EMR**, processing "
    "behavioral and telemetry data to support model development, performance tracking, and insights.",
    "Developed anomaly detection workflows using LightGBM, statistical evaluation, and threshold-based alerts for transaction "
    "monitoring, reducing false-positive alerts by **25%**.",
    "Evaluated AI/ML performance through **A/B testing**, accuracy metrics, and operational monitoring, helping teams compare "
    "models and make evidence-based deployment decisions.",
    "Automated analytical and model evaluation workflows using **MLflow and FastAPI**, reducing model release cycles from two "
    "weeks to five days and improving experiment reproducibility.",
    "Applied SHAP explainability to investigate feature contributions and prediction patterns, supporting model governance, risk "
    "assessment, and transparent analysis.",
    "Optimized Llama 3 models using LoRA and quantization-aware training, reducing model size by **40%** while keeping accuracy "
    "within 3% of full-precision benchmarks.",
]:
    bullet(b)

job("Carelon Global Solutions", "Machine Learning Engineer", "India | September 2020 - July 2023")
for b in [
    "Integrated structured and unstructured healthcare data with **PySpark, AWS Glue, S3, and Delta Lake**, building ETL pipelines "
    "that improved data reliability by **30%** under HIPAA requirements.",
    "Identified and resolved provider data accuracy issues by automating daily **NPPES** ingestion with **Python** and **SQL**, "
    "improving data accuracy by **74%** and cutting processing overhead by **60%**.",
    "Delivered self-service **Tableau** and **Power BI** reports backed by SQL data models, reducing reporting latency by **40%** "
    "for business stakeholders.",
    "Converted unstructured clinical text into analyzable entities using BERT and BioBERT, achieving **80% extraction accuracy** "
    "and reducing document processing time by **55%**.",
    "Performed statistical model evaluation, cross-validation, and hyperparameter tuning using Scikit-learn, XGBoost, and "
    "TensorFlow, increasing accuracy by **8%** and reducing training time by **15%**.",
    "Automated data ingestion, preprocessing, feature engineering, and recurring workflows through **Apache Airflow DAGs**, "
    "reducing manual processing effort by **25%**.",
    "Implemented **data quality checks** and validation standards across healthcare data workflows, supporting downstream analysis "
    "and real-time EHR integration through REST APIs and containerized services.",
    "Partnered with data engineering, product, and client stakeholders to define analytical KPIs, evaluate solution performance, "
    "and prioritize delivery, reducing turnaround time by **15%**.",
]:
    bullet(b)

doc.core_properties.author = "Ritesh Somashekar"
doc.core_properties.title = "Ritesh Somashekar - Data Analyst Resume"
doc.core_properties.keywords = "Data Analyst, SQL, Python, R, Tableau, Power BI, Data Quality, Statistical Analysis"
doc.save(OUT)
print("saved", OUT)
