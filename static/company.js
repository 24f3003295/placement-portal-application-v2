// Check if JS is loaded
console.log("JS FILE LOADED");

// Get token
const token = localStorage.getItem("token");

// =======================
// LOAD DASHBOARD
// =======================
window.loadDashboard = function () {
    console.log("Loading dashboard...");

    fetch('/company/dashboard', {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => {
        console.log("Dashboard data:", data);

        // Jobs
        const jobsEl = document.getElementById("jobs");
        if (!data.jobs || data.jobs.length === 0) {
            jobsEl.innerHTML = `<div class="empty-state"><div class="empty-icon">💼</div><p>No jobs posted yet</p></div>`;
        } else {
            jobsEl.innerHTML = data.jobs.map(j => `
                <div class="job-card">
                    <div>
                        <div class="job-title-text">${j.title}</div>
                        <div class="job-meta">Job ID #${j.id}</div>
                    </div>
                    <div class="action-group">
                        <button class="btn btn-ghost btn-sm" onclick="toggleJob(${j.id})">Toggle</button>
                        <button class="btn btn-secondary btn-sm" onclick="viewApps(${j.id})">View Apps</button>
                    </div>
                </div>
            `).join('');
        }

        // Applications
        const appsEl = document.getElementById("applications");
        if (!data.applications || data.applications.length === 0) {
            appsEl.innerHTML = `<div class="empty-state"><div class="empty-icon">📋</div><p>No applications yet</p></div>`;
        } else {
            appsEl.innerHTML = data.applications.map(a => {
                const statusClass = {
                    selected: 'badge-success', shortlisted: 'badge-warning',
                    rejected: 'badge-danger', pending: 'badge-muted'
                }[a.status] || 'badge-muted';

                return `
                <div class="app-card">
                    <div class="app-header">
                        <div class="app-id">Application #${a.id}</div>
                        <span class="badge ${statusClass}">${a.status}</span>
                    </div>
                    <div style="font-size:13.5px; color:var(--text-secondary); margin-bottom:12px">
                        Student ID: <strong>#${a.student_id}</strong>
                    </div>
                    <div class="app-actions">
                        <button class="btn btn-secondary btn-sm" onclick="viewStudent(${a.student_id})">👤 Profile</button>
                        <button class="btn btn-secondary btn-sm" onclick="updateStatus(${a.id}, 'shortlisted')">Shortlist</button>
                        <button class="btn btn-success btn-sm"   onclick="updateStatus(${a.id}, 'selected')">Select</button>
                        <button class="btn btn-danger btn-sm"    onclick="updateStatus(${a.id}, 'rejected')">Reject</button>
                        <button class="btn btn-ghost btn-sm"     onclick="scheduleInterview(${a.id})">📅 Schedule</button>
                    </div>
                </div>`;
            }).join('');
        }
    })
    .catch(err => console.error("Dashboard error:", err));
};

// =======================
// VIEW STUDENT PROFILE
// =======================
window.viewStudent = function (id) {
    fetch(`/company/student/${id}`, {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) { alert(data.error); return; }

        document.getElementById("studentDetails").innerHTML = `
            <div class="student-detail-card">
                <h4>👤 Student Profile</h4>
                <div class="detail-row"><span class="detail-key">Name</span><span class="detail-val">${data.name}</span></div>
                <div class="detail-row"><span class="detail-key">Email</span><span class="detail-val">${data.email}</span></div>
                <div class="detail-row"><span class="detail-key">Branch</span><span class="detail-val">${data.branch || '—'}</span></div>
                <div class="detail-row"><span class="detail-key">CGPA</span><span class="detail-val">${data.cgpa || '—'}</span></div>
                <div class="detail-row"><span class="detail-key">Skills</span><span class="detail-val">${data.skills || '—'}</span></div>
                <div class="detail-row"><span class="detail-key">Resume</span><span class="detail-val">
                    <a href="${data.resume}" target="_blank" class="btn btn-secondary btn-sm" style="text-decoration:none">📄 View Resume</a>
                </span></div>
            </div>`;
    })
    .catch(err => console.error("Student fetch error:", err));
};

// =======================
// CREATE JOB
// =======================
window.createJob = function () {
    const title      = document.getElementById("title").value;
    const skills     = document.getElementById("skills").value;
    const experience = document.getElementById("experience").value;
    const salary     = document.getElementById("salary").value;

    fetch('/company/job', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ title, skills_required: skills, experience, salary })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.msg);
        loadDashboard();
    })
    .catch(err => console.error("Create job error:", err));
};

// =======================
// TOGGLE JOB
// =======================
window.toggleJob = function (id) {
    fetch(`/company/job/${id}/toggle`, {
        method: 'PUT',
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => { alert(data.msg); loadDashboard(); })
    .catch(err => console.error("Toggle error:", err));
};

// =======================
// VIEW APPLICATIONS
// =======================
window.viewApps = function (jobId) {
    fetch(`/company/job/${jobId}/applications`, {
        headers: { "Authorization": "Bearer " + token }
    })
    .then(res => res.json())
    .then(data => { alert(JSON.stringify(data, null, 2)); })
    .catch(err => console.error("View apps error:", err));
};

// =======================
// UPDATE STATUS
// =======================
window.updateStatus = function (id, status) {
    const token = localStorage.getItem("token");

    if (status === 'selected') {
        const fileInput = document.getElementById("offerLetterInput");
        fileInput.value = "";

        fileInput.onchange = function () {
            const file = fileInput.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append("status", "selected");
            formData.append("offer_letter", file);
            formData.append("feedback", "Congratulations! You are selected.");

            fetch(`/company/application/${id}/update`, {
                method: 'PUT',
                headers: { "Authorization": "Bearer " + token },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                alert(data.msg);
                loadDashboard();
            })
            .catch(err => alert("Upload failed: " + err.message));
        };

        fileInput.click();

    } else {
        fetch(`/company/application/${id}/update`, {
            method: 'PUT',
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ status, feedback: `Status updated to ${status}` })
        })
        .then(res => res.json())
        .then(data => { alert(data.msg); loadDashboard(); })
        .catch(err => console.error("Update error:", err));
    }
};

// =======================
// SCHEDULE INTERVIEW
// =======================
window.scheduleInterview = function (id) {
    const date     = prompt("Enter Date (YYYY-MM-DD)");
    const location = prompt("Enter Location");

    fetch(`/company/application/${id}/schedule`, {
        method: 'PUT',
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ date, location })
    })
    .then(res => res.json())
    .then(data => { alert(data.msg); loadDashboard(); })
    .catch(err => console.error("Schedule error:", err));
};

window.onload = function () {
    console.log("Page loaded → fetching dashboard");
    loadDashboard();
};
