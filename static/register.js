const app = Vue.createApp({
    data() {
        return {
            role: "",
            email: "",
            password: "",

            // company
            company_name: "",
            industry: "",
            location: "",
            website: "",

            // student
            name: "",
            course: ""
        }
    },

    methods: {
        async register() {
            if (this.role === "company") {
                await fetch('/company/register', {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: this.email,
                        password: this.password,
                        company_name: this.company_name,
                        industry: this.industry,
                        location: this.location,
                        website: this.website
                    })
                });

            } else if (this.role === "student") {
                await fetch('/student/register', {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: this.email,
                        password: this.password,
                        name: this.name,
                        course: this.course
                    })
                });

            } else {
                alert("Select role");
                return;
            }

            alert("Registered successfully");
            window.location.href = "/login";
        }
    }
});

app.mount("#app");
