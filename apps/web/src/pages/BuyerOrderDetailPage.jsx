import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { apiRequest, isAuthenticated } from '../lib/api.js'
import { PageContainer } from '../components/SiteLayout.jsx'

export default function BuyerOrderDetailPage() {
  const { orderId } = useParams()
  const [order, setOrder] = useState(null)
  const [state, setState] = useState(isAuthenticated() ? 'loading' : 'signed-out')
  const [error, setError] = useState('')
  const [rating, setRating] = useState('5')
  const [reviewBody, setReviewBody] = useState('')
  const [reviewState, setReviewState] = useState('')
  useEffect(() => {
    if (!isAuthenticated()) return
    let cancelled = false
    apiRequest(`/orders/${orderId}`).then((value) => { if (!cancelled) { setOrder(value); setState('ready') } }).catch((err) => { if (!cancelled) { setError(err.message); setState('error') } })
    return () => { cancelled = true }
  }, [orderId])
  async function submitReview(event) {
    event.preventDefault(); setReviewState('')
    try {
      await apiRequest('/engagement/reviews', { method: 'POST', body: JSON.stringify({ order_id: orderId, rating: Number(rating), body: reviewBody || null }) })
      setReviewState('Thanks for sharing your experience.')
    } catch (err) { setReviewState(err.message) }
  }
  return <PageContainer><div className="page-heading"><span className="eyebrow">Buyer dashboard</span><h1>Order details</h1><p>Order reference {orderId}</p></div>{state === 'loading' && <div className="loading-state">Loading order…</div>}{state === 'signed-out' && <div className="empty-state"><strong>Sign in to view this order</strong><p><Link className="text-link" to="/login">Log in</Link> to continue.</p></div>}{state === 'error' && <div className="error-state" role="alert">{error}</div>}{state === 'ready' && <><section className="panel"><h2>Order summary</h2><div className="metric-grid"><div className="metric"><strong>{order.currency} {Number(order.total_amount).toFixed(2)}</strong><span>Total</span></div><div className="metric"><strong>{order.status.replaceAll('_', ' ')}</strong><span>Status</span></div><div className="metric"><strong>{new Date(order.created_at).toLocaleDateString()}</strong><span>Placed</span></div></div><p>Order ID: {order.id}</p><p>Listing: <Link className="text-link" to={`/listings/${order.listing_id}`}>View account listing</Link></p><Link className="btn btn-secondary" to="/dashboard/buyer">Back to dashboard</Link></section>{order.status === 'COMPLETED' && <section className="panel" style={{ marginTop: 18 }}><h2>Review your purchase</h2><form onSubmit={submitReview}><div className="form-field"><label htmlFor="rating">Rating</label><select id="rating" className="field" value={rating} onChange={(event) => setRating(event.target.value)}>{[5, 4, 3, 2, 1].map((value) => <option value={value} key={value}>{value} stars</option>)}</select></div><div className="form-field"><label htmlFor="review">Review (optional)</label><textarea id="review" className="field" rows="3" maxLength="2000" value={reviewBody} onChange={(event) => setReviewBody(event.target.value)} /></div>{reviewState && <p role="status">{reviewState}</p>}<button className="btn btn-primary">Submit review</button></form></section>}</>}</PageContainer>
}
