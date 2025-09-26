import React from "react";
import ReactDOM from "react-dom/client";
import './index.css'
import './app.css'
import App from './App.jsx'

import {BrowserRouter} from "react-router";
import { createRoot } from "react-dom/client";

const root = document.getElementById("root");
ReactDOM.createRoot(root).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>,
);