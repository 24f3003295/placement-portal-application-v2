const app = Vue.createApp({
    delimiters: ['[[', ']]'],

    data() {
        return {
            email: "",
            password: "",
            role: "",
            loading: false,
            error: ""
        }
    },

    methods: {
        async login() {
            if (!this.role) {
                this.error = "Please select your role first.";
                return;
            }
            if (!this.email || !this.password) {
                this.error = "Email and password are required.";
                return;
            }

            this.loading = true;
            this.error = "";

            try {
                const res = await axios.post("/api/login", {
                    email: this.email,
                    password: this.password
                });

                localStorage.setItem("token", res.data.token);
                localStorage.setItem("role", res.data.role);

                window.location.href = "/" + res.data.role;

            } catch (err) {
                this.error = err.response?.data?.error || "Invalid email or password. Please try again.";
            } finally {
                this.loading = false;
            }
        },

        goToRegister() {
            window.location.href = "/register";
        }
    }
});

app.mount("#app");
