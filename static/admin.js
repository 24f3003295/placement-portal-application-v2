axios.defaults.headers.common['Authorization'] =
    `Bearer ${localStorage.getItem("token")}`;

const app = Vue.createApp({
    delimiters: ['[[', ']]'],

    data() {
        return {
            stats: {},
            companies: [],
            students: [],
            jobs: [],
            applications: [],
            companySearch: "",
            studentSearch: ""
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
        // Stats
        async fetchStats() {
            const res = await axios.get("/admin/stats");
            this.stats = res.data;
        },

        // Companies
        async fetchCompanies() {
            const res = await axios.get(`/admin/companies?search=${this.companySearch}`);
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
            await axios.put(`/admin/company/${id}/deactivate`);
            this.fetchCompanies();
        },

        // Students
        async fetchStudents() {
            const res = await axios.get(`/admin/students?search=${this.studentSearch}`);
            this.students = res.data;
        },

        async deactivateStudent(id) {
            await axios.put(`/admin/student/${id}/deactivate`);
            this.fetchStudents();
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
