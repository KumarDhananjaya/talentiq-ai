import { Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Candidates from "./pages/Candidates";
import Jobs from "./pages/Jobs";

function App() {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <main className="flex-1 p-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />

          <Route
            path="/candidates"
            element={<Candidates />}
          />

          <Route
            path="/jobs"
            element={<Jobs />}
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;