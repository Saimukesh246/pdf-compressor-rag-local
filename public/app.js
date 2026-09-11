// PDF Compressor & AI Enterprise Suite Production Client Logic

document.addEventListener('DOMContentLoaded', () => {
  checkHealth();
  setupFileInputs();
});

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

async function checkHealth() {
  const healthText = document.getElementById('healthText');
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    if (data.status === 'healthy') {
      const gsState = data.ghostscript_available ? 'Ghostscript Active' : 'PyMuPDF Fallback';
      healthText.innerHTML = `<span style="color: #6ee7b7">🟢 FastAPI Online</span> &nbsp;|&nbsp; ⚡ ${gsState}`;
    } else {
      healthText.innerText = 'Engine Offline';
    }
  } catch (err) {
    healthText.innerText = 'FastAPI Engine Ready';
  }
}

function switchTab(tabName) {
  const tabs = ['compress', 'security', 'convert', 'ask', 'manip', 'about'];
  tabs.forEach(t => {
    const btn = document.getElementById(`tab${t.charAt(0).toUpperCase() + t.slice(1)}`);
    const sec = document.getElementById(`sec${t.charAt(0).toUpperCase() + t.slice(1)}`);
    if (btn && sec) {
      if (t === tabName) {
        btn.classList.add('active');
        sec.classList.add('active');
      } else {
        btn.classList.remove('active');
        sec.classList.remove('active');
      }
    }
  });
}

function selectProfile(level) {
  ['profMedium', 'profLow', 'profHigh'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.remove('active');
  });

  const levelSelect = document.getElementById('levelSelect');
  if (levelSelect) levelSelect.value = level;

  if (level === 'medium') document.getElementById('profMedium').classList.add('active');
  if (level === 'low') document.getElementById('profLow').classList.add('active');
  if (level === 'high') document.getElementById('profHigh').classList.add('active');
}

function formatBytes(bytes, decimals = 1) {
  if (bytes === 0) return '0 KB';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function clearSingleFile(event) {
  if (event) event.stopPropagation();
  const fileInput = document.getElementById('fileSingle');
  const dropContent = document.querySelector('#dropZoneSingle .drop-zone-content');
  const card = document.getElementById('fileSelectedCard');
  const btnCompress = document.getElementById('btnCompress');

  if (fileInput) fileInput.value = '';
  if (dropContent) dropContent.classList.remove('hidden');
  if (card) card.classList.add('hidden');
  if (btnCompress) btnCompress.disabled = true;

  document.getElementById('analysisPlaceholder').classList.remove('hidden');
  document.getElementById('analysisResults').classList.add('hidden');
  document.getElementById('previewCard').classList.add('hidden');
}

function setupFileInputs() {
  const singleInput = document.getElementById('fileSingle');
  const btnCompress = document.getElementById('btnCompress');
  const dropContent = document.querySelector('#dropZoneSingle .drop-zone-content');
  const selectedCard = document.getElementById('fileSelectedCard');

  if (singleInput) {
    singleInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        const file = e.target.files[0];
        document.getElementById('fileNameSingle').innerText = file.name;
        document.getElementById('fileSizeSingle').innerText = formatBytes(file.size);
        if (dropContent) dropContent.classList.add('hidden');
        if (selectedCard) selectedCard.classList.remove('hidden');
        btnCompress.disabled = false;
        showToast(`Selected document: ${file.name}`, 'info');
      }
    });
  }

  const wmInput = document.getElementById('fileWatermark');
  const btnWatermark = document.getElementById('btnWatermark');
  if (wmInput) {
    wmInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        document.getElementById('fileNameWatermark').innerText = `🏷️ ${e.target.files[0].name}`;
        btnWatermark.disabled = false;
      }
    });
  }

  const redInput = document.getElementById('fileRedact');
  const btnRedact = document.getElementById('btnRedact');
  if (redInput) {
    redInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        document.getElementById('fileNameRedact').innerText = `🕵️ ${e.target.files[0].name}`;
        btnRedact.disabled = false;
      }
    });
  }

  const pdfToImgInput = document.getElementById('filePdfToImg');
  const btnPdfToImg = document.getElementById('btnPdfToImg');
  if (pdfToImgInput) {
    pdfToImgInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        document.getElementById('fileNamePdfToImg').innerText = `🖼️ ${e.target.files[0].name}`;
        btnPdfToImg.disabled = false;
      }
    });
  }

  const exportMdInput = document.getElementById('fileExportMd');
  const btnExportMd = document.getElementById('btnExportMd');
  if (exportMdInput) {
    exportMdInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        document.getElementById('fileNameExportMd').innerText = `📝 ${e.target.files[0].name}`;
        btnExportMd.disabled = false;
      }
    });
  }

  const askInput = document.getElementById('fileAsk');
  const btnAsk = document.getElementById('btnAsk');
  const btnMindmap = document.getElementById('btnMindmap');
  const fileNameAsk = document.getElementById('fileNameAsk');

  if (askInput) {
    askInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        fileNameAsk.innerText = `📄 ${e.target.files[0].name}`;
        btnAsk.disabled = false;
        if (btnMindmap) btnMindmap.disabled = false;
      }
    });
  }

  const mergeInput = document.getElementById('fileMerge');
  const btnMerge = document.getElementById('btnMerge');
  const fileNameMerge = document.getElementById('fileNameMerge');

  if (mergeInput) {
    mergeInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        fileNameMerge.innerText = `🔗 ${e.target.files.length} PDFs selected`;
        btnMerge.disabled = false;
      }
    });
  }

  const splitInput = document.getElementById('fileSplit');
  const btnSplit = document.getElementById('btnSplit');
  const fileNameSplit = document.getElementById('fileNameSplit');

  if (splitInput) {
    splitInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        fileNameSplit.innerText = `✂️ ${e.target.files[0].name}`;
        btnSplit.disabled = false;
      }
    });
  }
}

