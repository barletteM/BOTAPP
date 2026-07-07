import html
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen


FALLBACK = (
    "I do not have an exact confirmed record for that in this demo. "
    "Based on the demo website notes, I can still guide you generally."
)
BOTS = [
    {
        "id": "1",
        "slug": "limkokwing-university",
        "name": "Limkokwing University Bot",
        "description": "Reception assistant for Limkokwing University inquiries.",
        "office_hours": "",
        "location": "",
        "phone": "",
        "email": "",
        "website": "",
        "reception_instructions": "Answer from approved Limkokwing University knowledge only.",
    },
    {
        "id": "2",
        "slug": "irca-glowdom-africa",
        "name": "IRCA-GLOWDOM AFRICA Bot",
        "description": "Reception assistant for IRCA-GLOWDOM AFRICA inquiries.",
        "office_hours": "",
        "location": "",
        "phone": "",
        "email": "",
        "website": "",
        "reception_instructions": "Answer from approved IRCA-GLOWDOM AFRICA knowledge only.",
    },
    {
        "id": "3",
        "slug": "windhoek-municipality",
        "name": "Windhoek Municipality Bot",
        "description": "Reception assistant for Windhoek Municipality public inquiries.",
        "office_hours": "",
        "location": "",
        "phone": "",
        "email": "",
        "website": "",
        "reception_instructions": "Answer from approved Windhoek Municipality knowledge only.",
    },
]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_ROOT = PROJECT_ROOT / "frontend"

SOURCE_LINKS = {
    "limkokwing-university": [
        {"label": "Limkokwing official site", "url": "https://www.limkokwing.net/"},
        {"label": "Limkokwing University profile", "url": "https://en.wikipedia.org/wiki/Limkokwing_University_of_Creative_Technology"},
        {"label": "Lim Kok Wing profile", "url": "https://en.wikipedia.org/wiki/Lim_Kok_Wing"},
    ],
    "irca-glowdom-africa": [
        {"label": "Public search: IRCA-GLOWDOM AFRICA", "url": "https://www.google.com/search?q=IRCA-GLOWDOM+AFRICA"},
        {"label": "Public search: GLOWDOM AFRICA Sebulon", "url": "https://www.google.com/search?q=GLOWDOM+AFRICA+Sebulon"},
        {"label": "LinkedIn public search", "url": "https://www.google.com/search?q=IRCA-GLOWDOM+AFRICA+LinkedIn"},
    ],
    "windhoek-municipality": [
        {"label": "City of Windhoek official site", "url": "https://www.windhoekcc.org.na/"},
        {"label": "City of Windhoek services", "url": "https://www.windhoekcc.org.na/"},
        {"label": "Windhoek public profile", "url": "https://en.wikipedia.org/wiki/Windhoek"},
    ],
}

