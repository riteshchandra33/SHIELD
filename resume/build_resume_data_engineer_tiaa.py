import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "/home/user/SHIELD/resume/Ritesh_Somashekar_Data_Engineer_TIAA.docx"

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
        r = p.add_run(part.strip("*") if (bold or (ital and part.startswith("*"))) else part)
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
p.add_run(" | ").font.size = Pt(12)
hyperlink(p, "https://github.com/riteshchandra33", "GitHub", 12)

# ---------------- Summary ----------------
heading("PROFESSIONAL SUMMARY")
bullet("**Data Engineer** with **5+ years** building **ETL/ELT pipelines** and cloud data platforms on **AWS** and **Snowflake** for "
       "healthcare and university research; pursuing **AWS Certified Data Engineer - Associate**.")
bullet("Hands-on with **AWS Glue, S3, Lambda, EventBridge, CloudWatch, Athena, SQS,** and **SNS** plus **Apache Airflow**, "
       "delivering **99.9% pipeline reliability** with logging, lineage tracking, and automated data quality checks.")
bullet("Skilled in **Python, SQL, PySpark, Snowflake, Databricks,** and **Delta Lake**, with **HIPAA-compliant** data handling and "
       "published research at **ACM WSDM '26** and **IEEE PST 2026**.")

# ---------------- Skills ----------------
heading("TECHNICAL SKILLS")
skill("AWS Data & Serverless", "**AWS Glue**, **Amazon S3**, **AWS Lambda**, **Amazon EventBridge** (Scheduler, Rules), Amazon "
      "Athena, Amazon SQS, Amazon SNS, Amazon RDS, API Gateway")
skill("Logging & Monitoring", "**Amazon CloudWatch** (Logs), S3 Log Archival, Pipeline Monitoring & Alerting, Data Lineage, "
      "Audit Logging")
skill("Data Warehousing & Lakes", "**Snowflake**, Databricks, Delta Lake, Data Modeling, Data Warehousing, Data Quality, "
      "Data Validation")
skill("Pipelines & Orchestration", "ETL/ELT, **Apache Airflow**, Apache Spark, **PySpark**, Kafka, Hadoop, Hive, Informatica "
      "PowerCenter, Precisely Data360")
skill("Programming & Databases", "**Python**, **SQL**, R, Scala, Bash, SQL Server, MySQL, PostgreSQL, MongoDB, ChromaDB")
skill("DevOps & Tools", "Git, GitHub, CI/CD, Docker, Kubernetes, DVC, FastAPI, REST APIs, Jira, Postman, Tableau, Power BI")

# ---------------- Education ----------------
heading("EDUCATION")
for line in ["**Master's in Data Analytics and Engineering** | George Mason University, Fairfax, VA, USA",
             "**Bachelor's in Information Science and Engineering** | Visvesvaraya Technological University, Bengaluru, Karnataka, India"]:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.1)
    p.paragraph_format.space_after = Pt(3)
    runs(p, line)

# ---------------- Certifications ----------------
heading("CERTIFICATIONS")
for line in ["**AWS Certified Data Engineer - Associate (DEA-C01)** | In Progress",
             "Study areas: AWS Glue, S3, Lambda, EC2, EventBridge, CloudWatch, CloudTrail, VPC Flow Logs, Redshift, Kinesis"]:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.1)
    p.paragraph_format.space_after = Pt(3)
    runs(p, line)

