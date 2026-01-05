import subprocess
import platform


def compress_with_ghostscript(
    input_pdf: str,
    output_pdf: str,
    level: str = "screen"
):
    """
    Compression levels:
    screen  -> maximum compression
    ebook   -> high compression
    printer -> medium
    prepress -> low
    """

    gs_cmd = "gswin64c" if platform.system() == "Windows" else "gs"

    command = [
        gs_cmd,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{level}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_pdf}",
        input_pdf,
    ]

    subprocess.run(command, check=True)