DEMO_KNOWLEDGE = {
    "limkokwing-university": [
        {
            "title": "Leadership and principal",
            "keywords": ["principal", "leader", "head", "director", "dean", "president", "vice", "chancellor", "management"],
            "answer": "For leadership questions, the safest demo answer is that Limkokwing University inquiries should be directed to the campus administration, admissions office, or faculty office for the current principal, dean, or head of department. Staff titles can change, so the receptionist should verify the current name before confirming it.",
        },
        {
            "title": "Office hours",
            "keywords": ["hour", "hours", "open", "opening", "close", "closing", "working", "time", "times"],
            "answer": "Demo guidance: university reception offices usually assist visitors Monday to Friday during normal business hours. For planning, try visiting between 08:00 and 16:30 on a weekday.",
        },
        {
            "title": "Admissions and applications",
            "keywords": ["admission", "apply", "application", "enrol", "intake", "register"],
            "answer": "For admissions, prepare your ID or passport, latest academic results, proof of qualification, contact details, and any programme-specific documents. The admissions desk can guide you on available intakes and application status.",
        },
        {
            "title": "Programmes and courses",
            "keywords": ["course", "program", "programme", "study", "faculty", "degree", "diploma"],
            "answer": "Limkokwing is known for creative technology fields such as design, multimedia, communication, business, computing, architecture, and related creative industries. Ask for the programme name and the bot can guide you on likely requirements.",
        },
        {
            "title": "Fees and payments",
            "keywords": ["fee", "payment", "pay", "tuition", "cost", "bank"],
            "answer": "For fees, ask the finance or admissions office for the current fee schedule. Usually students need a quotation or invoice, student reference number, and proof of payment after paying.",
        },
        {
            "title": "Documents",
            "keywords": ["document", "requirement", "certificate", "transcript", "result"],
            "answer": "Common documents include certified ID/passport copy, academic certificates or latest results, proof of address or contact details, passport photo, and proof of payment where required.",
        },
        {
            "title": "Location and directions",
            "keywords": ["location", "direction", "address", "where", "map"],
            "answer": "For directions, search for the official Limkokwing campus location or ask reception for the campus address before travelling. Bring your ID and the name of the department you need.",
        },
    ],
    "irca-glowdom-africa": [
        {
            "title": "Leadership and responsible person",
            "keywords": ["principal", "leader", "head", "director", "manager", "responsible", "owner", "management"],
            "answer": "For leadership or responsible-person questions, reception should confirm the current manager, director, or assigned coordinator before giving a name. In this demo, the best guidance is to ask for the IRCA-GLOWDOM AFRICA office administrator or service coordinator.",
        },
        {
            "title": "Office hours",
            "keywords": ["hour", "hours", "open", "opening", "close", "closing", "working", "time", "times"],
            "answer": "Demo guidance: IRCA-GLOWDOM AFRICA reception would normally assist clients on weekdays during business hours. A safe visit window is 08:00 to 16:30 unless an appointment says otherwise.",
        },
        {
            "title": "Services",
            "keywords": ["service", "training", "audit", "certification", "iso", "consulting"],
            "answer": "IRCA-GLOWDOM AFRICA can be presented in this demo as a professional training, auditing, certification-support, and compliance guidance desk. Ask which service you need and I can suggest the next step.",
        },
        {
            "title": "Appointments",
            "keywords": ["appointment", "booking", "book", "meeting", "schedule"],
            "answer": "For appointments, share your name, organisation, phone/email, preferred date, and service needed. Reception can then confirm availability or refer you to the right consultant.",
        },
        {
            "title": "Documents",
            "keywords": ["document", "requirement", "form", "certificate", "company"],
            "answer": "Common documents may include company registration details, contact person details, previous audit or training records, certificates, and the scope of service requested.",
        },
        {
            "title": "Fees and payments",
            "keywords": ["fee", "payment", "invoice", "quote", "quotation", "cost"],
            "answer": "For payment guidance, request a quotation first. Once accepted, use the invoice reference when paying and send proof of payment to the office or assigned coordinator.",
        },
    ],
    "windhoek-municipality": [
        {
            "title": "Leadership and officials",
            "keywords": ["principal", "leader", "head", "mayor", "ceo", "chief", "council", "councillor", "management"],
            "answer": "For leadership questions, the municipality should verify the current mayor, councillor, chief executive, or department head before confirming a name. In this demo, I can guide you to ask customer care for the relevant municipal department or official.",
        },
        {
            "title": "Office hours",
            "keywords": ["hour", "hours", "open", "opening", "close", "closing", "working", "time", "times"],
            "answer": "Demo guidance: municipal offices usually assist the public Monday to Friday during government business hours. Try visiting between 08:00 and 16:00 for counter services.",
        },
        {
            "title": "Municipal services",
            "keywords": ["service", "water", "electricity", "rates", "tax", "account", "waste", "permit"],
            "answer": "The municipality can assist with public services such as municipal accounts, rates and taxes, water and electricity queries, waste services, permits, and general city service requests.",
        },
        {
            "title": "Location and public inquiries",
            "keywords": ["location", "direction", "address", "where", "public", "query"],
            "answer": "For public inquiries, go to the relevant municipal customer care or service counter with your ID and account or erf details if your question is about a property or service account.",
        },
        {
            "title": "Documents",
            "keywords": ["document", "requirement", "id", "proof", "application", "form"],
            "answer": "Common municipal documents include ID, proof of address, municipal account number, erf or property details, completed application forms, and proof of payment where applicable.",
        },
        {
            "title": "Payments",
            "keywords": ["fee", "payment", "pay", "account", "bill", "arrears"],
            "answer": "For municipal payments, keep your municipal account number or reference ready. After payment, save proof of payment in case the account needs manual follow-up.",
        },
    ],
}

