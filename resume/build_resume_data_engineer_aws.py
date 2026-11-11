import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "/home/user/SHIELD/resume/Ritesh_Somashekar_Data_Engineer_AWS.docx"

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
centered("Data Engineer | AWS, Snowflake & Python", 14)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("Fairfax, VA | (571) 245-7770 | ").font.size = Pt(12)
hyperlink(p, "mailto:ritesh.chandra33@gmail.com", "ritesh.chandra33@gmail.com", 12)
p.add_run(" | ").font.size = Pt(12)
hyperlink(p, LINKEDIN, "LinkedIn", 12)

# ---------------- Summary ----------------
heading("PROFESSIONAL SUMMARY")
bullet("**Data Engineer** with **8+ years of experience** building scalable **ETL/ELT pipelines** and cloud data platforms on "
       "**AWS** and **Snowflake** across technology, healthcare, research, and industrial environments.")
bullet("Hands-on with **AWS Glue, S3, Lambda, Athena, EMR,** and **EC2**, plus **Apache Airflow, Spark/PySpark,** and **Kafka**, "
       "delivering **99.9% pipeline reliability** with end-to-end lineage tracking, monitoring, and automated data quality checks.")
bullet("Experienced in **data modeling** and **warehousing** (**Snowflake, Databricks, Delta Lake**), **HIPAA-compliant** data "
       "handling, and partnering with analytics, ML, and business teams to deliver trusted, analysis-ready data.")

# ---------------- Skills ----------------
heading("TECHNICAL SKILLS")
skill("AWS Data Services", "**AWS Glue**, **S3**, **Lambda**, **Athena**, **EMR**, **EC2**, IAM, SageMaker")
skill("Data Warehousing & Lakes", "**Snowflake**, Databricks, Delta Lake, Azure Data Lake, Star Schema, Dimensional Modeling, "
      "Data Warehousing")
skill("Pipelines & Orchestration", "ETL/ELT, **Apache Airflow**, Apache Spark, **PySpark**, Kafka, Flink, dbt, Azure Data Factory, "
      "Hadoop, Hive, Sqoop, Informatica PowerCenter")
skill("Programming & Databases", "**Python**, **SQL**, Scala, Java, Bash, PostgreSQL, Oracle, SQL Server, MySQL, MongoDB")
skill("Data Quality & Operations", "Data Validation, Data Lineage, Pipeline Monitoring & Alerting, Git, GitHub, CI/CD, Docker, "
      "Kubernetes, Linux")
skill("Analytics & ML", "Power BI, Tableau, Pandas, Scikit-learn, MLflow, FastAPI, REST APIs")

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
job("Apple", "AI & ML Engineer", "Cupertino, CA | May 2025 - Present")
for b in [
    "Designed large-scale data and feature engineering pipelines using **Python, Apache Spark,** and **AWS EMR**, processing "
    "behavioral and telemetry data for model development, performance tracking, and analytics.",
    "Engineered **real-time streaming pipelines** with **Apache Kafka, Flink,** and **Spark** to ingest and preprocess interaction "
    "data for downstream models, improving pipeline throughput by **26%**.",
    "Developed anomaly detection workflows using LightGBM, statistical evaluation, and threshold-based alerts, reducing "
    "false-positive alerts by **25%**.",
    "Automated data and model release workflows with **MLflow, FastAPI, Docker,** and **GitHub Actions**, reducing release cycles "
    "from two weeks to five days and improving reproducibility.",
]:
    bullet(b)

