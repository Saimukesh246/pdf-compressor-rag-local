// PDF Compressor & RAG Assistant Client Logic

document.addEventListener('DOMContentLoaded', () => {
  checkHealth();
  setupFileInputs();
});

async function checkHealth() {
  const healthText = document.getElementById('healthText');
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    if (data.status === 'healthy') {
      const gsState = data.ghostscript_available ? 'Ghostscript Active' : 'PyMuPDF Serverless Fallback';
      healthText.innerText = `Engine Ready (${gsState})`;
    } else {
      healthText.innerText = 'Engine Offline';
    }
  } catch (err) {
    healthText.innerText = 'Serverless Function Ready';
  }
}

function switchTab(tabName) {
  const tabs = ['compress', 'batch', 'ask', 'manip', 'about'];
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

function setupFileInputs() {
  const singleInput = document.getElementById('fileSingle');
  const btnCompress = document.getElementById('btnCompress');
  const fileNameSingle = document.getElementById('fileNameSingle');

  if (singleInput) {
    singleInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        fileNameSingle.innerText = `📁 ${e.target.files[0].name}`;
        btnCompress.disabled = false;
      }
    });
  }

  const batchInput = document.getElementById('fileBatch');
  const btnBatch = document.getElementById('btnBatch');
  const batchCount = document.getElementById('batchCount');

  if (batchInput) {
    batchInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        batchCount.innerText = `📦 ${e.target.files.length} PDF files selected`;
        btnBatch.disabled = false;
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
  btnCompress.innerText = '⏳ Compressing PDF...';

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

    document.getElementById('decModeBadge').innerText = data.decision_mode;
    document.getElementById('decStrategyText').innerText = data.strategy;

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

  } catch (err) {
    alert(`Compression Error: ${err.message}`);
  } finally {
    btnCompress.disabled = false;
    btnCompress.innerText = '🚀 Compress PDF';
  }
}

async function runBatchCompression() {
  const fileInput = document.getElementById('fileBatch');
  const btnBatch = document.getElementById('btnBatch');

  if (!fileInput.files || fileInput.files.length === 0) return;

  btnBatch.disabled = true;
  btnBatch.innerText = '⏳ Processing Batch...';

  const formData = new FormData();
  for (let i = 0; i < fileInput.files.length; i++) {
    formData.append('files', fileInput.files[i]);
  }
  formData.append('level', 'medium');

  try {
    const response = await fetch('/api/batch', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Batch compression failed');
    }

    const data = await response.json();

    const tbody = document.getElementById('batchTableBody');
    tbody.innerHTML = '';

    data.results.forEach(res => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${res.filename}</td>
        <td>${res.stats.original_size_kb.toFixed(1)} KB</td>
        <td>${res.stats.compressed_size_kb.toFixed(1)} KB</td>
        <td style="color: var(--success); font-weight: 600;">${res.stats.reduction_percent.toFixed(1)}%</td>
      `;
      tbody.appendChild(tr);
    });

    document.getElementById('batchResults').classList.remove('hidden');

    const btnBatchDownload = document.getElementById('btnBatchDownload');
    btnBatchDownload.href = `data:application/zip;base64,${data.zip_b64}`;

  } catch (err) {
    alert(`Batch Compression Error: ${err.message}`);
  } finally {
    btnBatch.disabled = false;
    btnBatch.innerText = '📦 Compress All PDFs & Export ZIP';
  }
}

async function runAskQuery() {
  const fileInput = document.getElementById('fileAsk');
  const queryInput = document.getElementById('inputQuery');
  const btnAsk = document.getElementById('btnAsk');

  if (!fileInput.files || fileInput.files.length === 0) {
    alert('Please select a PDF file first.');
    return;
  }
  if (!queryInput.value.trim()) {
    alert('Please enter a search prompt.');
    return;
  }

  btnAsk.disabled = true;
  btnAsk.innerText = '⏳ Searching...';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('query', queryInput.value.trim());

  try {
    const response = await fetch('/api/ask', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'RAG query failed');
    }

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

  } catch (err) {
    alert(`RAG Query Error: ${err.message}`);
  } finally {
    btnAsk.disabled = false;
    btnAsk.innerText = '🔍 Search Q&A';
  }
}

async function runMindmapGen() {
  const fileInput = document.getElementById('fileAsk');
  const btnMindmap = document.getElementById('btnMindmap');

  if (!fileInput.files || fileInput.files.length === 0) {
    alert('Please select a PDF file first.');
    return;
  }

  btnMindmap.disabled = true;
  btnMindmap.innerText = '⏳ Generating...';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const response = await fetch('/api/mindmap', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Mindmap generation failed');
    }

    const data = await response.json();

    document.getElementById('askSynthesizedAnswer').innerText = data.summary_text;
    document.getElementById('mermaidCodeText').innerText = data.mermaid_code;
    document.getElementById('mindmapBox').classList.remove('hidden');
    document.getElementById('askResultsArea').classList.remove('hidden');

  } catch (err) {
    alert(`Mindmap Error: ${err.message}`);
  } finally {
    btnMindmap.disabled = false;
    btnMindmap.innerText = '🧠 Generate Mindmap';
  }
}

async function runMergePDFs() {
  const fileInput = document.getElementById('fileMerge');
  const btnMerge = document.getElementById('btnMerge');

  if (!fileInput.files || fileInput.files.length < 2) {
    alert('Please select at least 2 PDF files to merge.');
    return;
  }

  btnMerge.disabled = true;
  btnMerge.innerText = '⏳ Merging PDFs...';

  const formData = new FormData();
  for (let i = 0; i < fileInput.files.length; i++) {
    formData.append('files', fileInput.files[i]);
  }

  try {
    const response = await fetch('/api/merge', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Merging failed');
    }

    const data = await response.json();

    const btnDownload = document.getElementById('btnDownloadMerge');
    btnDownload.href = `data:application/pdf;base64,${data.merged_file_b64}`;
    document.getElementById('mergeResults').classList.remove('hidden');

  } catch (err) {
    alert(`Merge Error: ${err.message}`);
  } finally {
    btnMerge.disabled = false;
    btnMerge.innerText = '🔗 Merge PDFs';
  }
}

async function runSplitPDF() {
  const fileInput = document.getElementById('fileSplit');
  const rangeInput = document.getElementById('inputRange');
  const btnSplit = document.getElementById('btnSplit');

  if (!fileInput.files || fileInput.files.length === 0) return;

  btnSplit.disabled = true;
  btnSplit.innerText = '⏳ Splitting PDF...';

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('range_str', rangeInput.value.trim());

  try {
    const response = await fetch('/api/split', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || 'Splitting failed');
    }

    const data = await response.json();

    const btnDownload = document.getElementById('btnDownloadSplit');
    btnDownload.href = `data:application/pdf;base64,${data.split_file_b64}`;
    document.getElementById('splitResults').classList.remove('hidden');

  } catch (err) {
    alert(`Split Error: ${err.message}`);
  } finally {
    btnSplit.disabled = false;
    btnSplit.innerText = '✂️ Split PDF Pages';
  }
}