DIRECT_ANSWERS = {
    "limkokwing-university": [
        {
            "triggers": ["summary", "all data", "tell me about", "profile", "about limkokwing", "background"],
            "answer": "Limkokwing University of Creative Technology is a private creative-technology university founded by Tan Sri Lim Kok Wing. Public information associates it with design, multimedia, communication, business, computing, technology, architecture, and creative-industry programmes, with international campuses across Africa, Europe, and Asia. For reception: route applications to Admissions, fees to Finance, documents/registration to Registry or Admissions, and programme advice to the relevant faculty desk.",
        },
        {
            "triggers": ["who is the founder", "founder", "lim kok wing"],
            "answer": "The founder of Limkokwing University of Creative Technology was Tan Sri Lim Kok Wing.",
        },
        {
            "triggers": ["who is the principal", "principal", "campus head", "head of campus", "director"],
            "answer": "For this demo, use Campus Administration as the named responsible desk for principal/campus-head questions. The globally known founder is Tan Sri Lim Kok Wing; the current local principal or campus director should be confirmed by the campus office before official use.",
        },
        {
            "triggers": ["contact", "phone", "email", "admissions office", "who do i contact"],
            "answer": "For Limkokwing inquiries, contact Admissions for applications and programme advice, Finance for fees and payments, Registry/Campus Administration for registration and documents, and the Faculty Office for course-specific questions.",
        },
        {
            "triggers": ["courses", "programmes", "programs", "what can i study", "faculties"],
            "answer": "Limkokwing is commonly associated with design, multimedia, communication, business, computing, technology, architecture, and creative-industry programmes. For exact current courses, ask Admissions for the latest programme list.",
        },
        {
            "triggers": ["requirements", "documents", "what documents", "registration requirements", "application requirements"],
            "answer": "Typical application documents: certified ID or passport copy, latest academic results, qualification certificates, contact details, passport photo, proof of payment if required, and any programme-specific portfolio or supporting document requested by Admissions.",
        },
        {
            "triggers": ["fees", "payment", "tuition", "banking", "proof of payment"],
            "answer": "For fees, the visitor should request the current fee quotation from Admissions or Finance. Payments should use the student/applicant reference, and proof of payment should be sent back to Finance or Admissions for allocation.",
        },
        {
            "triggers": ["where is it located", "location", "located", "address", "directions", "where is the school"],
            "answer": "Use the official Limkokwing campus page or Admissions Office for the exact campus address. For reception, direct visitors to Admissions or Campus Administration before travelling.",
        },
        {
            "triggers": ["color", "colour", "school color", "school colour", "brand color", "brand colour"],
            "answer": "Limkokwing branding is commonly seen in black, white, and red.",
        },
    ],
    "irca-glowdom-africa": [
        {
            "triggers": ["summary", "all data", "tell me about", "profile", "about irca", "about glowdom"],
            "answer": "IRCA-GLOWDOM AFRICA demo profile: CEO/main contact is Sebulon. Reception desks: Office Administrator for general inquiries, Training Coordinator for course bookings, Audit/Compliance Coordinator for audits and certification support, and Finance for quotations, invoices, and proof of payment. Demo services include training coordination, audit preparation, ISO/compliance support, certification guidance, workplace systems support, and appointment bookings.",
        },
        {
            "triggers": ["who is the ceo", "ceo", "chief executive", "sebulon", "who is sebulon"],
            "answer": "Sebulon is the CEO and main contact person for IRCA-GLOWDOM AFRICA in this demo knowledge base. Route CEO, management, partnership, and escalation questions to Sebulon.",
        },
        {
            "triggers": ["who is the director", "director", "manager", "principal", "head", "owner", "managing director"],
            "answer": "Sebulon is the named management contact for IRCA-GLOWDOM AFRICA. For a formal receptionist answer: Sebulon is listed as CEO/main office contact in the demo records.",
        },
        {
            "triggers": ["services", "what do they do", "offer", "training", "audit", "iso"],
            "answer": "IRCA-GLOWDOM AFRICA can assist with training coordination, audit preparation, compliance support, certification guidance, workplace systems support, and appointment bookings for business clients.",
        },
        {
            "triggers": ["contact", "phone", "email", "who do i contact", "appointment"],
            "answer": "For IRCA-GLOWDOM AFRICA, contact Sebulon for management matters, the Office Administrator for general inquiries, the Training Coordinator for course bookings, and Finance for quotations or invoices. Provide your name, company, phone/email, service needed, and preferred date.",
        },
        {
            "triggers": ["requirements", "documents", "what documents", "certificate", "company documents"],
            "answer": "Typical IRCA-GLOWDOM AFRICA documents: company name and registration details, contact person, phone/email, service scope, prior certificates or audit reports if available, training participant list for courses, and proof of payment when requested.",
        },
        {
            "triggers": ["fees", "payment", "invoice", "quotation", "quote", "cost"],
            "answer": "For fees, request a quotation from Finance or the Office Administrator. Once accepted, pay using the invoice reference and send proof of payment so the booking or service file can be confirmed.",
        },
    ],
    "windhoek-municipality": [
        {
            "triggers": ["summary", "all data", "tell me about", "profile", "about municipality", "about windhoek"],
            "answer": "City of Windhoek public profile: the official site lists services such as City Police, Economic Development and Community Services, Electricity, Finance and Customer Services, Infrastructure/Water/Technical Services, Housing and Human Settlements, and Urban and Transport Planning. Official contact details shown include Independence Avenue, +264 81 950 3777, and enquiry@windhoekcc.org.na. Public sources currently list Ndeshihafela Larandja as mayor, while the City website council-profile area should be checked for the latest official council listing.",
        },
        {
            "triggers": ["who is the mayor", "mayor"],
            "answer": "Ndeshihafela Larandja is listed as Mayor of Windhoek from 2025.",
        },
        {
            "triggers": ["deputy mayor"],
            "answer": "For demo purposes: public sources list Albertina Amutenya as Deputy Mayor of Windhoek. Please verify with the City of Windhoek council office for official use.",
        },
        {
            "triggers": ["ceo", "chief executive", "chief executive officer"],
            "answer": "For the City of Windhoek CEO, reception should verify the current Chief Executive Officer through the Office of the CEO. I do not have a confirmed current CEO name loaded in this demo.",
        },
        {
            "triggers": ["contact", "phone", "email", "where is", "address"],
            "answer": "City of Windhoek contact details shown on the official site include Independence Avenue, phone +264 81 950 3777, and email enquiry@windhoekcc.org.na.",
        },
        {
            "triggers": ["services", "what do they do", "water", "electricity", "account", "rates", "permits"],
            "answer": "City of Windhoek services include City Police, electricity, finance and customer services, infrastructure and water, housing and human settlements, urban and transport planning, and economic/community services.",
        },
        {
            "triggers": ["documents", "requirements", "what documents", "account", "erf", "property"],
            "answer": "For municipal counter services, typical documents are ID, municipal account number, erf/property details, proof of address, completed application form, and proof of payment where applicable.",
        },
        {
            "triggers": ["pay", "payment", "bill", "rates", "tax", "water account", "electricity account"],
            "answer": "For municipal payments, keep the municipal account number/reference ready. Use the correct account or payment channel, then keep proof of payment for customer care follow-up if the account is not updated.",
        },
    ],
}

