import React, { useState } from 'react';

const LoginForm = () => {
  const [user, setUser] = useState({ name: '', pwd: '' , timer: 30, });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await fetch('http://localhost:8003/auth', {
        method: 'POST',
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(user),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Ошибка сервера');
      }

      const result = await response.json();
      setMessage('Успешная авторизация!');
      setUser({ name: '', pwd: '', timer: '' }); // Очищаем форму

    } catch (err) {
      setError(err.message);
      setMessage(JSON.stringify(user));
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setUser(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Имя:</label>
          <input
            type="text"
            name="name"
            value={user.name}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Password:</label>
          <input
            type="password"
            name="pwd"
            value={user.pwd}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Timer:</label>
          <input
            type="timer"
            name="timer"
            value={user.timer}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Отправка...' : 'Войти в личный кабинет'}
        </button>
      </form>

      {message && <div style={{color: 'green'}}>{message}</div>}
      {error && <div style={{color: 'red'}}>Ошибка: {error}</div>}
    </div>
  );
};

export default LoginForm;