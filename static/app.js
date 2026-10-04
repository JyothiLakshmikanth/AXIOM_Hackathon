/**
 * AXIOM Interactive Frontend Client
 * Connects to FastAPI LangGraph orchestrator endpoints,
 * renders visual-first Imagen/Mermaid outputs, and handles intent clarification pills.
 */

document.addEventListener("DOMContentLoaded", () => {
  fetchKgStats();
  if (window.mermaid) {
    mermaid.initialize({ startOnLoad: false, theme: 'dark' });
  }
});

async function fetchKgStats() {
  try {
    const res = await fetch("/api/kg/stats");
    if (res.ok) {
      const data = await res.json();
      const badge = document.getElementById("kg-stat-text");
      if (badge) {
        badge.innerText = `Neo4j KG: ${data.total_nodes} Nodes | ${data.total_edges} Edges`;
      }
    }
  } catch (e) {
    console.debug("KG stats fetch failed:", e);
  }
}

function submitPrompt(text) {
  const input = document.getElementById("user-input");
  if (input) {
    input.value = text;
    handleFormSubmit(new Event("submit"));
  }
}

async function handleFormSubmit(event) {
  if (event) event.preventDefault();
  
  const input = document.getElementById("user-input");
  const query = input.value.trim();
  if (!query) return;

  // Clear input
  input.value = "";

  // Hide welcome hero on first message
  const hero = document.getElementById("welcome-hero");
  if (hero) hero.style.display = "none";

  const chatHistory = document.getElementById("chat-history");

  // 1. Render User Message
  appendUserMessage(query);

  // 2. Render Loading State
  const loadingRow = appendLoadingIndicator();
  chatHistory.scrollTop = chatHistory.scrollHeight;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query })
    });

    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }

    const data = await response.json();
    loadingRow.remove();

    // Update active master badge in header
    updateMasterBadge(data.target_master, data.target_capability);

    // 3. Render Agent Response
    appendAgentResponse(data);

  } catch (error) {
    loadingRow.remove();
    appendErrorMessage(`Failed to communicate with AXIOM Master: ${error.message}`);
  }

  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function updateMasterBadge(master, capability) {
  const badgeVal = document.getElementById("current-master-val");
  if (badgeVal) {
    if (master) {
      badgeVal.innerText = `${master} (${capability || 'Active'})`;
    } else {
      badgeVal.innerText = "Router (Awaiting Intent)";
    }
  }
}

function appendUserMessage(text) {
  const chatHistory = document.getElementById("chat-history");
  const row = document.createElement("div");
  row.className = "message-row user";
  row.innerHTML = `
    <div class="message-bubble">${escapeHtml(text)}</div>
    <div class="avatar user-avatar">U</div>
  `;
  chatHistory.appendChild(row);
}

function appendLoadingIndicator() {
  const chatHistory = document.getElementById("chat-history");
  const row = document.createElement("div");
  row.className = "message-row agent";
  row.id = "loading-row";
  row.innerHTML = `
    <div class="avatar master-avatar">⚙</div>
    <div class="message-bubble">
      <div style="display:flex; align-items:center; gap:10px; color:var(--text-muted); font-size:13px;">
        <span class="status-dot green" style="animation: pulse-glow 1s infinite alternate;"></span>
        <span>AXIOM Orchestrator reasoning through LangGraph master state...</span>
      </div>
    </div>
  `;
  chatHistory.appendChild(row);
  return row;
}

function appendErrorMessage(text) {
  const chatHistory = document.getElementById("chat-history");
  const row = document.createElement("div");
  row.className = "message-row agent";
  row.innerHTML = `
    <div class="avatar master-avatar" style="background:#ef4444;">!</div>
    <div class="message-bubble" style="border-color:#ef4444; color:#fca5a5;">
      ${escapeHtml(text)}
    </div>
  `;
  chatHistory.appendChild(row);
}

