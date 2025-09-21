import Header from './components/Header/Header'
import TeachingSection from './components/TeachingSection'
import DifferencesSection from './components/DifferencesSection'
import IntroSection from './components/IntroSection'
import TabsSection from './components/TabsSection'
import FeedbackSection from './components/FeedbackSection'
import { useState } from 'react'
import EffectSection from './components/EffectSection'
import { BrowserRouter, Routes, Route, Link, Outlet, NavLink } from 'react-router';

import Home from "./components/Home.jsx";
import User from "./components/User.jsx";

const Navigation = () => {
  return (
    <nav
      style={{
        borderBottom: "solid 1px",
        paddingBottom: "1rem",
      }}
    >
      <Link to="/home">Home</Link>
      <Link to="/user">User</Link>
    </nav>

  );
};

const Layout = () => {


  return (
    <>
      <h1>React Router</h1>

      <nav
        style={{
          borderBottom: "solid 1px",
          paddingBottom: "1rem",
        }}
      >
        <NavLink to="/home" >Home</NavLink>
        <NavLink to="/user" >Users</NavLink>
      </nav>

      <main style={{ padding: "1rem 0" }}>
        <Outlet />
      </main>
    </>
  );
};


export default function App() {
  //const [visible, setVisible] = useState(true)
  const [tab, setTab] = useState('effect')

  // setTimeout(() => {
  //   setVisible(false)
  // }, 3000)

  return (
      <>
          <h1>React Router</h1>
    <Routes>
      <Route element={<Layout />}>
        <Route path="home" element={<Home />} />
        <Route path="user" element={<User />} />
      </Route>
    </Routes>
          <div> 2</div>


          <Header/>
          <IntroSection/>


          <TabsSection active={tab} onChange={(current) => setTab(current)}/>

          {tab === 'main' && (
              <>
                  <TeachingSection/>
                  <DifferencesSection/>
              </>
          )}
          {tab === 'feedback' && <FeedbackSection/>}
          {//tab === 'effect' && <EffectSection />
          }


      </>
  )
}
