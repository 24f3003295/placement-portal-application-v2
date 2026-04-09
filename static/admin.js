axios.defaults.headers.common['Authorization'] =
    `Bearer ${localStorage.getItem("token")}`;

const app = Vue.createApp({
    delimiters: ['[[', ']]'],

    data() {
        return {
            tab: 'companies',
            stats: {},
            companies: [],
            students: [],
            jobs: [],
            applications: [],
            companySearch: "",
            studentSearch: "",
            selectedStudent: null
        }
    },

    mounted() {
        this.fetchStats();
        this.fetchCompanies();
        this.fetchStudents();
        this.fetchJobs();
        this.fetchApplications();
    },

    methods: {
        setTab(name) {
            this.tab = name;
            // Update sidebar active state
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            const idx = ['companies','students','jobs','applications'].indexOf(name);
            const items = document.querySelectorAll('.nav-item');
            if (items[idx]) items[idx].classList.add('active');
        },

        // Stats
        async fetchStats() {
            const res = await axios.get("/admin/stats");
            this.stats = res.data;
        },

        // Companies
        async fetchCompanies() {
            let url = "/admin/companies";
            if (this.companySearch.trim() !== "") url += `?search=${this.companySearch}`;
            const res = await axios.get(url);
            this.companies = res.data;
        },

        async approve(id) {
            await axios.put(`/admin/company/${id}/approve`);
            this.fetchCompanies();
        },

        async deleteCompany(id) {
            await axios.delete(`/admin/company/${id}`);
            this.fetchCompanies();
        },

        async deactivate(id) {
            try {
                const response = await axios.put(`/admin/company/${id}/deactivate`);
                if (response.status === 200) {
                    alert(response.data.msg);
                    await this.fetchCompanies();
                }
            } catch (error) {
                console.error("Deactivation failed:", error);
                const errorMsg = error.response?.data?.error || "Could not deactivate company.";
                alert(errorMsg);
            }
        },

        async viewStudent(id) {
            try {
                const res = await axios.get(`/admin/student/${id}`);
                this.selectedStudent = res.data;
                this.setTab('students');
            } catch (error) {
                const msg = error.response?.data?.error || "Failed to load student";
                alert(msg);
            }
        },

        // Students
        async fetchStudents() {
            let url = "/admin/students";
            if (this.studentSearch.trim() !== "") url += `?search=${this.studentSearch}`;
            const res = await axios.get(url);
            this.students = res.data;
        },

        async deactivateStudent(id) {
            try {
                const response = await axios.put(`/admin/student/${id}/deactivate`);
                alert(response.data.msg);
                await this.fetchStudents();
            } catch (error) {
                const errorMsg = error.response?.data?.error || "An error occurred.";
                alert(errorMsg);
            }
        },

        // Jobs
        async fetchJobs() {
            const res = await axios.get("/admin/jobs");
            this.jobs = res.data;
        },

        async approveJob(id) {
            await axios.put(`/admin/job/${id}/approve`);
            this.fetchJobs();
        },

        async deleteJob(id) {
            await axios.delete(`/admin/job/${id}`);
            this.fetchJobs();
        },

        // Applications
        async fetchApplications() {
            const res = await axios.get("/admin/applications");
            this.applications = res.data;
        },

        async approveApplication(id) {
            await axios.put(`/admin/application/${id}/approve`);
            this.fetchApplications();
        },

        async deleteApplication(id) {
            await axios.delete(`/admin/application/${id}`);
            this.fetchApplications();
        }
    }
});

app.mount("#app");