async function runSingleCompression() {
  const fileInput = document.getElementById('fileSingle');
  const levelSelect = document.getElementById('levelSelect');
  const inputPassword = document.getElementById('inputPassword');
  const chkStripMeta = document.getElementById('chkStripMeta');
  const chkGrayscale = document.getElementById('chkGrayscale');
  const btnCompress = document.getElementById('btnCompress');

  if (!fileInput.files || fileInput.files.length === 0) return;

  const file = fileInput.files[0];
  const level = levelSelect.value;
  const password = inputPassword ? inputPassword.value : '';
  const stripMeta = chkStripMeta ? chkStripMeta.checked : false;
  const grayscale = chkGrayscale ? chkGrayscale.checked : false;

  btnCompress.disabled = true;
  btnCompress.innerHTML = '⏳ Analyzing & Compressing PDF...';

  const formData = new FormData();
  formData.append('file', file);
  formData.append('level', level);
  if (password) formData.append('password', password);
  formData.append('strip_metadata', stripMeta);
  formData.append('grayscale', grayscale);

  try {
    const response = await fetch('/api/compress', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Compression failed');
    }

    const data = await response.json();

    document.getElementById('analysisPlaceholder').classList.add('hidden');
    document.getElementById('analysisResults').classList.remove('hidden');

    document.getElementById('metOrigSize').innerText = `${data.stats.original_size_kb.toFixed(1)} KB`;
    document.getElementById('metPageCount').innerText = data.metrics.page_count;
    document.getElementById('metImageCount').innerText = data.metrics.image_count;
    document.getElementById('metTextLength').innerText = data.metrics.text_length;

    const modeBadge = document.getElementById('decModeBadge');
    modeBadge.innerText = data.decision_mode;
    modeBadge.classList.remove('hidden');

    document.getElementById('decStrategyText').innerText = data.strategy;

    document.getElementById('heroReductionValue').innerText = `-${data.stats.reduction_percent.toFixed(1)}%`;
    document.getElementById('metCompSize').innerText = `${data.stats.compressed_size_kb.toFixed(1)} KB`;
    document.getElementById('metReduction').innerText = `${data.stats.reduction_percent.toFixed(1)}%`;
    if (document.getElementById('metPsnr')) {
      document.getElementById('metPsnr').innerText = `${data.stats.psnr_db.toFixed(1)} dB`;
    }
    if (document.getElementById('metSsim')) {
      document.getElementById('metSsim').innerText = `${data.stats.ssim_percent.toFixed(1)}%`;
    }

    document.getElementById('compResultsArea').classList.remove('hidden');

    const btnDownload = document.getElementById('btnDownload');
    btnDownload.href = `data:application/pdf;base64,${data.compressed_file_b64}`;
    btnDownload.download = `compressed_${data.filename}`;

    if (data.preview_original_b64 && data.preview_compressed_b64) {
      document.getElementById('previewCard').classList.remove('hidden');
      document.getElementById('imgPreviewOrig').src = `data:image/png;base64,${data.preview_original_b64}`;
      document.getElementById('imgPreviewComp').src = `data:image/png;base64,${data.preview_compressed_b64}`;
    }

    showToast(`PDF Compressed successfully! Reduced by ${data.stats.reduction_percent.toFixed(1)}%`, 'success');

  } catch (err) {
    showToast(`Compression Error: ${err.message}`, 'error');
  } finally {
    btnCompress.disabled = false;
    btnCompress.innerHTML = '🚀 Compress PDF Document';
  }
}

