console.log("Student JS Loaded");

const token = localStorage.getItem("token");

if (!token) {
    alert("Login first!");
    window.location.href = "/login";
}

// SWITCH SECTIONS
function showSection(sectionId) {
    const sections = [
        "jobsSection",
        "applicationsSection",
        "interviewsSection",
        "placementsSection",
        "profileSection"
    ];

    sections.forEach(id => {
        document.getElementById(id).style.display = "none";
    });

    document.getElementById(sectionId).style.display = "block";
}

// LOAD JOBS
function loadJobs() {
    fetch('/student/jobs', {
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        let html = "";

        if (!data.length) {
            html = "<li>No jobs available</li>";
        } else {
            data.forEach(j => {
                html += `<li>
                    ${j.title} | ${j.company} | ₹${j.salary}
                    <br>Skills: ${j.skills}
                    <br>
                    <button onclick="applyJob(${j.id})">Apply</button>
                </li><hr>`;
            });
        }

        document.getElementById("jobs").innerHTML = html;
    });
}

// UPDATE PROFILE
function updateProfile() {
    const data = {
        branch: document.getElementById("branch").value,
        cgpa: document.getElementById("cgpa").value,
        graduation_year: document.getElementById("year").value,
        skills: document.getElementById("skillsInput").value,
        resume_link: document.getElementById("resume").value
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
    .then(data => {
        alert(data.msg || data.error);
    });
}

// SEARCH JOBS
function searchJobs() {
    const search = document.getElementById("search").value.trim();

    let url = "/student/jobs";

    if (search !== "") {
        url += `?search=${encodeURIComponent(search)}`;
    }

    fetch(url, {
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        let html = "";

        if (!data.length) {
            html = "<li>No jobs found</li>";
        } else {
            data.forEach(j => {
                html += `<li>
                    ${j.title} | ${j.company} | ₹${j.salary}
                    <br>Skills: ${j.skills}
                    <br>
                    <button onclick="applyJob(${j.id})">Apply</button>
                </li><hr>`;
            });
        }

        document.getElementById("jobs").innerHTML = html;
    });
}

// APPLY JOB
function applyJob(id) {
    fetch(`/student/apply/${id}`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        alert(data.msg || data.error);
    });
}

// LOAD APPLICATIONS
function loadApplications() {
    fetch('/student/applications', {
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        let html = "";

        if (!data.length) {
            html = "<li>No applications yet</li>";
        } else {
            data.forEach(a => {
                html += `<li>
                    ${a.job_title} | ${a.company}
                    <br>Status: ${a.status}
                    <br>Applied: ${a.applied_date}
                    <br>Interview: ${a.interview_date || "Not scheduled"}
                    <br>Location: ${a.interview_location || "-"}
                    <br>Feedback: ${a.feedback || "-"}
                </li><hr>`;
            });
        }

        document.getElementById("applications").innerHTML = html;
    });
}

// LOAD INTERVIEWS
function loadInterviews() {
    fetch('/student/interviews', {
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        let html = "";

        if (!data.length) {
            html = "<li>No interviews scheduled</li>";
        } else {
            data.forEach(i => {
                html += `<li>
                    ${i.job} | ${i.company}
                    <br>Date: ${i.date}
                    <br>Location: ${i.location}
                </li><hr>`;
            });
        }

        document.getElementById("interviews").innerHTML = html;
    });
}

// LOAD PLACEMENTS
function loadPlacements() {
    // Ensure 'token' is retrieved from localStorage if not globally defined
    const token = localStorage.getItem("token");

    fetch('/student/placements', {
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => res.json())
    .then(data => {
        let html = "";

        if (!data || data.length === 0) {
            html = "<li>No placements yet</li>";
        } else {
            data.forEach(p => {
                // We use p.application_id here because that's what the backend sends
                html += `<li>
                    <strong>${p.job_title}</strong> | ${p.company}
                    <br>Salary: ₹${p.salary || 'Negotiable'}
                    <br>Joining: ${p.joining_date || 'To be announced'}
                    <br>
                    <button onclick="downloadOffer(${p.application_id})">Download Offer Letter</button>
                </li><hr>`;
            });
        }

        document.getElementById("placements").innerHTML = html;
    })
    .catch(err => {
        console.error("Error loading placements:", err);
        document.getElementById("placements").innerHTML = "<li>Error loading placement data.</li>";
    });
}

// DOWNLOAD OFFER LETTER
function downloadOffer(id) {
    const token = localStorage.getItem("token");

    // The route matches: /student/application/<int:id>/download
    fetch(`/student/application/${id}/download`, {
        headers: {
            "Authorization": "Bearer " + token
        }
    })
    .then(res => {
        if (res.status === 404) throw new Error("Offer letter file not found on server.");
        if (res.status === 403) throw new Error("You do not have permission to download this.");
        if (!res.ok) throw new Error("Download failed");
        return res.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        // You can make this dynamic if you store the original filename
        a.download = `Offer_Letter_${id}.pdf`; 
        document.body.appendChild(a); // Required for Firefox
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    })
    .catch(err => alert(err.message));
}

// AUTO LOAD
window.onload = function () {
    showSection('jobsSection');
    loadJobs();
};
