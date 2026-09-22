import { useNavigate } from "react-router-dom";

function Dashboard() {
    const navigate = useNavigate();

    const logout = () => {
        localStorage.removeItem("token");
        window.location.href = "/login";
    };

    return (
        <div>
            <h1>CodeLens Dashboard</h1>

            <p>
                Welcome to your AI-Powered GitHub Repository Assistant.
            </p>

            <button onClick={() => navigate("/repository")}>
                Import GitHub Repository
            </button>

            <br />
            <br />

            <button onClick={logout}>
                Logout
            </button>
        </div>
    );
}

export default Dashboard;