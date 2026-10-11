import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout.jsx';
import ChatPage from './pages/ChatPage.jsx';
import TablesPage from './pages/TablesPage.jsx';
import ReportsPage from './pages/ReportsPage.jsx';
import ProcurementPage from './pages/ProcurementPage.jsx';
import SimulationPage from './pages/SimulationPage.jsx';
import PipelinePage from './pages/PipelinePage.jsx';
function NotFound(){return <div className="panel"><h2>Page not found</h2><p>Use the navigation to open a workspace page.</p></div>}
export default function App(){return <Routes><Route element={<Layout/>}><Route index element={<ChatPage/>}/><Route path="tables" element={<TablesPage/>}/><Route path="reports" element={<ReportsPage/>}/><Route path="procurement" element={<ProcurementPage/>}/><Route path="simulation" element={<SimulationPage/>}/><Route path="pipeline" element={<PipelinePage/>}/><Route path="*" element={<NotFound/>}/></Route></Routes>}