import React, { Suspense, lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Loader from "./components/Loader.jsx";
import RoleGate from "./components/RoleGate.jsx";
import PageLoader from "./components/PageLoader.jsx";

const Login = lazy(() => import("./pages/Login.jsx"));
const Signup = lazy(() => import("./pages/Signup.jsx"));
const Dashboard = lazy(() => import("./pages/Dashboard.jsx"));
const Profile = lazy(() => import("./pages/Profile.jsx"));
const ServiceBooking = lazy(() => import("./pages/ServiceBooking.jsx"));
const AdminPanel = lazy(() => import("./pages/admin/AdminPanel.jsx"));

export default function App(){
  return (
  <Suspense fallback={<div className="relative min-h-screen"><PageLoader label="Loading module..." /></div>}>
      <Routes>
        <Route path="/" element={<Loader />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
  <Route path="/dashboard" element={<RoleGate allow={["user"]}><Dashboard /></RoleGate>} />
  <Route path="/profile" element={<RoleGate allow={["user"]}><Profile /></RoleGate>} />
  <Route path="/service" element={<RoleGate allow={["user"]}><ServiceBooking /></RoleGate>} />
  <Route path="/admin" element={<RoleGate allow={["admin"]}><AdminPanel /></RoleGate>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
