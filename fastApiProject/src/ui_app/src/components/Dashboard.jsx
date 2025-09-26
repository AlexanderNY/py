import {Outlet} from "react-router";



const Dashboard = () => {



  return (
<>
      <h1>Dashboard</h1>
      {/* will either be <Home/> or <Settings/> */}
<Outlet />
    </>
  );
};

export default Dashboard;