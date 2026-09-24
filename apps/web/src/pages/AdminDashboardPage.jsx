import DashboardShell from '../components/DashboardShell.jsx'

export default function AdminDashboardPage() {
  return <DashboardShell role="Admin" title="Platform overview" description="Review marketplace activity and moderation queues." nav={['Overview', 'Listings', 'Users', 'Reports', 'Orders', 'Audit log']} metrics={ [['Open reports', '0'], ['Pending listings', '0'], ['Registered users', '0']] }>
    <section className="panel"><h2>Moderation queue</h2><div className="empty-state"><strong>All caught up</strong><p>New reports and listings that need review will appear here.</p></div></section>
  </DashboardShell>
}
