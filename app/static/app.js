const pipelineForm = document.getElementById("pipeline-form");
const leadForm = document.getElementById("lead-form");
const cardForm = document.getElementById("card-form");
const settingsForm = document.getElementById("settings-form");

const leadsList = document.getElementById("leads-list");
const leadPipelineSelect = document.getElementById("lead-pipeline");
const settingsFeedback = document.getElementById("settings-feedback");

const kanbanColumns = {
  todo: document.getElementById("kanban-todo"),
  doing: document.getElementById("kanban-doing"),
  done: document.getElementById("kanban-done"),
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Erro na requisição");
  }

  return response.json();
}

function renderPipelines(pipelines) {
  leadPipelineSelect.innerHTML = "";
  for (const pipeline of pipelines) {
    const opt = document.createElement("option");
    opt.value = String(pipeline.id);
    opt.textContent = `${pipeline.name} (#${pipeline.id})`;
    leadPipelineSelect.appendChild(opt);
  }
}

function renderLeads(leads) {
  leadsList.innerHTML = "";
  for (const lead of leads) {
    const item = document.createElement("div");
    item.className = "item";
    item.textContent = `#${lead.id} - ${lead.title} | Pipeline ${lead.pipeline_id} | Etapa: ${lead.stage_name}`;
    leadsList.appendChild(item);
  }
}

function renderCards(cards) {
  Object.values(kanbanColumns).forEach((column) => (column.innerHTML = ""));

  for (const card of cards) {
    const item = document.createElement("div");
    item.className = "item";

    const title = document.createElement("strong");
    title.textContent = card.title;

    const select = document.createElement("select");
    ["todo", "doing", "done"].forEach((status) => {
      const option = document.createElement("option");
      option.value = status;
      option.textContent = status;
      option.selected = card.status === status;
      select.appendChild(option);
    });

    select.addEventListener("change", async (event) => {
      await api(`/kanban/cards/${card.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: event.target.value }),
      });
      await loadCards();
    });

    item.append(title, document.createElement("br"), select);
    kanbanColumns[card.status].appendChild(item);
  }
}

async function loadPipelines() {
  const data = await api("/smartflow/pipelines");
  renderPipelines(data);
}

async function loadLeads() {
  const data = await api("/smartflow/leads");
  renderLeads(data);
}

async function loadCards() {
  const data = await api("/kanban/cards");
  renderCards(data);
}

async function loadSettings() {
  const data = await api("/configuracoes");
  document.getElementById("company-name").value = data.company_name;
  document.getElementById("locale").value = data.locale;
  document.getElementById("timezone").value = data.timezone;
}

pipelineForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = document.getElementById("pipeline-name").value;
  const stages = document
    .getElementById("pipeline-stages")
    .value.split(",")
    .map((stage) => stage.trim())
    .filter(Boolean)
    .map((name) => ({ name }));

  await api("/smartflow/pipelines", {
    method: "POST",
    body: JSON.stringify({ name, stages }),
  });

  pipelineForm.reset();
  await loadPipelines();
});

leadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = document.getElementById("lead-title").value;
  const pipelineId = Number(leadPipelineSelect.value);

  await api("/smartflow/leads", {
    method: "POST",
    body: JSON.stringify({ title, pipeline_id: pipelineId }),
  });

  leadForm.reset();
  await loadLeads();
});

cardForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = document.getElementById("card-title").value;
  const status = document.getElementById("card-status").value;

  await api("/kanban/cards", {
    method: "POST",
    body: JSON.stringify({ title, status }),
  });

  cardForm.reset();
  await loadCards();
});

settingsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    company_name: document.getElementById("company-name").value,
    locale: document.getElementById("locale").value,
    timezone: document.getElementById("timezone").value,
  };

  await api("/configuracoes", {
    method: "PUT",
    body: JSON.stringify(payload),
  });

  settingsFeedback.textContent = "Configurações salvas com sucesso.";
});

(async function init() {
  await Promise.all([loadPipelines(), loadLeads(), loadCards(), loadSettings()]);
})();
