import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { PageContainer } from '../components/SiteLayout.jsx'
import { apiRequest, isAuthenticated } from '../lib/api.js'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ListingDetailsPage() {
  const { listingId } = useParams()
  const [listing, setListing] = useState(null)
  const [state, setState] = useState('loading')
  const [favorite, setFavorite] = useState(false)
  const [actionError, setActionError] = useState('')
  const [messageBody, setMessageBody] = useState('')
  const [messageSent, setMessageSent] = useState(false)
  const [reportOpen, setReportOpen] = useState(false)
  const [reportReason, setReportReason] = useState('Suspicious listing')
  const [reportSent, setReportSent] = useState(false)
  useEffect(() => {
    let cancelled = false
    fetch(`${API_URL}/api/v1/listings/${listingId}`).then(async (response) => {
      if (!response.ok) throw new Error(`Listing unavailable (${response.status})`)
      return response.json()
    }).then((data) => { if (!cancelled) { setListing(data); setState('ready') } }).catch(() => { if (!cancelled) setState('error') })
    return () => { cancelled = true }
  }, [listingId])

  async function toggleFavorite() {
    if (!isAuthenticated()) return
    setActionError('')
    try {
      await apiRequest(`/favorites/${listingId}`, { method: favorite ? 'DELETE' : 'PUT' })
      setFavorite((value) => !value)
    } catch (err) { setActionError(err.message) }
  }

  async function contactSeller(event) {
    event.preventDefault(); setActionError('')
    try {
      await apiRequest('/engagement/conversations', { method: 'POST', body: JSON.stringify({ listing_id: listingId, body: messageBody }) })
      setMessageBody(''); setMessageSent(true)
    } catch (err) { setActionError(err.message) }
  }

  async function reportListing(event) {
    event.preventDefault(); setActionError('')
    try {
      await apiRequest('/engagement/reports', { method: 'POST', body: JSON.stringify({ listing_id: listingId, reason: reportReason }) })
      setReportSent(true); setReportOpen(false)
    } catch (err) { setActionError(err.message) }
  }

  return <PageContainer>
    {state === 'loading' && <div className="loading-state" role="status">Loading listing…</div>}
    {state === 'error' && <div className="error-state" role="alert"><strong>This listing is unavailable</strong><p>It may have been removed or is no longer active.</p><Link className="btn btn-secondary" to="/marketplace">Back to marketplace</Link></div>}
    {state === 'ready' && <>
      <div className="page-heading"><span className="eyebrow">Marketplace listing</span><h1>{listing.title}</h1><p>{listing.description || 'Review the account details and seller information before continuing.'}</p></div>
      <div className="dashboard-grid" style={{ gridTemplateColumns: '1.2fr .8fr' }}>
        <section className="listing-card"><div className="listing-art"><div className="listing-rating"><strong>{listing.team_strength}</strong><span>TEAM STRENGTH</span></div></div><div className="listing-body"><h3>{listing.title}</h3><div className="listing-meta"><span>Account details available after sign in</span></div></div></section>
        <section className="panel">
          <span className="eyebrow">Marketplace listing</span><h2 style={{ marginTop: 10 }}>Account details</h2><p style={{ color: 'var(--muted)', fontSize: 14, lineHeight: 1.7 }}>Team strength {listing.team_strength}. Listing currency: {listing.currency}.</p>
          <div className="listing-bottom"><span className="listing-price">${Number(listing.price_amount).toFixed(2)}</span><span className="rating">{listing.currency}</span></div>
          {isAuthenticated() ? <button className="btn btn-secondary btn-block" style={{ marginTop: 18 }} onClick={toggleFavorite}>{favorite ? 'Remove from favorites' : 'Save to favorites'}</button> : <Link className="btn btn-secondary btn-block" style={{ marginTop: 18 }} to="/login">Log in to save</Link>}
          {isAuthenticated() ? <form onSubmit={contactSeller} style={{ marginTop: 16 }}><label className="form-field"><span>Message the seller</span><textarea className="field" rows="3" maxLength="5000" required value={messageBody} onChange={(event) => setMessageBody(event.target.value)} /></label><button className="btn btn-secondary btn-block">Send message</button>{messageSent && <p role="status">Message sent. <Link className="text-link" to="/messages">Open inbox</Link></p>}</form> : <Link className="btn btn-secondary btn-block" style={{ marginTop: 10 }} to="/login">Log in to message seller</Link>}
          {isAuthenticated() && <div style={{ marginTop: 16 }}><button className="btn btn-quiet" onClick={() => setReportOpen((value) => !value)}>Report this listing</button>{reportSent && <p role="status">Report submitted for review.</p>}{reportOpen && <form onSubmit={reportListing}><label className="form-field"><span>Reason for report</span><select className="field" value={reportReason} onChange={(event) => setReportReason(event.target.value)}><option>Suspicious listing</option><option>Misleading information</option><option>Prohibited content</option><option>Other</option></select></label><button className="btn btn-secondary">Submit report</button></form>}</div>}
          {actionError && <p className="error-state" role="alert">{actionError}</p>}
          <Link className="btn btn-primary btn-block" style={{ marginTop: 10 }} to="/login">Log in to continue</Link>
        </section>
      </div>
    </>}
  </PageContainer>
}
