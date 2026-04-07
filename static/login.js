const app = Vue.createApp({
    data() {
        return {
            email: "",
            password: "",
            role: ""
        }
    },

    methods: {
        async login() {
            if (!this.role) {
                alert("Select role");
                return;
            }

            try {
                const res = await axios.post("/api/login", {
                    email: this.email,
                    password: this.password
                });

                localStorage.setItem("token", res.data.token);
                localStorage.setItem("role", res.data.role);

                // Redirect
                window.location.href = "/" + res.data.role;

            } catch {
                alert("Login failed");
            }
        },

        goToRegister() {
            window.location.href = "/register";
        }
    }
});

app.mount("#app");
