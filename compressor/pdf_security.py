import fitz  # PyMuPDF

def encrypt_pdf(input_path: str, output_path: str, user_password: str, owner_password: str = None):
    """
    Encrypts a PDF document with password protection using AES-256 encryption.
    """
    if not user_password:
        raise ValueError("User password cannot be empty.")

    owner_pw = owner_password if owner_password else user_password

    doc = fitz.open(input_path)
    # Save with AES-256 encryption
    doc.save(
        output_path,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw=owner_pw,
        user_pw=user_password,
        permissions=fitz.PDF_PERM_ACCESSIBILITY | fitz.PDF_PERM_PRINT
    )
    doc.close()
    return {
        "status": "encrypted",
        "output_path": output_path
    }

def decrypt_pdf(input_path: str, output_path: str, password: str):
    """
    Decrypts a password-protected PDF document and saves an unencrypted copy.
    """
    doc = fitz.open(input_path)
    if not doc.is_encrypted:
        doc.save(output_path)
        doc.close()
        return {"status": "already_unencrypted", "output_path": output_path}

    if not password or not doc.authenticate(password):
        doc.close()
        raise ValueError("Invalid password for encrypted PDF.")

    # Save clean unencrypted copy
    doc.save(output_path, encryption=fitz.PDF_ENCRYPT_NONE)
    doc.close()
    return {
        "status": "decrypted",
        "output_path": output_path
    }