function appendAgentResponse(data) {
  const chatHistory = document.getElementById("chat-history");
  const row = document.createElement("div");
  row.className = "message-row agent";

  const masterName = data.target_master || "AXIOM Router";
  const capability = data.target_capability ? ` • ${data.target_capability}` : "";
  const confidence = data.confidence_score ? `Confidence: ${(data.confidence_score * 100).toFixed(0)}%` : "";

  // Parse markdown
  let renderedMarkdown = "";
  if (data.final_output_markdown && window.marked) {
    renderedMarkdown = marked.parse(data.final_output_markdown);
  } else {
    renderedMarkdown = `<p>${data.final_output_markdown || "Execution complete."}</p>`;
  }

  // Visual Asset Card (Visual-First)
  let visualCardHtml = "";
  const visual = data.visual_artifact || {};
  if (visual.requires_visual) {
    const caption = visual.structured_caption || "Visual-first synthesized analysis";
    const imgUrl = visual.image_url || "";
    const mermaidCode = visual.fallback_mermaid || "";

    visualCardHtml = `
      <div class="visual-asset-card">
        <div class="visual-header">
          <span>🎨 Visual-First Presentation: ${visual.visual_type || "System Diagram"}</span>
          <span style="font-size:10px; color:var(--text-dim);">${visual.image_model || "Imagen 2"}</span>
        </div>
        <div class="visual-body">
          ${mermaidCode ? `<div class="mermaid">${mermaidCode}</div>` : `<img src="${imgUrl}" alt="${caption}" style="max-width:100%; border-radius:8px;" onerror="this.style.display='none'">`}
        </div>
        <div class="visual-caption">🔍 ${caption}</div>
      </div>
    `;
  }

  // Clarification Pills
  let clarificationHtml = "";
  const clarification = data.clarification || {};
  if (clarification.clarification_needed && clarification.clarification_questions) {
    clarificationHtml = `
      <div class="clarification-pills-box">
        <div style="font-size:11px; font-weight:600; text-transform:uppercase; color:#fb7185;">Suggested clarifications (Click to select):</div>
        ${clarification.clarification_questions.map(q => `
          <button class="clarification-pill" onclick="submitPrompt('${escapeAttr(q)}')">
            ➔ ${escapeHtml(q)}
          </button>
        `).join("")}
      </div>
    `;
  }

  // Evidence Drawer
  let evidenceDrawerHtml = "";
  const envelopes = data.evidence_envelopes || [];
  if (envelopes.length > 0) {
    const envItems = envelopes.map(env => `
      <div class="evidence-item">
        <div>
          <strong>${escapeHtml(env.artifact_id || "RECORD")}</strong>
          <span style="color:var(--text-dim); font-size:10px; margin-left:6px;">(${env.artifact_type || "evidence"})</span>
        </div>
        <span class="env-tag ${env.source_system}">${env.source_system}</span>
      </div>
    `).join("");

    evidenceDrawerHtml = `
      <div class="evidence-drawer">
        <div class="evidence-drawer-header" onclick="toggleEvidenceDrawer(this)">
          <span>📋 Grounded Evidence Envelopes (${envelopes.length})</span>
          <span class="toggle-icon">▼</span>
        </div>
        <div class="evidence-list" style="display:none;">
          ${envItems}
        </div>
      </div>
    `;
  }

  row.innerHTML = `
    <div class="avatar master-avatar">⬡</div>
    <div class="message-bubble">
      <div class="meta-header">
        <div class="meta-agent-tag">
          <span>${masterName}${capability}</span>
        </div>
        ${confidence ? `<span class="confidence-pill">${confidence}</span>` : ""}
      </div>
      
      <div class="markdown-body">
        ${renderedMarkdown}
      </div>

      ${visualCardHtml}
      ${clarificationHtml}
      ${evidenceDrawerHtml}
    </div>
  `;

  chatHistory.appendChild(row);

  // Render any dynamic Mermaid diagrams in this row
  if (window.mermaid) {
    mermaid.run({ nodes: row.querySelectorAll(".mermaid") });
  }
}

function toggleEvidenceDrawer(headerElem) {
  const list = headerElem.nextElementSibling;
  const icon = headerElem.querySelector(".toggle-icon");
  if (list.style.display === "none") {
    list.style.display = "flex";
    if (icon) icon.innerText = "▲";
  } else {
    list.style.display = "none";
    if (icon) icon.innerText = "▼";
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function escapeAttr(str) {
  if (!str) return "";
  return str.replace(/'/g, "\\'").replace(/"/g, "&quot;");
}
