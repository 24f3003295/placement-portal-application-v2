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
            if (!this.role) {
                alert("Select role");
                return;
            }

            const endpoint = this.role === "company" ? '/company/register' : '/student/register';
            const payload = this.role === "company" ? {
                email: this.email,
                password: this.password,
                company_name: this.company_name,
                industry: this.industry,
                location: this.location,
                website: this.website
            } : {
                email: this.email,
                password: this.password,
                name: this.name
            };

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();

                if (response.ok) {
                    alert(result.msg);
                    window.location.href = "/login";
                } else {
                    // This will show you exactly what went wrong
                    alert("Error: " + (result.error || "Registration failed"));
                }
            } catch (err) {
                alert("Connection error");
            }
        }
    }
});

app.mount("#app");
