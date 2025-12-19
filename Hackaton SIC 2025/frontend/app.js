const chatLog = document.getElementById("chatLog");
const chatForm = document.getElementById("chatForm");
const userQuestion = document.getElementById("userQuestion");
const strictMode = document.getElementById("strictMode");
const citationsToggle = document.getElementById("citations");
const resetButton = document.getElementById("resetChat");
const quickPrompts = document.querySelectorAll("[data-prompt]");
const drawerButtons = document.querySelectorAll("[data-open-drawer]");
const drawerOverlay = document.querySelector(".drawer-overlay");
const drawers = {
  info: document.getElementById("drawer-info"),
  menu: document.getElementById("drawer-menu"),
};

// Config: usa backend local por defecto o define window.LEGALBOT_API_URL en producción.
// Ejemplo en consola: window.LEGALBOT_API_URL = "http://localhost:8000/api/chat";
const DEFAULT_API_URL = "http://localhost:8000/api/chat";
const API_URL = window.LEGALBOT_API_URL || DEFAULT_API_URL;

const knowledgeBase = [
  {
    id: "codigo_trabajo",
    name: "Código de Trabajo",
    article: "Art. 213 - Licencias y fuero",
    keywords: ["trabajo", "laboral", "empleador", "empleado", "licencia", "fuero", "despido"],
    summary:
      "El empleador debe respetar licencias por maternidad/paternidad, garantizar condiciones dignas y no afectar el fuero de maternidad sin autorización judicial.",
  },
  {
    id: "codigo_familia",
    name: "Código de la Familia",
    article: "Art. 256-260 - Adopción y tutela",
    keywords: ["familia", "adopcion", "adopción", "matrimonio", "guarda", "menor"],
    summary:
      "Define requisitos de idoneidad, consentimiento del menor cuando aplique y control judicial para formalizar adopciones y tutelas.",
  },
  {
    id: "codigo_penal",
    name: "Código Penal",
    article: "Art. 214 - Hurto",
    keywords: ["penal", "delito", "hurto", "robo", "pena", "sancion", "sanción"],
    summary:
      "El hurto simple se sanciona con pena de prisión graduada según el monto. Circunstancias agravantes elevan la pena.",
  },
  {
    id: "codigo_civil",
    name: "Código Civil",
    article: "Art. 1644 - Responsabilidad",
    keywords: ["civil", "contrato", "responsabilidad", "obligacion", "obligación", "daños", "perjuicios"],
    summary:
      "Regula la obligación de reparar daños causados por dolo o culpa, con énfasis en restitución e indemnización.",
  },
];

function renderMessage(role, text, { citations = [] } = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = text.replace(/\n/g, "<br>");

  if (citations.length) {
    const sourceWrap = document.createElement("div");
    sourceWrap.className = "sources";
    citations.forEach((c) => {
      const pill = document.createElement("span");
      pill.className = "pill neutral";
      pill.textContent = `${c.code} • ${c.article} • ${c.document}`;
      sourceWrap.appendChild(pill);
    });
    bubble.appendChild(sourceWrap);
  }

  wrapper.appendChild(bubble);
  chatLog.appendChild(wrapper);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function showLoading() {
  const wrapper = document.createElement("div");
  wrapper.className = "message assistant";
  const bubble = document.createElement("div");
  bubble.className = "bubble loading";
  bubble.innerHTML = `
    <div class="dots">
      <span></span><span></span><span></span>
    </div>
    <p>Buscando artículos relevantes y generando respuesta...</p>
  `;
  wrapper.appendChild(bubble);
  chatLog.appendChild(wrapper);
  chatLog.scrollTop = chatLog.scrollHeight;
  return wrapper;
}

function removeLoading(node) {
  if (node && node.parentNode === chatLog) {
    chatLog.removeChild(node);
  }
}

function detectContext(question) {
  const lower = question.toLowerCase();
  return knowledgeBase.find((item) => item.keywords.some((k) => lower.includes(k)));
}

async function callBackend(question) {
  if (!API_URL) return null;

  const payload = {
    question,
    strict: strictMode.checked,
    citations: citationsToggle.checked,
  };

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    return await res.json();
  } catch (err) {
    console.error("No se pudo contactar el backend:", err);
    return { error: "No se pudo contactar el backend. Se usará la respuesta simulada." };
  }
}

function buildMockAnswer(question) {
  const match = detectContext(question);
  const baseCitations = match
    ? [
        {
          code: match.name,
          article: match.article,
          document: `Dataset/JSON/${match.id}.json`,
        },
      ]
    : [
        {
          code: "Constitución de Panamá",
          article: "Referencia general",
          document: "Dataset/Constitucion/constitucion_panama.pdf",
        },
      ];

  const strict = strictMode.checked;
  const withCitations = citationsToggle.checked ? baseCitations : [];

  if (match) {
    return {
      text: `Resumen rápido sobre ${match.name}:\n\n- ${match.summary}\n- La cita relevante: ${match.article}.\n\n${strict ? "Modo estricto: respuesta basada solo en el fragmento recuperado." : "Modo flexible: se permite resumir en lenguaje claro."}`,
      citations: withCitations,
    };
  }

  return {
    text: `No se encontró un fragmento directo para tu consulta, pero puedo indicarte que las respuestas siempre se limitan a los códigos cargados. Reformula con el código o artículo si lo conoces.\n\n${strict ? "Sin evidencia suficiente → devuelvo control al usuario." : "Activa Modo estricto para forzar solo evidencias."}`,
    citations: withCitations,
  };
}

function resetChat() {
  chatLog.innerHTML = "";
  renderMessage("assistant", "Hola, soy LegalBot Panamá. Pregunta sobre un artículo específico o describe tu caso y te devolveré una respuesta breve con la cita legal correspondiente.", {
    citations: [{ code: "Dataset RAG SIC 2025", article: "Embeddings FAISS", document: "Dataset/FAISS/*" }],
  });
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const question = userQuestion.value.trim();
  if (!question) return;

  renderMessage("user", question);
  userQuestion.value = "";

  const loadingNode = showLoading();

  setTimeout(async () => {
    const backendResponse = await callBackend(question);
    let text = "";
    let citations = [];

    if (backendResponse && !backendResponse.error) {
      text = backendResponse.answer || backendResponse.text || "Respuesta recibida.";
      citations = backendResponse.sources || backendResponse.citations || [];
    } else {
      const mock = buildMockAnswer(question);
      text = backendResponse?.error ? `${backendResponse.error}\n\n${mock.text}` : mock.text;
      citations = mock.citations;
    }

    removeLoading(loadingNode);
    renderMessage("assistant", text, { citations });
  }, 650 + Math.random() * 450);
});

resetButton.addEventListener("click", resetChat);

quickPrompts.forEach((btn) => {
  btn.addEventListener("click", () => {
    const prompt = btn.getAttribute("data-prompt");
    userQuestion.value = prompt;
    userQuestion.focus();
  });
});

function openDrawer(name) {
  const drawer = drawers[name];
  if (!drawer) return;
  drawer.classList.add("open");
  drawerOverlay.classList.add("visible");
}

function closeDrawers() {
  Object.values(drawers).forEach((d) => d.classList.remove("open"));
  drawerOverlay.classList.remove("visible");
}

drawerButtons.forEach((btn) => {
  btn.addEventListener("click", () => openDrawer(btn.dataset.openDrawer));
});

drawerOverlay.addEventListener("click", closeDrawers);
document.querySelectorAll("[data-close-drawer]").forEach((el) => el.addEventListener("click", closeDrawers));

resetChat();
