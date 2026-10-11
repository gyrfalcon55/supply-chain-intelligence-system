import { NavLink, Outlet } from 'react-router-dom';
import { Bot, Database, Truck, ClipboardList, CalendarDays, FlaskConical, Boxes, Activity, PanelLeftClose } from 'lucide-react';
const links = [
  { to: '/', label: 'Analytics Agent', icon: Bot, end: true },
  { to: '/tables', label: 'View Tables', icon: Database },
  { to: '/reports', label: 'Inventory & Suppliers', icon: Truck },
  { to: '/procurement', label: 'Procurement Orders', icon: ClipboardList },
  { to: '/simulation', label: 'Sales Simulation', icon: CalendarDays },
  { to: '/pipeline', label: 'ML Pipeline', icon: FlaskConical },
];
export default function Layout() {
 return <div className="app-shell">
  <aside className="sidebar">
   <div className="brand"><div className="brand-mark"><Boxes size={22}/></div><div><strong>SupplySense</strong><span>INTELLIGENCE PLATFORM</span></div></div>
   <div className="workspace-label">WORKSPACE</div>
   <nav className="nav-list">{links.map(({to,label,icon:Icon,end}) => <NavLink key={to} to={to} end={end} className={({isActive})=>`nav-link ${isActive?'active':''}`}><Icon size={18}/><span>{label}</span>{label==='Analytics Agent'&&<i className="live-dot"/>}</NavLink>)}</nav>
   <div className="sidebar-bottom"><div className="status-line"><span className="live-dot"/> API workspace</div><div className="sidebar-foot"><Activity size={15}/> Demand · Inventory · Procurement</div></div>
  </aside>
  <main className="main-area"><header className="topbar"><div className="mobile-brand"><Boxes size={19}/> SupplySense</div><div className="crumb">Operations <span>/</span> <b>Intelligence workspace</b></div><div className="topbar-right"><span className="status-pill"><i/> System workspace</span><div className="avatar">SC</div></div></header><div className="page-wrap"><Outlet/></div><footer className="footer">SUPPLYSENSE <span>•</span> Supply Chain Intelligence System</footer></main>
 </div>
}