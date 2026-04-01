axios.defaults.headers.common['Authorization'] =
    `Bearer ${localStorage.getItem("token")}`;

const app = Vue.createApp({
    data() {
        return {
            email: "",
            password: ""
        }
    },
    methods: {
        async login() {
            try {
                const res = await axios.post("http://127.0.0.1:5000/api/login", {
                    email: this.email,
                    password: this.password
                });

                localStorage.setItem("token", res.data.token);
                localStorage.setItem("role", res.data.role);

                // Redirect based on role
                if (res.data.role === "admin") {
                    alert("Go to Admin Dashboard");
                } else if (res.data.role === "company") {
                    alert("Go to Company Dashboard");
                } else {
                    alert("Go to Student Dashboard");
                }

            } catch (err) {
                alert("Login failed");
            }
        }
    }
});

app.mount("#app");
