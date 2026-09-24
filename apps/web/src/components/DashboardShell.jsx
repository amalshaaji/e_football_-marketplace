import { Link } from 'react-router-dom'
import { PageContainer } from './SiteLayout.jsx'

export default function DashboardShell({ role, title, description, nav, metrics, children }) {
  return <PageContainer>
    <div className="dashboard-top"><span className="eyebrow">{role} dashboard</span><h1>{title}</h1><p>{description}</p></div>
    <div className="dashboard-grid"><aside className="dashboard-nav" aria-label={`${role} dashboard navigation`}>{nav.map((item) => { const entry = typeof item === 'string' ? { label: item, to: '#' } : item; return <Link key={entry.label} to={entry.to}>{entry.label}</Link> })}</aside><div><section className="metric-grid">{metrics.map(([label, value]) => <div className="metric" key={label}><strong>{value}</strong><span>{label}</span></div>)}</section>{children}</div></div>
  </PageContainer>
}