async function runWatermark() {
  const fileInput = document.getElementById('fileWatermark');
  const textInput = document.getElementById('inputWatermarkText');
  const btnWatermark = document.getElementById('btnWatermark');

  if (!fileInput.files || fileInput.files.length === 0) return;

  btnWatermark.disabled = true;
  btnWatermark.innerHTML = '⏳ Applying Watermark...';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('text', textInput.value.trim() || 'CONFIDENTIAL');

  try {
    const response = await fetch('/api/watermark', { method: 'POST', body: formData });
    if (!response.ok) { const err = await response.json(); throw new Error(err.detail || 'Watermarking failed'); }
    const data = await response.json();

    const btnDownload = document.getElementById('btnDownloadWatermark');
    btnDownload.href = `data:application/pdf;base64,${data.file_b64}`;
    document.getElementById('watermarkResults').classList.remove('hidden');
    showToast('Watermark applied successfully!', 'success');
  } catch (err) {
    showToast(`Watermark Error: ${err.message}`, 'error');
  } finally {
    btnWatermark.disabled = false;
    btnWatermark.innerHTML = '🏷️ Apply Diagonal Watermark';
  }
}

async function runRedactPII() {
  const fileInput = document.getElementById('fileRedact');
  const chkEmail = document.getElementById('chkRedactEmail').checked;
  const chkPhone = document.getElementById('chkRedactPhone').checked;
  const chkCC = document.getElementById('chkRedactCC').checked;
  const btnRedact = document.getElementById('btnRedact');

  if (!fileInput.files || fileInput.files.length === 0) return;

  btnRedact.disabled = true;
  btnRedact.innerHTML = '⏳ Redacting PII...';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('redact_email', chkEmail);
  formData.append('redact_phone', chkPhone);
  formData.append('redact_credit_card', chkCC);

  try {
    const response = await fetch('/api/redact-pii', { method: 'POST', body: formData });
    if (!response.ok) { const err = await response.json(); throw new Error(err.detail || 'Redaction failed'); }
    const data = await response.json();

    const btnDownload = document.getElementById('btnDownloadRedact');
    btnDownload.href = `data:application/pdf;base64,${data.file_b64}`;
    document.getElementById('redactResults').classList.remove('hidden');
    showToast(`Redacted ${data.total_redactions} PII text occurrences!`, 'success');
  } catch (err) {
    showToast(`Redaction Error: ${err.message}`, 'error');
  } finally {
    btnRedact.disabled = false;
    btnRedact.innerHTML = '🕵️ Redact Sensitive PII';
  }
}

