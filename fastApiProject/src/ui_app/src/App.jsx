import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import HomeForm from "./components/HomeForm";
import SignupForm from "./components/SignupForm";
import LoginForm from "./components/LoginForm";
import ResetPassword from "./components/ResetPassword";
import Dashboard from "./components/Dashboard";

export default function App() {
      const [isLoggedIn, setIsLoggedIn] = useState(false);

      const handleLoginSuccess = () => {
        setIsLoggedIn(true);
      };



  return (
    <Router>
       <div>
          {isLoggedIn ? (
            // Рендер страниц после логина (например, дашборд)
 <div>
          <nav>
            <ul>
                <li>
                    <Link to="/">Home</Link>
                </li>
                <li>
                    <Link to="/login">Login</Link>
                </li>
                <li>
                    <Link to="/signup">Signup</Link>
                </li>
                <li>
                    <Link to="/reset">Reset Passord</Link>
                </li>
            </ul>
        </nav>
        <div>
          <Routes>
          <Route path="/" element={<HomeForm/>}/>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/reset" element={<Reset />} />
          <Route path="/dashboard" element={<Dashboard2 />} />
          </Routes>
        </div>
 </div>
          ) : (
            // Рендер страницы логина
              <div>
        <nav>
            <ul>
                <li>
                    <Link to="/">Home</Link>
                </li>
                <li>
                    <Link to="/reset">Reset Passord</Link>
                </li>
                <li>
                    <Link to="/dashboard">Dashboard</Link>
                </li>
            </ul>
        </nav>
        <div>
          <Routes>
          <Route path="/" element={<HomeForm/>}/>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/reset" element={<Reset />} />
          <Route path="/dashboard" element={<Dashboard2 />} />
        </Routes>
        </div>
                  </div>
          )}
        </div>
    </Router>
  );
}

function Home() {
  return (
    <div>
      <h2>Home</h2>
      <HomeForm />
    </div>
  );
}

function Login() {
  return (
    <div>
      <h2>Login</h2>
      <LoginForm/>
    </div>
  );
}

function Signup() {
  return (
    <div>
      <h2>Signup</h2>
      <SignupForm/>
    </div>
  );
}

function Reset() {
  return (
    <div>
      <h2>Password Reset</h2>
      <ResetPassword />
    </div>
  );
}

function Dashboard2() {
  return (
    <div>
      <h2>Dashboard</h2>
      <Dashboard/>
    </div>
  );
}