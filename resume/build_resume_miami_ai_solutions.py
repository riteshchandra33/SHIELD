import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "/home/user/SHIELD/resume/Ritesh_Somashekar_AI_Solutions_Engineer_Miami.docx"

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


# ---------------- Header ----------------
centered("Ritesh Somashekar", 18)
centered("AI Solutions Engineer | Generative AI Services & Adoption", 14)
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
bullet("**AI Solutions Engineer** with **5+ years** taking **generative AI** from idea to pilot to supported service in **higher "
       "education** and **healthcare**; published at **ACM WSDM '26** and **IEEE PST 2026**.")
bullet("Hands-on with **enterprise LLM platforms and APIs (Azure OpenAI, GPT-4, Claude, Gemini)**, **RAG, agents, embeddings, vector "
       "search,** and **workflow automation**, built with **security, privacy (HIPAA),** and **access controls (OAuth 2.0)**.")
bullet("Partners with researchers, public agencies, and business stakeholders, using **evaluation frameworks**, **documentation**, "
       "and **demos** to explain AI capabilities, limitations, and risks to technical and non-technical audiences.")

# ---------------- Skills ----------------
heading("TECHNICAL SKILLS")
skill("Generative AI Platforms & APIs", "Azure OpenAI, GPT-4, Claude, Gemini, Llama 3 (Ollama), LLM APIs, Prompt Engineering, "
      "Structured Outputs")
skill("AI Solution Patterns", "RAG, Agentic AI, Embeddings, Vector Search (ChromaDB, Pinecone, pgvector, FAISS), LangChain, "
      "LlamaIndex, Workflow Automation (Apache Airflow)")
skill("AI Evaluation & Governance", "Evaluation Frameworks, RAGAS, Hallucination Detection, Guardrails, Model Monitoring, Drift "
      "Detection, A/B Testing")
skill("Security & Integration", "OAuth 2.0, REST APIs, API Versioning, HIPAA Compliance, FastAPI, Docker, Kubernetes, CI/CD")
skill("Programming & Cloud", "Python, SQL, Java, AWS (S3, Lambda, SageMaker, SQS), Azure, Snowflake, Databricks")
skill("Consulting & Delivery", "Stakeholder Consultation, Requirements Analysis, Pilot-to-Production Delivery, Technical "
      "Documentation, Demonstrations")

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
    "To bring AI into 9-1-1 training, worked with **Fairfax County DPSC** instructors to scope needs, then co-developed **SHIELD**, "
    "an **LLM-agent** training platform; published and demonstrated at **ACM WSDM '26**.",
    "To move SHIELD from prototype to pilot, supported agency testing sessions and built a **Python/Streamlit** app with **SQLite** "
    "accounts and course enrollment, refining it from instructor feedback.",
    "To deliver safe AI without commercial API costs or data-sharing risk, co-developed **MATE-911**, a locally hosted **RAG** "
    "service on **Llama 3.1 8B** with **0.81 protocol F1**; published at **IEEE PST 2026**.",
    "To make AI output trustworthy in a high-stakes domain, led the **guardrails and validation layer** aligned to **NENA** "
    "protocols, lowering hallucinations from **9.5% to 3.0%**.",
    "To give partners a clear basis for decisions, built an **evaluation framework** with ablation studies, showing **semantic "
    "search** retrieval lifted the pass rate from **49.7% to 97.6%**.",
    "To ground answers in approved content, led the **RAG knowledge base and data pipeline** for **160 gold-standard scenarios**, "
    "cutting hallucinations from **13.0% to 3.0%**.",
    "To support faculty and student research, delivered a **RAG research assistant** (**LlamaIndex, pgvector, FastAPI**) used by "
    "**40+ researchers**, raising **recall@10 from 61% to 88%**.",
    "To compare LLM vendors on equal terms, evaluated **GPT-4, Claude,** and **Gemini** through **LangChain**, selecting "
    "configurations that raised accuracy by **16%** and cut hallucinations by **19%**.",
    "To make AI work repeatable, wrote **documentation and reproducibility standards** adopted by **two follow-on LLM studies**, "
    "cutting onboarding time for new researchers to **under 2 days**.",
    "To turn pilots into supportable services, set up **MLflow**, **Docker**, and **CI/CD**, cutting release cycles from **2 weeks "
    "to 5 days** with **A/B testing**.",
]:
    bullet(b)

job("Carelon Global Solutions (Elevance Health)", "Machine Learning Engineer", "Bengaluru, India | May 2022 - August 2023")
for b in [
    "To reduce member support load, delivered an enterprise **Azure OpenAI** assistant with **LangChain** and **Pinecone** RAG for "
    "**15K+ daily queries**, cutting resolution time by **38%** and raising ticket deflection by **25%**.",
    "To keep AI services reliable after launch, set up **monitoring**, **drift detection**, and automated retraining, sustaining "
    "**over 95% accuracy** for **12 months** across **200+ end users**.",
    "To integrate AI with clinical systems, containerized model services with **Docker, Kubernetes,** and **Jenkins CI/CD** behind "
    "**REST APIs**, improving uptime by **20%** and enabling real-time EHR integration.",
    "To automate clinical text review, built **BERT/BioBERT** extraction models on unstructured medical notes, reaching **80% "
    "accuracy** and cutting processing time by **55%**.",
    "To automate data workflows under **HIPAA**, designed **20+ pipelines** with **Apache Airflow** and **AWS**, raising "
    "throughput by **70%** and reaching **99.9% reliability**.",
]:
    bullet(b)

job("Carelon Global Solutions (Elevance Health)", "Data Engineer", "Bengaluru, India | October 2020 - April 2022")
for b in [
    "To control access to sensitive health data, built **RESTful services** with **OAuth 2.0** authentication and **API "
    "versioning**, giving internal teams secure, consistent integrations.",
    "To align data work with business goals, partnered with stakeholders on the **Seven Plus Locations** project to map pipelines "
    "to KPIs, improving claims data accuracy.",
    "To reduce manual claims reconciliation, redesigned **claims-balancing workflows** in **Python** and **SQL**, cutting "
    "operational overhead by **60%**.",
    "To eliminate costly invoice errors, automated **medical invoice processing** with rule-based classification, reducing "
    "manual errors by **70%**.",
]:
    bullet(b)

# ---------------- Projects ----------------
heading("PROJECTS")
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(2)
p.paragraph_format.keep_with_next = True
runs(p, "**Agentic AI Ticket Automation System** | SecureGPT, LLaMA, AWS SQS, JIRA, NIST-CSF")
bullet("To cut security-ticket triage time, built an **agentic AI** workflow with **SecureGPT** and **LLaMA** that auto-creates "
       "**JIRA** tickets under **NIST-CSF**, reaching **93% automation accuracy** and **70%** faster triage.")

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
doc.core_properties.title = "Ritesh Somashekar - AI Solutions Engineer Resume"
doc.core_properties.keywords = "AI Solutions Engineer, Generative AI, LLM, RAG, Azure OpenAI, AI Governance, Higher Education"
doc.save(OUT)
print("saved", OUT)
