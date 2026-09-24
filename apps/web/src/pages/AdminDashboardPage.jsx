import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiRequest, isAuthenticated } from '../lib/api.js'
import { PageContainer } from '../components/SiteLayout.jsx'

const sections = ['Overview', 'Listings', 'Reports', 'Users', 'Orders', 'Payments', 'Reviews', 'Audit log']
const endpoints = { Listings: '/admin/listings?status_filter=PENDING_REVIEW', Reports: '/admin/reports', Users: '/admin/users', Orders: '/admin/orders', Payments: '/admin/payments', Reviews: '/admin/reviews?include_hidden=true', 'Audit log': '/admin/audit-logs' }

export default function AdminDashboardPage() {
  const [section, setSection] = useState('Overview')
  const [stats, setStats] = useState(null)
  const [items, setItems] = useState([])
  const [state, setState] = useState(isAuthenticated() ? 'loading' : 'signed-out')
  const [error, setError] = useState('')
  const [reload, setReload] = useState(0)

  const load = useCallback(async () => {
    const summary = await apiRequest('/admin/stats')
    setStats(summary)
    if (section === 'Overview') {
      const [listings, reports] = await Promise.all([apiRequest(endpoints.Listings), apiRequest(endpoints.Reports)])
      setItems([...(listings.items || []), ...(reports.items || [])])
    } else {
      const result = await apiRequest(endpoints[section])
      setItems(result.items || [])
    }
    setState('ready')
  }, [section])

  useEffect(() => {
    if (!isAuthenticated()) return
    let cancelled = false
    Promise.resolve().then(() => load()).catch((err) => { if (!cancelled) { setError(err.message); setState('error') } })
    return () => { cancelled = true }
  }, [load, reload])

  async function moderateListing(id, status) {
    try { await apiRequest(`/admin/listings/${id}/moderation`, { method: 'PATCH', body: JSON.stringify({ status }) }); setReload((value) => value + 1) }
    catch (err) { setError(err.message) }
  }
  async function moderateReport(id, status) {
    try { await apiRequest(`/admin/reports/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) }); setReload((value) => value + 1) }
    catch (err) { setError(err.message) }
  }
  async function toggleUser(item) {
    try { await apiRequest(`/admin/users/${item.id}/status`, { method: 'PATCH', body: JSON.stringify({ is_active: !item.is_active }) }); setReload((value) => value + 1) }
    catch (err) { setError(err.message) }
  }
  async function moderateReview(id, hidden) {
    try { await apiRequest(`/engagement/reviews/${id}/moderation?hidden=${hidden}`, { method: 'PATCH' }); setReload((value) => value + 1) }
    catch (err) { setError(err.message) }
  }

  return <PageContainer>
    <div className="dashboard-top"><span className="eyebrow">Administration</span><h1>Platform overview</h1><p>Review marketplace activity and moderate submissions.</p></div>
    {state === 'signed-out' && <div className="empty-state"><strong>Administrator sign-in required</strong><p><Link className="text-link" to="/login">Log in</Link> with an administrator account to open these tools.</p></div>}
    {state === 'loading' && <div className="loading-state">Loading administration…</div>}
    {state === 'error' && <div className="error-state" role="alert"><strong>Could not load admin tools</strong><p>{error}</p><button className="btn btn-secondary" onClick={() => setReload((value) => value + 1)}>Try again</button></div>}
    {state === 'ready' && <>
      <section className="metric-grid">{[['Users', stats.users], ['Active listings', stats.active_listings], ['Pending review', stats.pending_listings], ['Open reports', stats.open_reports], ['Orders', stats.orders], ['Payments', stats.payments]].map(([label, value]) => <div className="metric" key={label}><strong>{value}</strong><span>{label}</span></div>)}</section>
      <div className="dashboard-nav" style={{ display: 'flex', gap: 5, overflowX: 'auto', margin: '18px 0' }}>{sections.map((item) => <button className={`btn ${section === item ? 'btn-primary' : 'btn-quiet'}`} key={item} onClick={() => { setSection(item); setState('loading') }}>{item}</button>)}</div>
      {error && <div className="error-state" role="alert" style={{ marginBottom: 14 }}>{error}</div>}
      <section className="panel"><h2>{section === 'Overview' ? 'Pending moderation' : section}</h2>
        {items.length === 0 ? <div className="empty-state"><strong>{section === 'Overview' ? 'All caught up' : `No ${section.toLowerCase()} to show`}</strong><p>Items that need attention will appear here.</p></div> : <div className="table-wrap"><table className="data-table"><thead><tr><th>Item</th><th>Details</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead><tbody>{items.map((item) => <tr key={item.id}>
          <td>{item.title || item.email || item.reason || item.action || item.id.slice(0, 8)}</td>
          <td>{item.price_amount ? `${item.currency} ${Number(item.price_amount).toFixed(2)}` : item.rating ? `${item.rating} stars` : item.entity_type || item.role || item.provider || item.total_amount ? `${item.entity_type || item.role || item.provider || `${item.currency} ${item.total_amount}`}` : item.details || item.details === null ? JSON.stringify(item.details) : item.id.slice(0, 8)}</td>
          <td><span className="pill">{item.status || (item.is_active ? 'ACTIVE' : item.is_active === false ? 'DISABLED' : item.is_hidden ? 'HIDDEN' : '—')}</span></td>
          <td>{item.created_at ? new Date(item.created_at).toLocaleDateString() : '—'}</td>
          <td>{section === 'Listings' && item.status === 'PENDING_REVIEW' && <><button className="btn btn-quiet" onClick={() => moderateListing(item.id, 'ACTIVE')}>Approve</button><button className="btn btn-quiet" onClick={() => moderateListing(item.id, 'REJECTED')}>Reject</button></>}{section === 'Reports' && <><button className="btn btn-quiet" onClick={() => moderateReport(item.id, 'UNDER_REVIEW')}>Review</button><button className="btn btn-quiet" onClick={() => moderateReport(item.id, 'RESOLVED')}>Resolve</button><button className="btn btn-quiet" onClick={() => moderateReport(item.id, 'DISMISSED')}>Dismiss</button></>}{section === 'Users' && <button className="btn btn-quiet" disabled={JSON.parse(localStorage.getItem('current_user') || '{}').id === item.id} onClick={() => toggleUser(item)}>{item.is_active ? 'Disable' : 'Enable'}</button>}{section === 'Reviews' && <button className="btn btn-quiet" onClick={() => moderateReview(item.id, !item.is_hidden)}>{item.is_hidden ? 'Unhide' : 'Hide'}</button>}</td>
        </tr>)}</tbody></table></div>}
      </section>
    </>}
  </PageContainer>
}