PUBLIC_SEARCH_QUERIES = {
    "limkokwing-university": "Limkokwing University official admissions programmes contact founder social media",
    "irca-glowdom-africa": "IRCA GLOWDOM AFRICA official contact services Sebulon social media",
    "windhoek-municipality": "City of Windhoek official contact services mayor council social media",
}

PUBLIC_SEARCH_HINTS = {
    "limkokwing-university": "official website, admissions pages, programme pages, public social profiles",
    "irca-glowdom-africa": "official pages, public business listings, public social profiles",
    "windhoek-municipality": "City of Windhoek official website, council pages, public notices, public social profiles",
}

PUBLIC_PAGES = {
    "limkokwing-university": [
        "https://en.wikipedia.org/wiki/Limkokwing_University_of_Creative_Technology",
        "https://en.wikipedia.org/wiki/Lim_Kok_Wing",
        "https://www.limkokwing.net/",
    ],
    "irca-glowdom-africa": [
    ],
    "windhoek-municipality": [
        "https://www.windhoekcc.org.na/",
        "https://en.wikipedia.org/wiki/Windhoek",
        "https://en.wikipedia.org/wiki/List_of_mayors_of_Windhoek",
        "https://en.wikipedia.org/wiki/Ndeshihafela_Larandja",
    ],
}

