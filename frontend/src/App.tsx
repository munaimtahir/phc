import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Nav from "./components/Nav";
import Login from "./components/Login";
import { useAuth } from "./lib/auth";
import RegistryPage from "./pages/registry/RegistryPage";
import DailyPage from "./pages/daily/DailyPage";
import PrintPage from "./pages/print/PrintPage";
import DraftingPage from "./pages/drafting/DraftingPage";

function App() {
  const { username } = useAuth();

  if (!username) {
    return <Login />;
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        <Nav />
        <Routes>
          <Route path="/" element={<Navigate to="/registry" replace />} />
          <Route path="/registry" element={<RegistryPage />} />
          <Route path="/daily" element={<DailyPage />} />
          <Route path="/print" element={<PrintPage />} />
          <Route path="/drafting" element={<DraftingPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
