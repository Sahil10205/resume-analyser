<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>AI Resume Analyzer Pro</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {
    margin: 0;
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1c1c1c);
    background-size: 400% 400%;
    animation: gradientBG 10s ease infinite;
    color: white;
}
@keyframes gradientBG {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}
h1 { text-align: center; }
.container { padding: 20px; }
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 20px;
}
.glass {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(15px);
    padding: 20px;
    border-radius: 15px;
}
textarea { width: 100%; height: 120px; }
button {
    width: 100%;
    padding: 12px;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    border: none;
    color: white;
    cursor: pointer;
    border-radius: 8px;
}
.progress-bar { background: rgba(255,255,255,0.2); }
.progress {
    height: 25px;
    width: 0%;
    text-align: center;
    font-weight: bold;
}
.loader { display:none; text-align:center; }
.toggle { display:flex; gap:10px; }
</style>
</head>

<body>

<h1>🚀 AI Resume Analyzer Pro</h1>

<div class="container">

<div class="grid">

<div class="glass">
<form id="form">
<div class="toggle">
    <label><input type="radio" name="mode" value="fast" checked> ⚡ Fast</label>
    <label><input type="radio" name="mode" value="ai"> 🧠 AI</label>
</div>

<br>

<input type="file" id="resume" required><br><br>
<textarea id="job" placeholder="Paste Job Description"></textarea><br><br>

<button type="submit" id="analyzeBtn">Analyze Resume</button>
</form>
</div>

<div class="glass">
<h3>ATS Score</h3>
<div class="progress-bar">
<div class="progress" id="progress"></div>
</div>
<h4 id="aiScore"></h4>
</div>

<div class="glass"><h3>Matched Skills</h3><ul id="matched"></ul></div>
<div class="glass"><h3>Missing Keywords</h3><ul id="keywords"></ul></div>
<div class="glass"><h3>Suggestions</h3><ul id="suggestions"></ul></div>
<div class="glass"><h3>🤖 AI Improvements</h3><ul id="improvements"></ul></div>

<div class="glass">
<h3>📊 Breakdown</h3>
<canvas id="chart"></canvas>
</div>

<div class="glass">
<h3>🕓 History</h3>
<ul id="history"></ul>
</div>

<div class="glass">
<button onclick="downloadReport()">📥 Download Report</button>
</div>

</div>

<div class="loader" id="loader">⏳ Analyzing Resume...</div>

</div>

<script>
let lastData = null;

// HISTORY
function saveHistory(score, aiScore) {
    let history = JSON.parse(localStorage.getItem("history")) || [];
    history.push({ ats: score, ai: aiScore, time: new Date().toLocaleString() });
    localStorage.setItem("history", JSON.stringify(history));
    loadHistory();
}
function loadHistory() {
    let history = JSON.parse(localStorage.getItem("history")) || [];
    document.getElementById("history").innerHTML =
        history.map(h => `<li>${h.ats}% | ${h.ai}% (${h.time})</li>`).join("");
}
loadHistory();

// COLOR
function getColor(score){
    if(score>75) return "lime";
    if(score>50) return "orange";
    return "red";
}

// FORM
document.getElementById("form").onsubmit = async (e)=>{
e.preventDefault();

let btn=document.getElementById("analyzeBtn");
btn.disabled=true;
btn.innerText="Analyzing...";
document.getElementById("loader").style.display="block";

let file=document.getElementById("resume").files[0];
let job=document.getElementById("job").value;
let mode=document.querySelector('input[name="mode"]:checked').value;

let formData=new FormData();
formData.append("resume",file);
formData.append("job_desc",job);
formData.append("mode",mode);

let res=await fetch("https://resume-analyser-production-93d7.up.railway.app/analyze",{
method:"POST",
body:formData
});

let data=await res.json();
lastData=data;

// SCORE
let score=data["ATS Score"];
let ai=data["AI Score"];

let bar=document.getElementById("progress");
bar.style.width=score+"%";
bar.style.background=getColor(score);
bar.innerText=score+"%";

document.getElementById("aiScore").innerText =
(ai==="Not Available") ? "🧠 AI: Not Available" : "🧠 AI: "+ai+"%";

// DATA RENDER FIXES
document.getElementById("matched").innerHTML =
(data["Matched Skills"] || []).map(s => `<li>${s}</li>`).join("");

document.getElementById("keywords").innerHTML =
(data["Missing Keywords"] || []).map(s => `<li>${s}</li>`).join("");

document.getElementById("suggestions").innerHTML =
(data["Suggestions"] || []).map(s => `<li>${s}</li>`).join("");

// AI improvements fallback
if (ai === "Not Available") {
  document.getElementById("improvements").innerHTML =
  "<li>AI quota exceeded. Showing basic analysis.</li>";
} else {
  document.getElementById("improvements").innerHTML =
  (data["AI Improvements"] || []).map(s=>`<li>${s}</li>`).join("");
}

// CHART FIX
new Chart(document.getElementById("chart"),{
type:"bar",
data:{
labels:["AI","TF-IDF","Keywords","Sections"],
datasets:[{
data:[
data.Breakdown["AI Semantic"],
data.Breakdown["TF-IDF"],
data.Breakdown.Keywords,
data.Breakdown.Sections
]
}]
}
});

saveHistory(score,ai);

document.getElementById("loader").style.display="none";
btn.disabled=false;
btn.innerText="Analyze Resume";
};

// DOWNLOAD
function downloadReport(){
    if(!lastData) return alert("Run analysis first!");
    let text=JSON.stringify(lastData,null,2);
    let blob=new Blob([text],{type:"text/plain"});
    let a=document.createElement("a");
    a.href=URL.createObjectURL(blob);
    a.download="report.txt";
    a.click();
}
</script>

</body>
</html>
