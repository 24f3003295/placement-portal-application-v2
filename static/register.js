const app = Vue.createApp({
    delimiters: ['[[', ']]'],

    data() {
        return {
            role: "",
            email: "",
            password: "",
            company_name: "",
            industry: "",
            location: "",
            website: "",
            name: "",
            course: "",
            loading: false,
            error: ""
        }
    },

    methods: {
        async register() {
            if (!this.role) {
                this.error = "Please select your role.";
                return;
            }

            this.loading = true;
            this.error = "";

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
                    this.error = result.error || "Registration failed. Please check your details.";
                }
            } catch (err) {
                this.error = "Connection error. Please try again.";
            } finally {
                this.loading = false;
            }
        }
    }
});

app.mount("#app");