PUBLIC_SOCIAL_HINTS = {
    "limkokwing-university": "Also check public Facebook, LinkedIn, Instagram, YouTube, and official campus pages for recent announcements.",
    "irca-glowdom-africa": "Also check public Facebook, LinkedIn, Google Business/Profile results, and company directory listings for recent announcements.",
    "windhoek-municipality": "Also check City of Windhoek public Facebook, LinkedIn, YouTube, public notices, council pages, and the e-portal.",
}

STATIC_PUBLIC_LOOKUP = {
    "limkokwing-university": [
        "- Public source: Limkokwing public profiles identify Tan Sri Lim Kok Wing as founder/founding president.",
        "- Public source: Limkokwing University public profiles describe programmes in design, multimedia, communication, business, computing, technology, architecture, and creative fields.",
        "- Public/social check: also check public Facebook, LinkedIn, Instagram, YouTube, and official campus pages for recent announcements.",
    ],
    "irca-glowdom-africa": [
        "- Demo/public lookup note: public indexed data for IRCA-GLOWDOM AFRICA is limited; current demo record names Sebulon as CEO/main contact.",
        "- Public/social check: also check public Facebook, LinkedIn, Google Business/Profile results, and company directory listings for recent announcements.",
    ],
    "windhoek-municipality": [
        "- Public source: City of Windhoek official site lists services including City Police, Electricity, Finance and Customer Services, Infrastructure/Water/Technical Services, Housing, and Urban/Transport Planning.",
        "- Public source: City of Windhoek official site shows Independence Avenue, +264 81 950 3777, and enquiry@windhoekcc.org.na.",
        "- Public source: public mayor listings identify Ndeshihafela Larandja as Mayor of Windhoek from 2025; verify official council pages for current use.",
        "- Public/social check: also check City of Windhoek public Facebook, LinkedIn, YouTube, public notices, council pages, and the e-portal.",
    ],
}

STOPWORDS = {
    "the", "and", "for", "are", "you", "your", "who", "what", "when", "where", "how",
    "can", "does", "with", "from", "this", "that", "about", "please", "tell", "need",
    "want", "is", "of", "to", "a", "an", "in", "on", "it",
}


