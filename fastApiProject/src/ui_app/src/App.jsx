import Header from './components/Header/Header'
import TeachingSection from './components/TeachingSection'
import DifferencesSection from './components/DifferencesSection'
import IntroSection from './components/IntroSection'
import TabsSection from './components/TabsSection'
import FeedbackSection from './components/FeedbackSection'
import { useState } from 'react'
import { BrowserRouter, Routes, Route, Link, Outlet, NavLink } from 'react-router';
import Dashboard from "./components/Dashboard.jsx";
import Home from "./components/Home.jsx";
import User from "./components/User.jsx";

export default function App() {
  //const [visible, setVisible] = useState(true)
  //const [tab, setTab] = useState('effect')

  // setTimeout(() => {
  //   setVisible(false)
  // }, 3000)

  return (
      <>
          <h1>React Router</h1>
    <nav>
      <NavLink to="/" >
        Home
      </NavLink>
      <NavLink to="/dashboard" >
        Trending Concerts
      </NavLink>
      <NavLink to="/concerts">All Concerts</NavLink>
      <NavLink to="/user">user</NavLink>
    </nav>

 <Routes>
     <Route path="/" element={<Home />} />
  <Route path="dashboard" element={<Dashboard />}>
    <Route index element={<Home />} />
    <Route path="user" element={<User />} />
  </Route>
</Routes>

</>
  )
}
