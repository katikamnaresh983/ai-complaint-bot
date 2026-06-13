const complaintsBody = document.querySelector("#complaints");
const categoriesEl = document.querySelector("#categories");
const replyEl = document.querySelector("#reply");
const form = document.querySelector("#whatsapp-form");
const refreshButton = document.querySelector("#refresh");

const priorityClass = {
  Urgent: "urgent",
  High: "high",
  Medium: "normal",
  Low: "normal",
};

async function loadDashboard() {
  const [statsResponse, complaintsResponse] = await Promise.all([
    fetch("/dashboard/stats"),
    fetch("/complaints/"),
  ]);
  const stats = await statsResponse.json();
  const complaints = await complaintsResponse.json();

  document.querySelector("#metric-total").textContent = stats.total;
  document.querySelector("#metric-open").textContent = stats.open;
  document.querySelector("#metric-progress").textContent = stats.in_progress;
  document.querySelector("#metric-urgent").textContent = stats.urgent;

  renderComplaints(complaints);
  renderCategories(stats.categories, stats.total);
}

function renderComplaints(complaints) {
  complaintsBody.innerHTML = "";

  if (!complaints.length) {
    complaintsBody.innerHTML = '<tr><td colspan="6">No complaints yet.</td></tr>';
    return;
  }

  for (const complaint of complaints.slice(0, 12)) {
    const row = document.createElement("tr");
    const badgeClass = priorityClass[complaint.priority] || "normal";
    row.innerHTML = `
      <td>#${complaint.id}</td>
      <td>${escapeHtml(complaint.resident_name)}</td>
      <td>${escapeHtml(complaint.category)}</td>
      <td><span class="badge ${badgeClass}">${escapeHtml(complaint.priority)}</span></td>
      <td>${escapeHtml(complaint.status)}</td>
      <td>${escapeHtml(complaint.summary)}</td>
    `;
    complaintsBody.appendChild(row);
  }
}

function renderCategories(categories, total) {
  categoriesEl.innerHTML = "";
  const entries = Object.entries(categories).sort((a, b) => b[1] - a[1]);

  if (!entries.length) {
    categoriesEl.textContent = "No categories yet.";
    return;
  }

  for (const [category, count] of entries) {
    const percentage = total ? Math.round((count / total) * 100) : 0;
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <div class="bar-label">
        <span>${escapeHtml(category)}</span>
        <span>${count}</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width: ${percentage}%"></div>
      </div>
    `;
    categoriesEl.appendChild(row);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form));

  const response = await fetch("/whatsapp/demo", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const result = await response.json();

  replyEl.hidden = false;
  replyEl.textContent = result.reply;
  await loadDashboard();
});

refreshButton.addEventListener("click", loadDashboard);

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

loadDashboard();