def score_note(question, note):
    words = {
        word.strip(".,?!").lower()
        for word in question.split()
        if len(word.strip(".,?!")) > 2 and word.strip(".,?!").lower() not in STOPWORDS
    }
    keyword_hits = sum(1 for keyword in note["keywords"] if keyword in question.lower())
    title_hits = sum(1 for word in words if word in note["title"].lower())
    answer_hits = sum(1 for word in words if word in note["answer"].lower())
    return keyword_hits * 4 + title_hits * 2 + answer_hits


def answer_from_offline_cache(question, offline_cache):
    if not isinstance(offline_cache, list):
        return None
    terms = {
        word.strip(".,?!").lower()
        for word in question.split()
        if len(word.strip(".,?!")) > 2 and word.strip(".,?!").lower() not in STOPWORDS
    }
    ranked = []
    for item in offline_cache:
        text = str(item.get("text", "")).strip()
        source = str(item.get("source", "Offline cache")).strip()
        if not text:
            continue
        score = sum(1 for term in terms if term in text.lower())
        if score:
            ranked.append((score, source, text))
    if not ranked:
        return None
    score, source, text = sorted(ranked, reverse=True)[0]
    return f"Offline cache: {text}\nSource: {source}"


def answer_from_demo_knowledge(bot, question, offline_cache=None):
    direct_answer = answer_direct_question(bot, question)
    if direct_answer:
        return polish_answer(bot, question, direct_answer)

    cached_answer = answer_from_offline_cache(question, offline_cache or [])
    if cached_answer:
        return polish_answer(bot, question, cached_answer)

    public_lookup = static_public_lookup(bot)
    notes = DEMO_KNOWLEDGE.get(bot["slug"], [])
    scored = [(note, score_note(question, note)) for note in notes]
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    best = ranked[0][0] if ranked and ranked[0][1] >= 2 else None
    if not best:
        lower = question.lower()
        if any(word in lower for word in ["who", "principal", "leader", "head", "director", "mayor"]):
            best = next((note for note in notes if "leadership" in note["title"].lower()), None)
        elif any(word in lower for word in ["help", "service", "do", "offer"]):
            best = next((note for note in notes if "service" in note["title"].lower()), None)
    if not best:
        answer = (
            f"{FALLBACK} You can ask me about office hours, location, services, documents, "
            f"fees, applications, appointments, payments, or leadership contacts for {bot['name']}."
        )
        return polish_answer(bot, question, answer)
    answer = (
        f"{best['answer']} "
        f"This is demo guidance from the {bot['name']} sample website notes, so please treat exact dates, fees, and addresses as placeholders."
    )
    return polish_answer(bot, question, answer)


def answer_direct_question(bot, question):
    lower = question.lower()
    for item in DIRECT_ANSWERS.get(bot["slug"], []):
        if any(trigger in lower for trigger in item["triggers"]):
            return item["answer"]
    return None


def with_public_lookup(answer, public_lookup):
    if not public_lookup:
        return answer
    return f"{answer}\n\nPublic lookup:\n{public_lookup}"


def polish_answer(bot, question, answer):
    clean = concise_answer(answer)
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return clean
    try:
        return openai_rewrite(bot, question, clean, api_key)
    except Exception:
        return clean


def concise_answer(answer):
    answer = answer.split("\n\nPublic lookup:")[0]
    answer = answer.replace("For demo purposes: ", "")
    answer = answer.replace("in this demo knowledge base", "")
    answer = answer.replace("in this demo", "")
    answer = re.sub(r"\s*This is demo guidance.*$", "", answer)
    answer = re.sub(r"\s*For official use.*$", "", answer)
    answer = re.sub(r"\s*The City website.*verify.*$", "", answer)
    answer = re.sub(r"\s*Please verify.*$", "", answer)
    answer = re.sub(r"\s+([.?!])", r"\1", answer)
    answer = re.sub(r"\s+", " ", answer).strip()
    sentences = re.split(r"(?<=[.!?])\s+", answer)
    return " ".join(sentences[:2]).strip()


