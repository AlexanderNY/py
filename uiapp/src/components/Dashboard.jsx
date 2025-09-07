import React, { useState } from 'react';



const Dashboard = () => {



  return (
      <div className="dashboard">
          <h2>Добро пожаловать, Q!</h2>
          <p>Вы успешно вошли в систему.</p>

          <div className="info-blocks">
              <div className="info-block">
                  <h4>📧 Ваш email</h4>
                  <p>Q</p>
              </div>

              <div className="info-block">
                  <h4>🆔 ID пользователя</h4>
                  <p>Q</p>
              </div>

              <div className="info-block">
                  <h4>🕒 Время входа</h4>
                  <p>Q</p>
              </div>

              <div className="info-block">
                  <h4>✅ Статус</h4>
                  <p>Аккаунт активен</p>
              </div>
          </div>

          <button className="logout-btn">
              Выйти
          </button>
      </div>
  );
};

export default Dashboard;