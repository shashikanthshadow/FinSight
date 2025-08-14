const expensesDiv = document.getElementById("expenses");
const addRowBtn = document.getElementById("addRow");
const analyzeBtn = document.getElementById("analyzeBtn");
const adviceEl = document.getElementById("advice");

let pieChart, barChart;

function makeRow(name = "", amount = "", category = "") {
  const row = document.createElement("div");
  row.className = "expense-row";
  row.innerHTML = `
    <input class="name" type="text" placeholder="Expense name (e.g., Rent)" value="${name}"/>
    <input class="amount" type="number" min="0" placeholder="Amount" value="${amount}"/>
    <select class="category">
       <option value="">Auto</option>
       <option>Housing</option><option>Utilities</option><option>Groceries</option>
       <option>Transport</option><option>Dining</option><option>Insurance</option>
       <option>Healthcare</option><option>Education</option><option>Entertainment</option>
       <option>Personal</option><option>Debt</option><option>Misc</option>
    </select>
    <button class="btn remove">✕</button>
  `;
  if (category) row.querySelector(".category").value = category;
  row.querySelector(".remove").onclick = () => row.remove();
  expensesDiv.appendChild(row);
}

addRowBtn.onclick = () => makeRow();

// Seed a couple rows to demo
makeRow("Rent", 15000, "Housing");
makeRow("Groceries", 6000, "Groceries");
makeRow("Internet", 1000, "Utilities");
makeRow("Dining out", 1500, "Dining");

function collectData() {
  const income = parseFloat(document.getElementById("income").value || "0");
  const rows = [...document.querySelectorAll(".expense-row")];
  const expenses = rows.map(r => ({
    name: r.querySelector(".name").value || "Unnamed",
    amount: parseFloat(r.querySelector(".amount").value || "0"),
    category: r.querySelector(".category").value || null
  }));
  return { income, expenses };
}

async function analyze() {
  adviceEl.textContent = "Crunching numbers and fetching live market data...";
  const payload = collectData();
  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    
    // Check for advice content and display it
    if (data.advice) {
        // Use an external library to render markdown
        adviceEl.innerHTML = marked.parse(data.advice);
    } else {
        adviceEl.textContent = "No advice returned.";
    }

    // Charts
    drawPie(data.categories);
    drawBar(data.summary);
  } catch (e) {
    adviceEl.textContent = "Error: " + e.message;
  }
}

function drawPie(categories) {
  const ctx = document.getElementById("pieChart").getContext("2d");
  const labels = Object.keys(categories);
  const values = Object.values(categories);

  if (pieChart) pieChart.destroy();
  pieChart = new Chart(ctx, {
    type: "pie",
    data: {
      labels,
      datasets: [{ data: values }]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: "bottom" } }
    }
  });
}

function drawBar(summary) {
  const ctx = document.getElementById("barChart").getContext("2d");
  const labels = ["Income", "Needs (curr)", "Wants (curr)", "Suggested Savings"];
  const values = [
    summary.income,
    summary.needs_current,
    summary.wants_current,
    summary.suggested_savings
  ];

  if (barChart) barChart.destroy();
  barChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{ data: values }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });
}

analyzeBtn.onclick = analyze;
