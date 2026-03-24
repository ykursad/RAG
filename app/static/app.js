const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");
const questionInput = document.getElementById("questionInput");
const askBtn = document.getElementById("askBtn");
const retrieveBtn = document.getElementById("retrieveBtn");
const resetBtn = document.getElementById("resetBtn");
const copyLastAnswerBtn = document.getElementById("copyLastAnswerBtn");
const refreshDocsBtn = document.getElementById("refreshDocsBtn");
const deleteSelectedDocBtn = document.getElementById("deleteSelectedDocBtn");
const topKInput = document.getElementById("topK");
const sourceFilterSelect = document.getElementById("sourceFilterSelect");
const documentListPanel = document.getElementById("documentListPanel");
const chatMessages = document.getElementById("chatMessages");
const sourcesPanel = document.getElementById("sourcesPanel");
const metaPanel = document.getElementById("metaPanel");

let lastBotAnswer = "";

function addMessage(text, role = "bot", meta = "") {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const box = document.createElement("div");

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  box.appendChild(bubble);

  if (meta) {
    const metaDiv = document.createElement("div");
    metaDiv.className = "bot-meta";
    metaDiv.textContent = meta;
    box.appendChild(metaDiv);
  }

  wrapper.appendChild(box);
  chatMessages.appendChild(wrapper);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setLoading(isLoading) {
  uploadBtn.disabled = isLoading;
  askBtn.disabled = isLoading;
  retrieveBtn.disabled = isLoading;
  resetBtn.disabled = isLoading;
  copyLastAnswerBtn.disabled = isLoading;
  refreshDocsBtn.disabled = isLoading;
  deleteSelectedDocBtn.disabled = isLoading;
}

function renderSources(sources) {
  sourcesPanel.innerHTML = "<h3>Kaynak Parçalar</h3>";

  if (!sources || sources.length === 0) {
    sourcesPanel.innerHTML += "<p>Kaynak bulunamadı.</p>";
    return;
  }

  sources.forEach((src, idx) => {
    const div = document.createElement("div");
    div.className = "source-item";

    const meta = document.createElement("div");
    meta.className = "source-meta";

    const sourceName = src.metadata?.source || "-";
    meta.textContent = `Kaynak ${idx + 1} | Belge: ${sourceName} | Sayfa: ${src.page ?? "-"} | Chunk ID: ${src.chunk_id}`;

    const title = document.createElement("h4");
    title.textContent = `Kanıt Kartı ${idx + 1}`;

    const pre = document.createElement("pre");
    pre.textContent = src.text;

    div.appendChild(title);
    div.appendChild(meta);
    div.appendChild(pre);

    sourcesPanel.appendChild(div);
  });
}

function renderMetaPanel(sourceCount, retrievedPages, promptContextLength, retrievedSources = []) {
  metaPanel.innerHTML = `
    <h3>Son Yanıt Özeti</h3>
    <p><strong>Kaynak Sayısı:</strong> ${sourceCount}</p>
    <p><strong>Sayfalar:</strong> ${retrievedPages.length ? retrievedPages.join(", ") : "-"}</p>
    <p><strong>Belgeler:</strong> ${retrievedSources.length ? retrievedSources.join(", ") : "-"}</p>
    <p><strong>Bağlam Uzunluğu:</strong> ${promptContextLength}</p>
  `;
}

function getSourceFilterValue() {
  const value = sourceFilterSelect.value.trim();
  return value ? value : null;
}

async function fetchDocuments() {
  try {
    const response = await fetch("/documents");
    const data = await response.json();

    if (!response.ok) {
      documentListPanel.innerHTML = "<p>Belge listesi alınamadı.</p>";
      return;
    }

    renderDocumentList(data.documents);
    populateSourceFilter(data.documents);
  } catch (error) {
    documentListPanel.innerHTML = "<p>Belge listesi alınırken hata oluştu.</p>";
  }
}

function renderDocumentList(documents) {
  if (!documents || documents.length === 0) {
    documentListPanel.innerHTML = "<p>Henüz indekslenmiş belge yok.</p>";
    return;
  }

  documentListPanel.innerHTML = "";

  documents.forEach((doc) => {
    const div = document.createElement("div");
    div.className = "doc-list-item";
    div.innerHTML = `
      <h4>${doc.source_name}</h4>
      <p>Chunk Sayısı: ${doc.chunk_count}</p>
      <p>Sayfalar: ${doc.pages.length ? doc.pages.join(", ") : "-"}</p>
    `;
    documentListPanel.appendChild(div);
  });
}

function populateSourceFilter(documents) {
  const currentValue = sourceFilterSelect.value;

  sourceFilterSelect.innerHTML = `<option value="">Tüm Belgeler</option>`;

  documents.forEach((doc) => {
    const option = document.createElement("option");
    option.value = doc.source_name;
    option.textContent = doc.source_name;
    sourceFilterSelect.appendChild(option);
  });

  const values = ["", ...documents.map(doc => doc.source_name)];
  if (values.includes(currentValue)) {
    sourceFilterSelect.value = currentValue;
  }
}

uploadBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    uploadStatus.textContent = "Lütfen bir dosya seçin.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    setLoading(true);
    uploadStatus.textContent = "Doküman işleniyor...";

    const response = await fetch("/ingest", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      uploadStatus.textContent = data.detail || "Yükleme hatası";
      return;
    }

    uploadStatus.textContent = `${data.filename} işlendi | Sayfa: ${data.pages} | Chunk: ${data.total_chunks}`;
    addMessage(
      `Doküman indekslendi: ${data.filename}`,
      "bot",
      `Kaynak adı: ${data.source_name} | Toplam sayfa: ${data.pages} | Toplam chunk: ${data.total_chunks}`
    );

    await fetchDocuments();
  } catch (error) {
    uploadStatus.textContent = "Beklenmeyen bir hata oluştu.";
  } finally {
    setLoading(false);
  }
});