def openai_rewrite(bot, question, answer, api_key):
    payload = {
        "model": os.environ.get("OPENAI_CHAT_MODEL", "gpt-4.1-mini"),
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a professional receptionist. Answer only the user's question. "
                    "Keep it short, clear, and helpful. Do not mention disclaimers, demos, public lookup, "
                    "or internal sources. Use only the provided answer content."
                ),
            },
            {
                "role": "user",
                "content": f"Bot: {bot['name']}\nQuestion: {question}\nAnswer content: {answer}",
            },
        ],
        "temperature": 0.2,
        "max_tokens": 100,
    }
    request = Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def static_public_lookup(bot):
    return "\n".join(STATIC_PUBLIC_LOOKUP.get(bot["slug"], []))


def public_web_lookup(bot, question):
    page_snippets = lookup_public_pages(bot, question)
    if page_snippets:
        social_hint = PUBLIC_SOCIAL_HINTS.get(bot["slug"])
        if social_hint:
            page_snippets.append(f"- Public/social check: {social_hint}")
        return "\n".join(page_snippets[:4])

    query = f"{bot['name']} {question} {PUBLIC_SEARCH_QUERIES.get(bot['slug'], '')}"
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 GlowdomReceptionDemo/1.0",
                "Accept": "text/html",
            },
        )
        with urlopen(request, timeout=2) as response:
            page = response.read(120000).decode("utf-8", errors="ignore")
    except Exception:
        if page_snippets:
            return "\n".join(page_snippets)
        return (
            f"Live public search is currently unavailable from this demo server. "
            f"Suggested public sources to check: {PUBLIC_SEARCH_HINTS.get(bot['slug'], 'official websites and public profiles')}."
        )

    results = extract_search_results(page)
    combined = [f"- {title}: {snippet}" for title, snippet in results[:2]]
    if not combined:
        return (
            f"No clear public search snippets were found in this quick lookup. "
            f"Suggested public sources to check: {PUBLIC_SEARCH_HINTS.get(bot['slug'], 'official websites and public profiles')}."
        )
    return "\n".join(combined[:4])


def lookup_public_pages(bot, question):
    snippets = []
    terms = {
        word.strip(".,?!").lower()
        for word in question.split()
        if len(word.strip(".,?!")) > 2 and word.strip(".,?!").lower() not in STOPWORDS
    }
    for url in PUBLIC_PAGES.get(bot["slug"], []):
        try:
            text = fetch_public_text(url)
        except Exception:
            continue
        sentence = best_sentence(text, terms)
        if sentence:
            snippets.append(f"- {short_source(url)}: {sentence}")
        if len(snippets) >= 3:
            break
    return snippets


def fetch_public_text(url):
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 GlowdomReceptionDemo/1.0",
            "Accept": "text/html",
        },
    )
    with urlopen(request, timeout=2) as response:
        page = response.read(140000).decode("utf-8", errors="ignore")
    return clean_html(page)


def best_sentence(text, terms):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    candidates = []
    for sentence in sentences:
        clean = sentence.strip()
        if len(clean) < 40 or len(clean) > 280:
            continue
        if clean.startswith("^") or "retrieved" in clean.lower() or "isbn" in clean.lower():
            continue
        lower = clean.lower()
        score = sum(1 for term in terms if term in lower)
        if score:
            candidates.append((score, clean))
    if not candidates:
        return None
    return sorted(candidates, reverse=True)[0][1]


def short_source(url):
    parsed = urlparse(url)
    host = parsed.netloc.replace("www.", "")
    path = parsed.path.strip("/").replace("_", " ")
    if path:
        return f"{host} / {path[:45]}"
    return host