async function runPdfToImages() {
  const fileInput = document.getElementById('filePdfToImg');
  const btnPdfToImg = document.getElementById('btnPdfToImg');

  if (!fileInput.files || fileInput.files.length === 0) return;

  btnPdfToImg.disabled = true;
  btnPdfToImg.innerHTML = '⏳ Exporting Images...';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const response = await fetch('/api/pdf-to-images', { method: 'POST', body: formData });
    if (!response.ok) { const err = await response.json(); throw new Error(err.detail || 'Conversion failed'); }
    const data = await response.json();

    const btnDownload = document.getElementById('btnDownloadPdfToImg');
    btnDownload.href = `data:application/zip;base64,${data.zip_b64}`;
    document.getElementById('pdfToImgResults').classList.remove('hidden');
    showToast('PDF pages exported to PNG ZIP archive!', 'success');
  } catch (err) {
    showToast(`Conversion Error: ${err.message}`, 'error');
  } finally {
    btnPdfToImg.disabled = false;
    btnPdfToImg.innerHTML = '🖼️ Convert PDF to PNG ZIP';
  }
}

async function runExportMarkdown() {
  const fileInput = document.getElementById('fileExportMd');
  const btnExportMd = document.getElementById('btnExportMd');

  if (!fileInput.files || fileInput.files.length === 0) return;

  btnExportMd.disabled = true;
  btnExportMd.innerHTML = '⏳ Exporting Markdown...';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const response = await fetch('/api/export-markdown', { method: 'POST', body: formData });
    if (!response.ok) { const err = await response.json(); throw new Error(err.detail || 'Export failed'); }
    const data = await response.json();

    document.getElementById('markdownOutputText').innerText = data.markdown_text;
    document.getElementById('exportMdResults').classList.remove('hidden');
    showToast(`Exported ${data.page_count} pages to Markdown!`, 'success');
  } catch (err) {
    showToast(`Export Error: ${err.message}`, 'error');
  } finally {
    btnExportMd.disabled = false;
    btnExportMd.innerHTML = '📝 Export Content to Markdown';
  }
}

function copyMarkdownText() {
  const text = document.getElementById('markdownOutputText').innerText;
  navigator.clipboard.writeText(text).then(() => {
    showToast('Markdown text copied to clipboard!', 'success');
  });
}

async function runAskQuery() {
  const fileInput = document.getElementById('fileAsk');
  const queryInput = document.getElementById('inputQuery');
  const btnAsk = document.getElementById('btnAsk');

  if (!fileInput.files || fileInput.files.length === 0) {
    showToast('Please select a PDF file first.', 'error');
    return;
  }
  if (!queryInput.value.trim()) {
    showToast('Please enter a search question.', 'error');
    return;
  }

  btnAsk.disabled = true;
  btnAsk.innerHTML = '⏳ Searching RAG Index...';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('query', queryInput.value.trim());

  try {
    const response = await fetch('/api/ask', { method: 'POST', body: formData });
    if (!response.ok) { const err = await response.json(); throw new Error(err.detail || 'RAG query failed'); }
    const data = await response.json();

    if (document.getElementById('askSynthesizedAnswer')) {
      document.getElementById('askSynthesizedAnswer').innerText = data.synthesized_answer || 'No synthesis generated.';
    }

    const container = document.getElementById('askMatchesContainer');
    container.innerHTML = '';

    if (data.results.length === 0) {
      container.innerHTML = '<p class="placeholder-text">No matching passages found in this document.</p>';
    } else {
      data.results.forEach((match, idx) => {
        const card = document.createElement('div');
        card.className = 'rag-match-card';
        card.innerHTML = `
          <div class="header">
            <span>Match [${idx + 1}] — Page ${match.page}</span>
            <span class="score">Relevance: ${(match.similarity * 100).toFixed(1)}%</span>
          </div>
          <p>${match.text}</p>
        `;
        container.appendChild(card);
      });
    }

    document.getElementById('askResultsArea').classList.remove('hidden');
    showToast('RAG Vector Query completed!', 'success');
  } catch (err) {
    showToast(`RAG Error: ${err.message}`, 'error');
  } finally {
    btnAsk.disabled = false;
    btnAsk.innerHTML = '🔍 Search Q&A';
  }
}

