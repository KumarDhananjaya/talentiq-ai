import { useEffect, useState } from "react";
import api from "../services/api";

function Dashboard() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await api.get("/health");

        if (response.data.status === "healthy") {
          setStatus("Backend connected successfully");
        } else {
          setStatus("Backend responded, but is not healthy");
        }
      } catch (error) {
        console.error(error);
        setStatus("Backend connection failed");
      }
    };

    checkBackend();
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold">
        TalentIQ AI Dashboard
      </h1>

      <p className="mt-2 text-gray-600">
        AI-Powered Recruitment Intelligence Platform
      </p>

      <div className="mt-6 rounded-lg border bg-white p-6">
        <h2 className="text-lg font-semibold">
          System Status
        </h2>

        <p className="mt-2">
          {status}
        </p>
      </div>
    </div>
  );
}

export default Dashboard;