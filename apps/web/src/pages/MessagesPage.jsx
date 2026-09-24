import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiRequest, isAuthenticated } from '../lib/api.js'
import { PageContainer } from '../components/SiteLayout.jsx'

export default function MessagesPage() {
  const [conversations, setConversations] = useState([])
  const [selected, setSelected] = useState(null)
  const [body, setBody] = useState('')
  const [state, setState] = useState(isAuthenticated() ? 'loading' : 'signed-out')
  const [error, setError] = useState('')
  const load = async () => { const items = await apiRequest('/engagement/conversations'); setConversations(items); setState('ready') }
  useEffect(() => {
    if (!isAuthenticated()) return
    let cancelled = false
    apiRequest('/engagement/conversations').then((items) => { if (!cancelled) { setConversations(items); setState('ready') } }).catch((err) => { if (!cancelled) { setError(err.message); setState('error') } })
    return () => { cancelled = true }
  }, [])
  async function open(id) {
    try { setSelected(await apiRequest(`/engagement/conversations/${id}`)); setError('') }
    catch (err) { setError(err.message) }
  }
  async function send(event) {
    event.preventDefault()
    if (!selected || !body.trim()) return
    try {
      const message = await apiRequest(`/engagement/conversations/${selected.id}/messages`, { method: 'POST', body: JSON.stringify({ body }) })
      setSelected((value) => ({ ...value, messages: [...value.messages, message] }))
      setBody('')
    } catch (err) { setError(err.message) }
  }
  return <PageContainer><div className="page-heading"><span className="eyebrow">Your inbox</span><h1>Messages</h1><p>Conversations about marketplace listings.</p></div>{state === 'signed-out' && <div className="empty-state"><strong>Sign in to view messages</strong><p><Link className="text-link" to="/login">Log in</Link> to continue.</p></div>}{state === 'loading' && <div className="loading-state">Loading messages…</div>}{state === 'error' && <div className="error-state" role="alert">{error} <button className="btn btn-secondary" onClick={() => load().catch((err) => setError(err.message))}>Try again</button></div>}{state === 'ready' && <div className="dashboard-grid"><aside className="dashboard-nav" aria-label="Conversations">{conversations.length ? conversations.map((item) => <button key={item.id} className="btn btn-quiet btn-block" onClick={() => open(item.id)}>Listing {item.listing_id?.slice(0, 8) || 'conversation'} <small>({item.messages?.length || 0})</small></button>) : <p className="empty-state">No conversations yet.</p>}</aside><section className="panel">{selected ? <><h2>Conversation</h2><div className="message-thread">{selected.messages?.map((message) => <article key={message.id} className="message-bubble"><p>{message.body}</p><small>{new Date(message.created_at).toLocaleString()}{message.read_at ? ' · Read' : ''}</small></article>)}</div><form onSubmit={send}><label className="form-field"><span>Write a message</span><textarea className="field" rows="3" maxLength="5000" value={body} onChange={(event) => setBody(event.target.value)} required /></label>{error && <p className="error-state" role="alert">{error}</p>}<button className="btn btn-primary">Send message</button></form></> : <div className="empty-state"><strong>Select a conversation</strong><p>Choose a conversation to read and reply.</p></div>}</section></div>}</PageContainer>
}