async function runMindmapGen() {
  const fileInput = document.getElementById('fileAsk');
  const btnMindmap = document.getElementById('btnMindmap');

  if (!fileInput.files || fileInput.files.length === 0) {
    showToast('Please select a PDF file first.', 'error');
    return;
  }

  btnMindmap.disabled = true;
  btnMindmap.innerHTML = '⏳ Generating Mindmap...';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const response = await fetch('/api/mindmap', { method: 'POST', body: formData });
    if (!response.ok) { const err = await response.json(); throw new Error(err.detail || 'Mindmap generation failed'); }
    const data = await response.json();

    document.getElementById('askSynthesizedAnswer').innerText = data.summary_text;
    document.getElementById('mermaidCodeText').innerText = data.mermaid_code;
    document.getElementById('mindmapBox').classList.remove('hidden');
    document.getElementById('askResultsArea').classList.remove('hidden');

    showToast('Mindmap generated successfully!', 'success');
  } catch (err) {
    showToast(`Mindmap Error: ${err.message}`, 'error');
  } finally {
    btnMindmap.disabled = false;
    btnMindmap.innerHTML = '🧠 Generate Mindmap';
  }
}

function copyMermaidCode() {
  const code = document.getElementById('mermaidCodeText').innerText;
  navigator.clipboard.writeText(code).then(() => {
    showToast('Mermaid Mindmap code copied to clipboard!', 'success');
  });
}

async function runMergePDFs() {
  const fileInput = document.getElementById('fileMerge');
  const btnMerge = document.getElementById('btnMerge');

  if (!fileInput.files || fileInput.files.length < 2) {
    showToast('Please select at least 2 PDF files to merge.', 'error');
    return;
  }

  btnMerge.disabled = true;
  btnMerge.innerHTML = '⏳ Merging PDFs...';

  const formData = new FormData();
  for (let i = 0; i < fileInput.files.length; i++) {
    formData.append('files', fileInput.files[i]);
  }

  try {
    const response = await fetch('/api/merge', { method: 'POST', body: formData });
    if (!response.ok) { const err = await response.json(); throw new Error(err.detail || 'Merging failed'); }
    const data = await response.json();

    const btnDownload = document.getElementById('btnDownloadMerge');
    btnDownload.href = `data:application/pdf;base64,${data.merged_file_b64}`;
    document.getElementById('mergeResults').classList.remove('hidden');

    showToast(`Successfully merged ${fileInput.files.length} PDFs into ${data.filename}!`, 'success');
  } catch (err) {
    showToast(`Merge Error: ${err.message}`, 'error');
  } finally {
    btnMerge.disabled = false;
    btnMerge.innerHTML = '🔗 Merge PDFs Now';
  }
}

async function runSplitPDF() {
  const fileInput = document.getElementById('fileSplit');
  const rangeInput = document.getElementById('inputRange');
  const btnSplit = document.getElementById('btnSplit');

  if (!fileInput.files || fileInput.files.length === 0) return;

  btnSplit.disabled = true;
  btnSplit.innerHTML = '⏳ Extracting Pages...';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('range_str', rangeInput.value.trim());

  try {
    const response = await fetch('/api/split', { method: 'POST', body: formData });
    if (!response.ok) { const err = await response.json(); throw new Error(err.detail || 'Splitting failed'); }
    const data = await response.json();

    const btnDownload = document.getElementById('btnDownloadSplit');
    btnDownload.href = `data:application/pdf;base64,${data.split_file_b64}`;
    document.getElementById('splitResults').classList.remove('hidden');

    showToast(`Successfully extracted pages (${data.extracted_pages})!`, 'success');
  } catch (err) {
    showToast(`Split Error: ${err.message}`, 'error');
  } finally {
    btnSplit.disabled = false;
    btnSplit.innerHTML = '✂️ Extract PDF Pages';
  }
}