job("George Mason University", "Graduate Research Assistant (Applied ML)", "Fairfax, VA | August 2024 - Present")
for b in [
    "Built end-to-end data pipelines using **Python, SQL, Pandas, AWS S3,** and **DVC** to process **30,000 academic documents**, "
    "covering cleaning, deduplication, and metadata tagging; improved entity-recognition F1-score by **18%** over spaCy.",
    "Standardized **15GB** of structured and unstructured data across six datasets using Pandas, reducing preparation time by "
    "**30%** through repeatable transformation and validation.",
    "Led the data pipeline for the **SHIELD** and **MATE-911** AI platforms (published at **ACM WSDM '26** and **IEEE PST 2026**), "
    "turning unstructured 9-1-1 call records into **160** validated, embedding-ready scenarios.",
    "Built reproducible **Python** and MLflow pipelines with Optuna, reducing iteration cycles from three days to **under 18 hours**, "
    "and deployed data APIs with **FastAPI and Docker** at **sub-200ms** latency.",
    "Collaborated with research teams using **Git** and **DVC** to document data and analysis methods, track experiments, and "
    "maintain reproducible workflows.",
]:
    bullet(b)

job("Accenture", "Machine Learning Engineer", "India | September 2020 - July 2023")
for b in [
    "Designed and managed **20+ enterprise ETL pipelines** on **AWS**, boosting data throughput by **70%** and ensuring high "
    "availability for downstream AI and BI applications.",
    "Automated workflows using **Apache Airflow, Python,** and **AWS (S3, Lambda, Athena)**, achieving **99.9% pipeline "
    "reliability** with end-to-end lineage tracking.",
    "Integrated structured and unstructured healthcare data with **PySpark, AWS Glue, S3,** and **Delta Lake**, building ETL "
    "pipelines that improved data reliability by **30%** under **HIPAA** requirements.",
    "Engineered ingestion pipelines for **400K+ XML/JSON healthcare records** into **Snowflake** and **Databricks**, accelerating "
    "model training by **60%** and reducing preprocessing time by **70%**.",
    "Built a daily ingestion workflow from **NPPES** repositories, improving data accuracy by **74%** and cutting processing "
    "overhead by **60%**.",
    "Engineered **PySpark** and **Databricks** pipelines processing **500GB+** of structured and unstructured data, reducing "
    "processing time by **45%** for downstream ML applications.",
    "Delivered self-service BI pipelines integrating **Tableau, Power BI,** and SQL-based models, reducing reporting latency by "
    "**40%**.",
    "Partnered with data engineering, product, and client stakeholders to define KPIs, evaluate solution performance, and "
    "prioritize delivery, reducing turnaround time by **15%**.",
]:
    bullet(b)

job("Honeywell", "Data Engineer", "India | January 2018 - September 2020")
for b in [
    "Engineered **ETL/ELT pipelines** for industrial IoT analytics with **Python, PySpark,** and **Apache Spark**, ingesting "
    "telemetry from **8+ source systems** via REST APIs and processing **2M+ records daily** into **Azure Data Lake**.",
    "Automated batch workflows with **Azure Data Factory** and **Apache Airflow**, adding source-to-target validation and "
    "monitoring across **15+ daily jobs** and cutting issue detection time to **under 15 minutes**.",
    "Implemented **data quality frameworks** (null checks, duplicate detection, schema validation, referential integrity), "
    "reducing downstream reporting errors by **40%** across **3 plant sites**.",
    "Designed a **star-schema** data warehouse for asset uptime and operational KPIs, cutting report turnaround time by **60%** "
    "across **5 operational teams**.",
    "Migrated large-scale workloads from **Hive** to **Apache Spark/PySpark**, and moved **Hadoop/Sqoop** ingestion to **Azure "
    "Data Services**, improving performance and scalability.",
    "Archived raw telemetry in **AWS S3**, designed **MongoDB** models for high-volume sensor data, and managed deployments "
    "with **Git, CI/CD,** and Linux shell scripting.",
]:
    bullet(b)

doc.core_properties.author = "Ritesh Somashekar"
doc.core_properties.title = "Ritesh Somashekar - Data Engineer Resume"
doc.core_properties.keywords = "Data Engineer, AWS Glue, S3, Lambda, EC2, Snowflake, Airflow, PySpark, ETL"
doc.save(OUT)
print("saved", OUT)
