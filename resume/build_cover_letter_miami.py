"""Builds the cover letter for the Miami University Senior AI Solutions Engineer role."""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "/home/user/SHIELD/resume/Ritesh_Somashekar_Cover_Letter_Miami.docx"
LINKEDIN = "https://www.linkedin.com/in/ritesh-somashekar-0497aa182/"

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.left_margin = sec.right_margin = Inches(0.9)
sec.top_margin = sec.bottom_margin = Inches(0.7)

st = doc.styles["Normal"]
st.font.name = "Calibri"
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.font.size = Pt(11)
st.paragraph_format.space_before = Pt(0)
st.paragraph_format.space_after = Pt(8)
st.paragraph_format.line_spacing = 1.08


def hyperlink(p, url, text):
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


def centered(text, size, after=0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(text)
    r.bold, r.font.size = True, Pt(size)


def rule(p):
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, v in (("val", "single"), ("sz", "6"), ("space", "4"), ("color", "808080")):
        b.set(qn("w:" + k), v)
    bdr.append(b)
    pPr.insert(0, bdr)


def para(text, after=8, justify=True):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(after)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if justify else WD_ALIGN_PARAGRAPH.LEFT
    return p


# Header (matches the resume)
centered("Ritesh Somashekar", 18)
centered("AI Solutions Engineer | Generative AI Services & Adoption", 13)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_after = Pt(14)
p.add_run("Fairfax, VA | (571) 245-7770 | ")
hyperlink(p, "mailto:ritesh.chandra33@gmail.com", "ritesh.chandra33@gmail.com")
p.add_run(" | ")
hyperlink(p, LINKEDIN, "LinkedIn")
rule(p)

para("October 30, 2026", after=10, justify=False)
para("Search Committee\nInformation Technology Services, Miami University\nRe: Senior AI Solutions Engineer", after=10, justify=False)
para("Dear Search Committee,", justify=False)

para("I am applying for the Senior AI Solutions Engineer position at Miami University. For the past two years at George Mason "
     "University, my work has followed the path this role describes: sitting down with a partner who has a real problem, judging "
     "whether AI can help responsibly, and carrying the answer from a prototype to something people rely on.")

para("Our partner was Fairfax County's 9-1-1 center. Instructors could not run enough role-play calls to train new call-takers, so "
     "we co-developed SHIELD, a platform where LLM agents simulate emergency calls and coach trainees (ACM WSDM '26). I supported "
     "testing sessions with the agency, built the application, and refined it from instructor feedback. For MATE-911 (IEEE PST "
     "2026), we ran Llama 3.1 locally instead of sending sensitive data to a commercial API, and I led the guardrails and "
     "evaluation work that brought hallucinations down to 3.0%. That project showed me how much adoption depends on trust: "
     "being able to show a non-technical partner what the system does well, where it fails, and which controls are in place.")

para("I have also worked on the enterprise side. At Carelon Global Solutions, I delivered an Azure OpenAI and LangChain "
     "assistant handling more than 15,000 daily member queries in a HIPAA-regulated environment, built OAuth 2.0-secured "
     "services, and set up monitoring that kept production models above 95% accuracy for a year. At GMU, I evaluated GPT-4, "
     "Claude, and Gemini side by side and wrote documentation and reproducibility standards that two follow-on studies adopted.")

para("What draws me to Miami is the chance to do this at institutional scale: shared AI services, evaluation frameworks, and "
     "guardrails that every unit can use, and a community of practice that grows around them. I have not yet owned enterprise "
     "platform administration or charge-back models, and I am eager to build that experience with Miami's ITS team.")

para("Thank you for your consideration. I would welcome the chance to discuss how I can help Miami adopt AI practically and "
     "responsibly.")

para("Sincerely,", after=2, justify=False)
para("Ritesh Somashekar", after=0, justify=False)

doc.core_properties.author = "Ritesh Somashekar"
doc.core_properties.title = "Ritesh Somashekar - Cover Letter - Senior AI Solutions Engineer"
doc.save(OUT)
print("saved", OUT)