askBtn.addEventListener("click", async () => {
  const question = questionInput.value.trim();
  const top_k = Number(topKInput.value || 6);
  const source_filter = getSourceFilterValue();

  if (!question) return;

  addMessage(question, "user");
  questionInput.value = "";

  try {
    setLoading(true);

    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k, source_filter }),
    });

    const data = await response.json();

    if (!response.ok) {
      addMessage(data.detail || "Soru sorulurken hata oluştu.", "bot");
      return;
    }

    lastBotAnswer = data.answer;

    addMessage(
      data.answer,
      "bot",
      `Kaynak sayısı: ${data.source_count} | Sayfalar: ${data.retrieved_pages.join(", ")} | Belgeler: ${data.retrieved_sources.join(", ")} | Bağlam uzunluğu: ${data.prompt_context_length}`
    );

    renderSources(data.sources);
    renderMetaPanel(
      data.source_count,
      data.retrieved_pages,
      data.prompt_context_length,
      data.retrieved_sources
    );
  } catch (error) {
    addMessage("İstek sırasında beklenmeyen bir hata oluştu.", "bot");
  } finally {
    setLoading(false);
  }
});

retrieveBtn.addEventListener("click", async () => {
  const question = questionInput.value.trim();
  const top_k = Number(topKInput.value || 6);
  const source_filter = getSourceFilterValue();

  if (!question) return;

  try {
    setLoading(true);

    const response = await fetch("/retrieve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k, source_filter }),
    });

    const data = await response.json();

    if (!response.ok) {
      addMessage(data.detail || "Retrieve sırasında hata oluştu.", "bot");
      return;
    }

    addMessage(
      "Retrieve tamamlandı. En alakalı kaynak parçalar aşağıda gösterildi.",
      "bot",
      `Toplam sonuç: ${data.total_results} | Filtre: ${source_filter || "Tüm Belgeler"}`
    );

    renderSources(data.results);
  } catch (error) {
    addMessage("Retrieve isteği sırasında beklenmeyen bir hata oluştu.", "bot");
  } finally {
    setLoading(false);
  }
});

resetBtn.addEventListener("click", async () => {
  try {
    setLoading(true);

    const response = await fetch("/reset", {
      method: "POST",
    });

    const data = await response.json();

    if (!response.ok) {
      addMessage(data.detail || "Reset işlemi başarısız oldu.", "bot");
      return;
    }

    lastBotAnswer = "";
    addMessage("Tüm indeks sıfırlandı. Yeni belgeler yükleyebilirsiniz.", "bot");
    uploadStatus.textContent = "İndeks temizlendi.";
    renderSources([]);
    renderMetaPanel(0, [], 0, []);
    await fetchDocuments();
  } catch (error) {
    addMessage("Reset işlemi sırasında beklenmeyen bir hata oluştu.", "bot");
  } finally {
    setLoading(false);
  }
});

copyLastAnswerBtn.addEventListener("click", async () => {
  if (!lastBotAnswer) {
    addMessage("Kopyalanacak bir bot cevabı bulunmuyor.", "bot");
    return;
  }

  try {
    await navigator.clipboard.writeText(lastBotAnswer);
    addMessage("Son bot cevabı panoya kopyalandı.", "bot");
  } catch (error) {
    addMessage("Kopyalama sırasında bir hata oluştu.", "bot");
  }
});

refreshDocsBtn.addEventListener("click", async () => {
  await fetchDocuments();
  addMessage("Belge listesi yenilendi.", "bot");
});

deleteSelectedDocBtn.addEventListener("click", async () => {
  const sourceName = getSourceFilterValue();

  if (!sourceName) {
    addMessage("Silmek için önce bir belge seçmelisiniz.", "bot");
    return;
  }

  try {
    setLoading(true);

    const response = await fetch(`/documents/${encodeURIComponent(sourceName)}`, {
      method: "DELETE",
    });

    const data = await response.json();

    if (!response.ok) {
      addMessage(data.detail || "Belge silinirken hata oluştu.", "bot");
      return;
    }

    addMessage(`${sourceName} kaynağı silindi.`, "bot");
    sourceFilterSelect.value = "";
    await fetchDocuments();
  } catch (error) {
    addMessage("Belge silme sırasında beklenmeyen bir hata oluştu.", "bot");
  } finally {
    setLoading(false);
  }
});

fetchDocuments();