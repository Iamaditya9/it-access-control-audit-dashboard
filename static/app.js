async function loadSummary() {
  const data = await fetch("/api/summary").then(r => r.json());
  document.getElementById("metrics").innerHTML = `
    <div class="metric"><span>Access Records</span><strong>${data.total_records}</strong></div>
    <div class="metric"><span>Open Findings</span><strong>${data.open_findings}</strong></div>
    <div class="metric risk"><span>High Risk</span><strong>${data.high_risk}</strong></div>
    <div class="metric"><span>Systems</span><strong>${data.systems}</strong></div>`;
}

async function loadFindings() {
  const data = await fetch("/api/findings").then(r => r.json());
  document.getElementById("findings").innerHTML = data.map(item => `
    <tr>
      <td>${item.control_name}</td>
      <td><span class="severity ${item.severity.toLowerCase()}">${item.severity}</span></td>
      <td>${item.finding}</td>
      <td>${item.recommendation}</td>
      <td><select onchange="updateFinding(${item.id}, this.value)">
        ${["Open","In Progress","Resolved"].map(s => `<option ${s === item.status ? "selected" : ""}>${s}</option>`).join("")}
      </select></td>
    </tr>`).join("");
}

async function updateFinding(id, status) {
  await fetch(`/api/findings/${id}`, {
    method: "PATCH",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({status})
  });
  loadSummary();
}

document.getElementById("upload").addEventListener("submit", async event => {
  event.preventDefault();
  const response = await fetch("/api/import", {method: "POST", body: new FormData(event.target)});
  const data = await response.json();
  document.getElementById("message").textContent = response.ok
    ? `Imported ${data.inserted} records and generated ${data.findings_generated} findings.`
    : data.error;
  loadSummary();
  loadFindings();
});

loadSummary();
loadFindings();
