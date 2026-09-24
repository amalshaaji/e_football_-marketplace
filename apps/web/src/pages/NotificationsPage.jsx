import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiRequest, isAuthenticated } from '../lib/api.js'
import { PageContainer } from '../components/SiteLayout.jsx'

export default function NotificationsPage() {
  const [items, setItems] = useState([])
  const [state, setState] = useState(isAuthenticated() ? 'loading' : 'signed-out')
  const [error, setError] = useState('')
  useEffect(() => {
    if (!isAuthenticated()) return
    let cancelled = false
    apiRequest('/engagement/notifications').then((value) => { if (!cancelled) { setItems(value); setState('ready') } }).catch((err) => { if (!cancelled) { setError(err.message); setState('error') } })
    return () => { cancelled = true }
  }, [])
  async function markRead(id) {
    try { const updated = await apiRequest(`/engagement/notifications/${id}/read`, { method: 'PATCH' }); setItems((current) => current.map((item) => item.id === id ? updated : item)) }
    catch (err) { setError(err.message) }
  }
  return <PageContainer><div className="page-heading"><span className="eyebrow">Account activity</span><h1>Notifications</h1><p>Updates about messages and marketplace activity.</p></div>{state === 'signed-out' && <div className="empty-state"><strong>Sign in to view notifications</strong><p><Link className="text-link" to="/login">Log in</Link> to continue.</p></div>}{state === 'loading' && <div className="loading-state">Loading notifications…</div>}{state === 'error' && <div className="error-state" role="alert">{error}</div>}{state === 'ready' && (items.length ? <section className="panel">{items.map((item) => <article className="notification-row" key={item.id}><div><strong>{item.event_type.replaceAll('.', ' ')}</strong><p>{item.event_type.startsWith('message') ? 'You have a conversation update.' : 'There is an update to your marketplace activity.'}</p><small>{new Date(item.created_at).toLocaleString()}</small></div>{item.read_at ? <span className="pill gray">Read</span> : <button className="btn btn-quiet" onClick={() => markRead(item.id)}>Mark read</button>}</article>)}</section> : <div className="empty-state"><strong>You’re all caught up</strong><p>New activity notifications will appear here.</p></div>)}</PageContainer>
}
