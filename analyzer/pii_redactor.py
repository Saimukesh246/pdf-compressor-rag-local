import fitz  # PyMuPDF
import re

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', re.IGNORECASE)
PHONE_REGEX = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
CREDIT_CARD_REGEX = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
SSN_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

def redact_pii_from_pdf(
    input_path: str,
    output_path: str,
    redact_email: bool = True,
    redact_phone: bool = True,
    redact_credit_card: bool = True,
    redact_ssn: bool = True,
    password: str = None
):
    """
    Scans PDF text for sensitive PII patterns and applies permanent black redact annotations.
    """
    doc = fitz.open(input_path)
    if doc.is_encrypted:
        if password and doc.authenticate(password):
            pass
        else:
            raise ValueError("Encrypted PDF requires a valid password.")

    total_redactions = 0

    patterns = []
    if redact_email: patterns.append((EMAIL_REGEX, "Email"))
    if redact_phone: patterns.append((PHONE_REGEX, "Phone"))
    if redact_credit_card: patterns.append((CREDIT_CARD_REGEX, "CreditCard"))
    if redact_ssn: patterns.append((SSN_REGEX, "SSN"))

    for page in doc:
        text = page.get_text("text")
        found_terms = set()

        for regex, category in patterns:
            matches = regex.findall(text)
            for m in matches:
                found_terms.add(m)

        for term in found_terms:
            quads = page.search_for(term)
            for quad in quads:
                page.add_redact_annot(quad, text="[REDACTED]", fill=(0, 0, 0))
                total_redactions += 1

        page.apply_redactions()

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return {
        "status": "success",
        "output_path": output_path,
        "total_redactions": total_redactions
    }