# ---------------- Experience ----------------
# Each bullet follows STAR: situation/task -> action (with tools) -> measurable result.
heading("PROFESSIONAL EXPERIENCE")
job("George Mason University", "Graduate Research Assistant", "Fairfax, VA | August 2024 - Present")
for b in [
    "To automate service-ticket triage for a cybersecurity partner, built a **serverless AWS pipeline** of **Lambda** functions "
    "triggered by **EventBridge Scheduler** rules and **S3 events**, reaching **93% automation accuracy** and **70%** faster triage.",
    "To make every pipeline run traceable, streamed Lambda logs to **Amazon CloudWatch**, archived run logs in **S3**, and sent "
    "SLA breach alerts through **SNS**, cutting operational risk by **40%** with audit-ready records.",
    "To scale ticket processing, designed an **event-driven backend** chaining Lambda stages through **S3 event triggers** and "
    "**SQS** messaging, with **Jira REST API** ingestion into S3-staged JSON and CSV data, improving scalability by **50%**.",
    "To give 9-1-1 training AI trustworthy data, led the **data pipeline** for **SHIELD** and **MATE-911** in **Python**, turning "
    "unstructured call records into **160** validated scenarios and cutting hallucinations from **13.0% to 3.0%**.",
    "To stop bad records reaching production, built **data quality gates** (completeness, schema, ontology, and 85% similarity "
    "checks) before loading into **ChromaDB**, lowering hallucinations from **9.5% to 3.0%**.",
    "To prepare research data at scale, built pipelines with **Python, SQL, Pandas, AWS S3,** and **DVC** for **30,000 documents** "
    "(cleaning, deduplication, metadata tagging), improving entity-recognition F1 by **18%**.",
    "To cut data preparation time, standardized **15GB** of structured and unstructured data across six datasets with repeatable "
    "transformation and validation, reducing preparation time by **30%**.",
    "To serve processed data to researchers, deployed **FastAPI** and **Docker** data APIs at **sub-200ms** latency, versioning "
    "datasets with **Git** and **DVC** for reproducible workflows.",
]:
    bullet(b)

job("Carelon Global Solutions (Elevance Health)", "Data Engineer", "Bengaluru, India | October 2020 - August 2023")
for b in [
    "To support downstream AI and BI applications, designed and managed **20+ enterprise ETL pipelines** on **AWS**, boosting "
    "data throughput by **70%** with high availability.",
    "To remove manual pipeline runs, automated workflows with **Apache Airflow, Python,** and **AWS (S3, Lambda, Athena)**, "
    "achieving **99.9% pipeline reliability** with end-to-end lineage tracking.",
    "To unify healthcare data under **HIPAA**, built **AWS Glue** and **PySpark** ETL pipelines into **S3** and **Delta Lake**, "
    "improving data reliability by **30%**.",
    "To speed up model training, ingested **400K+ XML/JSON healthcare records** into **Snowflake** and **Databricks**, "
    "accelerating training by **60%** and cutting preprocessing time by **70%**.",
    "To fix inaccurate provider data, built a daily **NPPES** ingestion workflow in **Python** and **SQL**, improving data accuracy "
    "by **74%** and cutting processing overhead by **60%**.",
    "To process growing data volumes, engineered **PySpark** and **Databricks** pipelines handling **500GB+** of structured and "
    "unstructured data, reducing processing time by **45%**.",
    "To modernize legacy workloads, migrated **Hive** and **Hadoop** jobs to **Apache Spark**, improving processing speed and "
    "scalability across enterprise data workflows.",
    "To give business teams faster reporting, delivered self-service **Tableau** and **Power BI** pipelines on SQL data models, "
    "cutting reporting latency by **40%**.",
    "To reduce manual claims work, redesigned **claims-balancing ETL workflows** and automated medical invoice pipelines, "
    "cutting operational overhead by **60%** and manual errors by **70%**.",
]:
    bullet(b)

# ---------------- Publications ----------------
heading("PUBLICATIONS")
for pub in [
    "R. S. Nayaka, **R. Somashekar**, et al. \"SHIELD: A Framework for Online Conversational AI System for Self-Regulated "
    "Learning at Emergency Communications Centers.\" *ACM WSDM '26*. doi:10.1145/3773966.3779411",
    "R. S. Nayaka, **R. Somashekar**, H. Purohit. \"MATE-911: Multimodal AI-powered Training Environment for Next-Generation "
    "911 Dispatcher Preparedness.\" *IEEE PST 2026*.",
]:
    bullet(pub)

doc.core_properties.author = "Ritesh Somashekar"
doc.core_properties.title = "Ritesh Somashekar - Data Engineer Resume"
doc.core_properties.keywords = "Data Engineer, AWS Glue, S3, Lambda, EventBridge, CloudWatch, Snowflake, Airflow, PySpark, ETL"
doc.save(OUT)
print("saved", OUT)
