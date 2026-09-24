import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import DashboardShell from '../components/DashboardShell.jsx'
import { apiRequest, isAuthenticated } from '../lib/api.js'

export default function BuyerDashboardPage() {
  const [orders, setOrders] = useState([])
  const [favorites, setFavorites] = useState([])
  const [state, setState] = useState(isAuthenticated() ? 'loading' : 'signed-out')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!isAuthenticated()) return
    let cancelled = false
    Promise.all([apiRequest('/orders/mine'), apiRequest('/favorites')]).then(([orderData, favoriteData]) => {
      if (cancelled) return
      setOrders(orderData)
      setFavorites(favoriteData)
      setState('ready')
    }).catch((err) => {
      if (cancelled) return
      setError(err.message)
      setState('error')
    })
    return () => { cancelled = true }
  }, [])

  async function removeFavorite(listingId) {
    try {
      await apiRequest(`/favorites/${listingId}`, { method: 'DELETE' })
      setFavorites((current) => current.filter((item) => item.listing_id !== listingId))
    } catch (err) { setError(err.message) }
  }

  const metrics = [['Orders', state === 'ready' ? String(orders.filter((order) => order.buyer_id === JSON.parse(localStorage.getItem('current_user') || '{}').id).length) : '—'], ['Favorites', state === 'ready' ? String(favorites.length) : '—'], ['Unread messages', '—']]
  return <DashboardShell role="Buyer" title="Your account" description="Keep track of your purchases and saved squads." nav={[{ label: 'Overview', to: '/dashboard/buyer' }, { label: 'Messages', to: '/messages' }, { label: 'Notifications', to: '/notifications' }, { label: 'Marketplace', to: '/marketplace' }]} metrics={metrics}>
    {state === 'signed-out' && <section className="panel"><div className="empty-state"><strong>Sign in to see your activity</strong><p>Your orders and saved squads are linked to your marketplace account.</p><Link className="btn btn-primary" to="/login">Log in</Link></div></section>}
    {state === 'loading' && <section className="panel"><div className="loading-state" role="status">Loading your account…</div></section>}
    {state === 'error' && <section className="panel"><div className="error-state" role="alert"><strong>Could not load your dashboard</strong><p>{error}</p><button className="btn btn-secondary" onClick={() => window.location.reload()}>Try again</button></div></section>}
    {state === 'ready' && <>
      <section className="panel" id="orders"><h2>Recent orders</h2>{orders.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th>Order</th><th>Amount</th><th>Status</th><th>Placed</th></tr></thead><tbody>{orders.map((order) => <tr key={order.id}><td><Link className="text-link" to={`/dashboard/buyer/orders/${order.id}`}>{order.id.slice(0, 8)}</Link></td><td>{order.currency} {Number(order.total_amount).toFixed(2)}</td><td><span className="pill">{order.status.replaceAll('_', ' ')}</span></td><td>{new Date(order.created_at).toLocaleDateString()}</td></tr>)}</tbody></table></div> : <div className="empty-state"><strong>Your orders will show up here</strong><p>When you purchase an account, you can track it from this page.</p><Link className="btn btn-secondary" to="/marketplace">Browse accounts</Link></div>}</section>
      <section className="panel" id="favorites" style={{ marginTop: 20 }}><h2>Saved accounts</h2>{favorites.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th>Account</th><th>Team strength</th><th>Price</th><th>Status</th><th /></tr></thead><tbody>{favorites.map((item) => <tr key={item.listing_id}><td><Link className="text-link" to={`/listings/${item.listing_id}`}>{item.title}</Link></td><td>{item.team_strength}</td><td>{item.currency} {Number(item.price_amount).toFixed(2)}</td><td>{item.status}</td><td><button className="btn btn-quiet" onClick={() => removeFavorite(item.listing_id)}>Remove</button></td></tr>)}</tbody></table></div> : <div className="empty-state"><strong>No saved accounts yet</strong><p>Save listings while you browse and they’ll appear here.</p><Link className="btn btn-secondary" to="/marketplace">Explore marketplace</Link></div>}</section>
    </>}
  </DashboardShell>
}
