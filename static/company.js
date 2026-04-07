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
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        console.log("Dashboard data:", data);

        // Jobs
        let jobsHTML = "";
        data.jobs.forEach(j => {
            jobsHTML += `<li>
                ${j.title} 
                <button onclick="toggleJob(${j.id})">Toggle</button>
                <button onclick="viewApps(${j.id})">View Apps</button>
            </li>`;
        });
        document.getElementById("jobs").innerHTML = jobsHTML;

        // Applications
        let appHTML = "";
        data.applications.forEach(a => {
            appHTML += `<li>
                App ID: ${a.id} | Student: ${a.student_id} | Status: ${a.status}
                <button onclick="updateStatus(${a.id}, 'shortlisted')">Shortlist</button>
                <button onclick="updateStatus(${a.id}, 'selected')">Select</button>
                <button onclick="updateStatus(${a.id}, 'rejected')">Reject</button>
                <button onclick="scheduleInterview(${a.id})">Schedule</button>
            </li>`;
        });
        document.getElementById("applications").innerHTML = appHTML;
    })
    .catch(err => console.error("Dashboard error:", err));
};

// =======================
// CREATE JOB
// =======================
window.createJob = function () {
    console.log("Create Job Clicked");

    const title = document.getElementById("title").value;
    const skills = document.getElementById("skills").value;
    const experience = document.getElementById("experience").value;
    const salary = document.getElementById("salary").value;

    console.log("Sending data:", { title, skills, experience, salary });

    fetch('/company/job', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            title: title,
            skills_required: skills,
            experience: experience,
            salary: salary
        })
    })
    .then(res => {
        console.log("Response received");
        return res.json();
    })
    .then(data => {
        console.log("Response data:", data);
        alert(data.msg);
        loadDashboard();
    })
    .catch(err => console.error("Create job error:", err));
};

// =======================
// TOGGLE JOB
// =======================
window.toggleJob = function (id) {
    console.log("Toggling job:", id);

    fetch(`/company/job/${id}/toggle`, {
        method: 'PUT',
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
        alert(data.msg);
        loadDashboard();
    })
    .catch(err => console.error("Toggle error:", err));
};

// =======================
// VIEW APPLICATIONS
// =======================
window.viewApps = function (jobId) {
    console.log("Viewing applications for job:", jobId);

    fetch(`/company/job/${jobId}/applications`, {
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
        alert(JSON.stringify(data, null, 2));
    })
    .catch(err => console.error("View apps error:", err));
};

// =======================
// UPDATE STATUS
// =======================
window.updateStatus = function (id, status) {
    console.log("Updating status:", id, status);

    fetch(`/company/application/${id}/update`, {
        method: 'PUT',
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            status: status
        })
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
        alert(data.msg);
        loadDashboard();
    })
    .catch(err => console.error("Update status error:", err));
};

// =======================
// SCHEDULE INTERVIEW
// =======================
window.scheduleInterview = function (id) {
    const date = prompt("Enter Date (YYYY-MM-DD)");
    const location = prompt("Enter Location");

    console.log("Scheduling:", id, date, location);

    fetch(`/company/application/${id}/schedule`, {
        method: 'PUT',
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({
            date: date,
            location: location
        })
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);
        alert(data.msg);
        loadDashboard();
    })
    .catch(err => console.error("Schedule error:", err));
};
window.onload = function () {
    console.log("Page loaded → fetching dashboard");
    loadDashboard();
};
