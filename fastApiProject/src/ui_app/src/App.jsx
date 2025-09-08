// App.js
import React, { useState, useEffect } from 'react';
import './App.css';
import LogInForm from "./components/LogInForm";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    const savedStatus = localStorage.getItem('isLoggedIn');
    return savedStatus === 'true';
  });

  const [activeTab, setActiveTab] = useState('login');
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    localStorage.setItem('isLoggedIn', isLoggedIn);
  }, [isLoggedIn]);

  const handleLogin = (loginData) => {
    // Эмуляция успешного логина с получением данных пользователя
    const mockUserData = {
      username: loginData.username || loginData.email,
      email: loginData.email,
      loginTime: new Date().toLocaleTimeString(),
      userId: Math.floor(Math.random() * 1000) // Mock ID
    };
    
    setUserData(mockUserData);
    setIsLoggedIn(true);
  };

  const handleRegister = (registerData) => {
    // Эмуляция успешной регистрации
    const mockUserData = {
      username: registerData.username,
      email: registerData.email,
      registrationDate: new Date().toLocaleDateString(),
      userId: Math.floor(Math.random() * 1000)
    };
    
    setUserData(mockUserData);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('isLoggedIn');
    setIsLoggedIn(false);
    setUserData(null);
    setActiveTab('login'); // Возвращаем на вкладку логина после выхода
  };

  // Компонент формы логина
  const LoginForm = ({ onLogin }) => {
    const [formData, setFormData] = useState({ username: '', password: '' });

    const handleSubmit = (e) => {
      e.preventDefault();
      if (formData.username && formData.password) {
        onLogin(formData);
      }
    };

    return (
<LogInForm />
    );
  };

  // Компонент формы регистрации
  const RegisterForm = ({ onRegister }) => {
    const [formData, setFormData] = useState({ 
      username: '', 
      email: '', 
      password: '', 
      confirmPassword: '' 
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      if (formData.password === formData.confirmPassword) {
        onRegister(formData);
      } else {
        alert('Пароли не совпадают!');
      }
    };

    return (
      <form onSubmit={handleSubmit} className="auth-form">
        <h3>Регистрация</h3>
        <div className="form-group">
          <label>Имя пользователя:</label>
          <input
            type="text"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <label>Пароль:</label>
          <input
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <label>Подтвердите пароль:</label>
          <input
            type="password"
            value={formData.confirmPassword}
            onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
            required
          />
        </div>
        <button type="submit" className="submit-btn">Зарегистрироваться</button>
      </form>
    );
  };

  // Компонент вкладок
  const AuthTabs = () => (
    <div className="auth-container">
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'login' ? 'active' : ''}`}
          onClick={() => setActiveTab('login')}
        >
          Вход
        </button>
        <button 
          className={`tab ${activeTab === 'register' ? 'active' : ''}`}
          onClick={() => setActiveTab('register')}
        >
          Регистрация
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'login' ? (
          <LoginForm onLogin={handleLogin} />
        ) : (
          <RegisterForm onRegister={handleRegister} />
        )}
      </div>
    </div>
  );

  // Компонент dashboard после успешного входа
  const UserDashboard = () => (
    <div className="dashboard">
      <h2>Добро пожаловать, {userData?.username}!</h2>
      <p>Вы успешно вошли в систему.</p>
      
      <div className="info-blocks">
        <div className="info-block">
          <h4>📧 Ваш email</h4>
          <p>{userData?.email}</p>
        </div>
        
        <div className="info-block">
          <h4>🆔 ID пользователя</h4>
          <p>{userData?.userId}</p>
        </div>
        
        <div className="info-block">
          <h4>🕒 Время входа</h4>
          <p>{userData?.loginTime || userData?.registrationDate}</p>
        </div>
        
        <div className="info-block">
          <h4>✅ Статус</h4>
          <p>Аккаунт активен</p>
        </div>
      </div>
      
      <button onClick={handleLogout} className="logout-btn">
        Выйти
      </button>
    </div>
  );

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔐 Auth System</h1>
        <p>Демонстрационная система аутентификации</p>
      </header>
      
      <main className="app-main">
        {!isLoggedIn ? <AuthTabs /> : <UserDashboard />}
      </main>
    </div>
  );
}

export default App;