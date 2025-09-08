import React, { useState } from "react";

export default function LogInForm() {
  // states for registration
  const [formData, setFormData] = useState({
    name: "",
    password: "",
  });

  // states for errors, form submission, and password match
  const [error, setError] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  // handling input changes
  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  // handling form submission
  const handleSubmit = (event) => {
    event.preventDefault();
    if (
      formData.name === "" ||
      formData.password === ""
    ) {
      setError(true);
    } else {
      setSubmitted(true);
      setError(false);
    }

  };

  // show success message
  const successMessage = () => {
    return (
      <div className="success" style={{ display: submitted ? "" : "none" }}>
        <h1>Successfully Logged in!!!</h1>
      </div>
    );
  };

  return (
          <form onSubmit={handleSubmit} className="auth-form">
        <h3>Вход в систему</h3>
        <div className="form-group">
          <label>Имя пользователя или Email:</label>
          <input
            type="text"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
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
        <button type="submit" className="submit-btn">Войти</button>
      </form>
  );
}
