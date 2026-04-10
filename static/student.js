console.log("Student JS Loaded");

const token = localStorage.getItem("token");

if (!token) {
    alert("Login first!");
    window.location.href = "/login";
}

// ─── Section Switcher ─────────────────────────
function showSection(sectionId) {
    const sections = [
        "jobsSection", "applicationsSection",
        "interviewsSection", "placementsSection", "profileSection"
    ];
    sections.forEach(id => {
        document.getElementById(id).style.display = "none";
    });
    document.getElementById(sectionId).style.display = "block";

    // Update topbar title
    const titles = {
        jobsSection: "Browse Jobs",
        applicationsSection: "My Applications",
        interviewsSection: "Scheduled Interviews",
        placementsSection: "My Placements",
        profileSection: "My Profile"
    };
    const titleEl = document.getElementById("topbar-title");
    if (titleEl) titleEl.textContent = titles[sectionId] || "Dashboard";
}

function setActive(navId) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const el = document.getElementById(navId);
    if (el) el.classList.add('active');
}

// ─── Load Jobs ────────────────────────────────
function loadJobs() {
    fetch('/student/jobs', {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => renderJobs(data));
}

function renderJobs(data) {
    const el = document.getElementById("jobs");
    if (!data || !data.length) {
        el.innerHTML = `<div class="empty-state"><div class="empty-icon">💼</div><p>No jobs available right now</p></div>`;
        return;
    }

    el.innerHTML = data.map((j, i) => {
        const skills = (j.skills || '').split(',').map(s => s.trim()).filter(Boolean);
        return `
        <div class="job-card" style="animation-delay:${i * 0.05}s">
            <div class="job-card-header">
                <div>
                    <div class="job-card-title">${j.title}</div>
                    <div class="job-card-meta">
                        <span>🏢 ${j.company}</span>
                        <span>💰 ₹${Number(j.salary).toLocaleString('en-IN')}</span>
                    </div>
                </div>
            </div>
            <div class="skills-tags">
                ${skills.map(s => `<span class="skill-tag">${s}</span>`).join('') || '<span class="skill-tag">General</span>'}
            </div>
            <button class="btn btn-primary btn-sm" onclick="applyJob(${j.id})">Apply Now →</button>
        </div>`;
    }).join('');
}

// ─── Update Profile ───────────────────────────
function updateProfile() {
    const data = {
        branch:          document.getElementById("branch").value,
        cgpa:            document.getElementById("cgpa").value,
        graduation_year: document.getElementById("year").value,
        skills:          document.getElementById("skillsInput").value,
        resume_link:     document.getElementById("resume").value
    };

    fetch('/student/profile', {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => alert(data.msg || data.error));
}

// ─── Load Profile (pre-fill) ──────────────────
function loadProfile() {
    // Optional: pre-fill if endpoint exists
}

// ─── Search Jobs ──────────────────────────────
function searchJobs() {
    const search = document.getElementById("search").value.trim();
    let url = "/student/jobs";
    if (search !== "") url += `?search=${encodeURIComponent(search)}`;

    fetch(url, { headers: { "Authorization": "Bearer " + token } })
    .then(res => res.json())
    .then(data => renderJobs(data));
}

// ─── Apply Job ────────────────────────────────
function applyJob(id) {
    fetch(`/student/apply/${id}`, {
        method: "POST",
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => alert(data.msg || data.error));
}

// ─── Load Applications ────────────────────────
function loadApplications() {
    fetch('/student/applications', {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => {
        const el = document.getElementById("applications");
        if (!data || !data.length) {
            el.innerHTML = `<div class="empty-state"><div class="empty-icon">📋</div><p>No applications yet</p></div>`;
            return;
        }

        el.innerHTML = data.map((a, i) => {
            const statusClass = {
                selected: 'badge-success', shortlisted: 'badge-warning',
                rejected: 'badge-danger',  pending: 'badge-muted',
                approved: 'badge-success'
            }[a.status] || 'badge-muted';

            return `
            <div class="app-timeline-item" style="animation-delay:${i*0.05}s">
                <div class="app-top">
                    <div>
                        <div class="app-job-title">${a.job_title}</div>
                        <div class="app-company">🏢 ${a.company}</div>
                    </div>
                    <span class="badge ${statusClass}">${a.status}</span>
                </div>
                <div class="app-details">
                    <div class="app-detail-item">
                        <div class="app-detail-label">Applied On</div>
                        <div class="app-detail-val">${a.applied_date || '—'}</div>
                    </div>
                    <div class="app-detail-item">
                        <div class="app-detail-label">Interview</div>
                        <div class="app-detail-val">${a.interview_date || 'Not scheduled'}</div>
                    </div>
                    <div class="app-detail-item">
                        <div class="app-detail-label">Location</div>
                        <div class="app-detail-val">${a.interview_location || '—'}</div>
                    </div>
                    <div class="app-detail-item">
                        <div class="app-detail-label">Feedback</div>
                        <div class="app-detail-val">${a.feedback || '—'}</div>
                    </div>
                </div>
            </div>`;
        }).join('');
    });
}

// ─── Load Interviews ──────────────────────────
function loadInterviews() {
    fetch('/student/interviews', {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => {
        const el = document.getElementById("interviews");
        if (!data || !data.length) {
            el.innerHTML = `<div class="empty-state"><div class="empty-icon">📅</div><p>No interviews scheduled</p></div>`;
            return;
        }

        el.innerHTML = data.map((i, idx) => `
            <div class="interview-card" style="animation-delay:${idx*0.05}s">
                <div style="font-family:var(--font-heading); font-size:16px; font-weight:700; margin-bottom:8px">
                    ${i.job}
                </div>
                <div style="color:var(--text-secondary); font-size:13.5px; margin-bottom:12px">🏢 ${i.company}</div>
                <div style="display:flex; gap:24px; flex-wrap:wrap;">
                    <div><div style="font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700">Date</div>
                         <div style="font-size:14px; margin-top:3px">${i.date}</div></div>
                    <div><div style="font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); font-weight:700">Location</div>
                         <div style="font-size:14px; margin-top:3px">${i.location}</div></div>
                </div>
            </div>`).join('');
    });
}

// ─── Load Placements ──────────────────────────
function loadPlacements() {
    const token = localStorage.getItem("token");

    fetch('/student/placements', {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => {
        const el = document.getElementById("placements");
        if (!data || data.length === 0) {
            el.innerHTML = `<div class="empty-state"><div class="empty-icon">🏆</div><p>No placements yet — keep applying!</p></div>`;
            return;
        }

        el.innerHTML = data.map((p, i) => `
            <div class="placement-card" style="animation-delay:${i*0.05}s">
                <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px; flex-wrap:wrap;">
                    <div>
                        <div class="placement-company">🎉 ${p.job_title}</div>
                        <div class="placement-meta">🏢 ${p.company}</div>
                        <div style="display:flex; gap:20px; flex-wrap:wrap; font-size:13.5px; color:var(--text-secondary)">
                            <span>💰 ₹${p.salary ? Number(p.salary).toLocaleString('en-IN') : 'Negotiable'}</span>
                            <span>📅 Joining: ${p.joining_date || 'TBA'}</span>
                        </div>
                    </div>
                    <button class="btn btn-success btn-sm" onclick="downloadOffer(${p.application_id})">
                        📄 Download Offer
                    </button>
                </div>
            </div>`).join('');
    })
    .catch(err => {
        console.error("Error loading placements:", err);
        document.getElementById("placements").innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><p>Error loading placement data</p></div>`;
    });
}

// ─── Download Offer Letter ────────────────────
function downloadOffer(id) {
    const token = localStorage.getItem("token");

    fetch(`/student/application/${id}/download`, {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(async res => {
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.error || "Download failed");
        }
        return res.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a   = document.createElement("a");
        a.href     = url;
        a.download = `Offer_Letter_${id}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    })
    .catch(err => alert(err.message));
}

// =======================
// EXPORT CSV (STUDENT)
// =======================
window.exportCSV = function () {
    fetch('/student/export', {
        method: 'GET',
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("exportStatus").innerText =
            "⏳ Export started...";

        checkExportStatus(data.task_id);
    })
    .catch(err => console.error("Export error:", err));
};


// =======================
// CHECK STATUS
// =======================
function checkExportStatus(taskId) {
    const interval = setInterval(() => {
        fetch(`/task/${taskId}`)
        .then(res => res.json())
        .then(data => {

            if (data.status === "done") {
                clearInterval(interval);

                document.getElementById("exportStatus").innerHTML =
                    `✅ Export Ready! <br>
                     <a href="/${data.file}" target="_blank" class="btn btn-secondary btn-sm">
                        📥 Download CSV
                     </a>`;

                alert("✅ Your CSV export is ready!");
            } 
            else {
                document.getElementById("exportStatus").innerText =
                    "⏳ Processing... " + data.status;
            }

        })
        .catch(err => console.error("Status error:", err));
    }, 2000);
}


// ─── Auto Load ────────────────────────────────
window.onload = function () {
    showSection('jobsSection');
    loadJobs();
};