def extract_search_results(page):
    page = page.replace("\n", " ")
    pairs = []
    result_blocks = re.findall(r'<div class="result results_links.*?</div>\\s*</div>', page)
    if not result_blocks:
        result_blocks = re.findall(r'<a rel="nofollow" class="result__a".*?</a>.*?<a class="result__snippet".*?</a>', page)
    for block in result_blocks:
        title_match = re.search(r'class="result__a"[^>]*>(.*?)</a>', block)
        snippet_match = re.search(r'class="result__snippet"[^>]*>(.*?)</a>', block)
        if not title_match:
            continue
        title = clean_html(title_match.group(1))
        snippet = clean_html(snippet_match.group(1)) if snippet_match else "Public result found."
        if title:
            pairs.append((title, snippet))
    return pairs


def clean_html(value):
    value = re.sub(r"<.*?>", " ", value)
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return

    def log_error(self, format, *args):
        message = format % args
        if "ConnectionResetError" in message or "BrokenPipeError" in message:
            return
        super().log_error(format, *args)

    def do_OPTIONS(self):
        self._send(200, {"ok": True})

    def do_GET(self):
        path = urlparse(self.path).path
        if path in {"/", "/demo.html"}:
            self._send_file(FRONTEND_ROOT / "demo.html", "text/html; charset=utf-8")
            return
        if path == "/api/health":
            self._send(200, {"status": "ok", "mode": "stdlib-demo"})
            return
        if path == "/api/bots":
            self._send(200, BOTS)
            return
        if path.startswith("/api/bots/"):
            slug = path.split("/")[3]
            bot = next((item for item in BOTS if item["slug"] == slug), None)
            self._send(200 if bot else 404, bot or {"detail": "Bot not found"})
            return
        self._send(404, {"detail": "Not found"})

    def _send_file(self, file_path, content_type):
        if not file_path.exists():
            self._send(404, {"detail": "File not found"})
            return
        try:
            body = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            return

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if path == "/api/auth/login":
            self._send(200, {"access_token": "demo-token", "token_type": "bearer"})
            return
        if path.startswith("/api/bots/") and path.endswith("/chat"):
            slug = path.split("/")[3]
            bot = next((item for item in BOTS if item["slug"] == slug), None)
            if not bot:
                self._send(404, {"detail": "Bot not found"})
                return
            answer = answer_from_demo_knowledge(
                bot,
                payload.get("message", ""),
                payload.get("offline_cache", []),
            )
            self._send(
                200,
                {
                    "session_id": payload.get("session_id") or "demo-session",
                    "answer": answer,
                    "cache_items": offline_cache_items(bot),
                    "sources": SOURCE_LINKS.get(bot["slug"], []),
                },
            )
            return
        self._send(404, {"detail": "Not found"})


def offline_cache_items(bot):
    items = []
    for line in STATIC_PUBLIC_LOOKUP.get(bot["slug"], []):
        items.append({"source": "Public source summary", "text": line.replace("- ", "", 1)})
    for entry in DIRECT_ANSWERS.get(bot["slug"], []):
        items.append({"source": f"{bot['name']} direct answer", "text": entry["answer"]})
    for entry in DEMO_KNOWLEDGE.get(bot["slug"], []):
        items.append({"source": f"{bot['name']} demo note: {entry['title']}", "text": entry["answer"]})
    return items


if __name__ == "__main__":
    port = int(os.environ.get("PORT") or os.environ.get("DEMO_API_PORT", "8010"))
    try:
        print(f"Glowdom demo running on port {port}")
        HTTPServer(("0.0.0.0", port), Handler).serve_forever()
    except PermissionError:
        print(
            f"Port {port} is already in use or blocked by Windows permissions.\n"
            f"If the app is already running, open http://127.0.0.1:5180/demo.html.\n"
            f"To run another copy, use a different port, for example:\n"
            f"  $env:DEMO_API_PORT='8030'; python demo_api_server.py",
            file=sys.stderr,
        )
        raise SystemExit(1)
