import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import DashboardShell from '../components/DashboardShell.jsx'
import { apiRequest, isAuthenticated } from '../lib/api.js'

const emptyAccount = { title: '', platform: 'PlayStation', team_strength: '', player_count: '', coin_balance: '' }

export default function SellerDashboardPage() {
  const [profile, setProfile] = useState(null)
  const [accounts, setAccounts] = useState([])
  const [listings, setListings] = useState([])
  const [orders, setOrders] = useState([])
  const [state, setState] = useState(isAuthenticated() ? 'loading' : 'signed-out')
  const [error, setError] = useState('')
  const [accountForm, setAccountForm] = useState(emptyAccount)
  const [selectedAccount, setSelectedAccount] = useState('')
  const [showAccountForm, setShowAccountForm] = useState(false)
  const [showListingForm, setShowListingForm] = useState(false)
  const [listingForm, setListingForm] = useState({ title: '', description: '', price_amount: '', currency: 'USD' })
  const [busy, setBusy] = useState(false)

  const loadDashboard = useCallback(async () => {
    const [myProfile, myAccounts, myListings, myOrders] = await Promise.all([
      apiRequest('/users/me/seller-profile'), apiRequest('/users/me/accounts'),
      apiRequest('/listings/seller/mine'), apiRequest('/orders/seller/mine'),
    ])
    setProfile(myProfile)
    setAccounts(myAccounts)
    setListings(myListings)
    setOrders(myOrders)
    setSelectedAccount((current) => current || myAccounts[0]?.id || '')
    setState('ready')
  }, [])

  useEffect(() => {
    if (!isAuthenticated()) return
    let cancelled = false
    Promise.resolve().then(() => loadDashboard()).catch((err) => {
      if (!cancelled && err.message.includes('seller profile')) setState('setup')
      else if (!cancelled) { setError(err.message); setState('error') }
    })
    return () => { cancelled = true }
  }, [loadDashboard])

  async function createSellerProfile() {
    setBusy(true); setError('')
    try {
      const user = JSON.parse(localStorage.getItem('current_user') || '{}')
      await apiRequest('/users/me/seller-profile', { method: 'POST', body: JSON.stringify({ shop_name: `${user.display_name || 'My'} Squad Shop` }) })
      await loadDashboard()
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  async function submitAccount(event) {
    event.preventDefault(); setBusy(true); setError('')
    try {
      await apiRequest('/users/me/accounts', { method: 'POST', body: JSON.stringify({ ...accountForm, team_strength: Number(accountForm.team_strength), player_count: Number(accountForm.player_count), coin_balance: Number(accountForm.coin_balance || 0) }) })
      setAccountForm(emptyAccount); setShowAccountForm(false); await loadDashboard()
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  async function submitListing(event) {
    event.preventDefault(); setBusy(true); setError('')
    try {
      await apiRequest('/listings', { method: 'POST', body: JSON.stringify({ ...listingForm, account_id: selectedAccount, price_amount: Number(listingForm.price_amount) }) })
      setListingForm({ title: '', description: '', price_amount: '', currency: 'USD' }); setShowListingForm(false); await loadDashboard()
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  async function archiveListing(id) {
    setError('')
    try { await apiRequest(`/listings/${id}`, { method: 'DELETE' }); await loadDashboard() }
    catch (err) { setError(err.message) }
  }

  const metrics = [['Active listings', state === 'ready' ? String(listings.filter((item) => item.status === 'ACTIVE').length) : '—'], ['Orders', state === 'ready' ? String(orders.length) : '—'], ['Sales', state === 'ready' ? `${orders.filter((item) => item.status === 'COMPLETED').length}` : '—']]
  return <DashboardShell role="Seller" title="Seller overview" description={profile ? `Welcome, ${profile.shop_name}. Manage your listings and orders.` : 'Manage your listings and keep an eye on your sales.'} nav={[{ label: 'Overview', to: '/dashboard/seller' }, { label: 'Messages', to: '/messages' }, { label: 'Marketplace', to: '/marketplace' }]} metrics={metrics}>
    {state === 'signed-out' && <section className="panel"><div className="empty-state"><strong>Sign in to manage your seller account</strong><p>Log in or create an account to list your squad.</p><Link className="btn btn-primary" to="/login">Log in</Link></div></section>}
    {state === 'loading' && <section className="panel"><div className="loading-state">Loading seller dashboard…</div></section>}
    {state === 'setup' && <section className="panel"><div className="empty-state"><strong>Set up your seller profile</strong><p>Create your seller profile before adding eFootball accounts and listings.</p><button className="btn btn-primary" disabled={busy} onClick={createSellerProfile}>{busy ? 'Setting up…' : 'Become a seller'}</button></div></section>}
    {state === 'error' && <section className="panel"><div className="error-state" role="alert"><strong>Could not load seller dashboard</strong><p>{error}</p><button className="btn btn-secondary" onClick={() => loadDashboard().catch((err) => setError(err.message))}>Try again</button></div></section>}
    {state === 'ready' && <>
      {error && <div className="error-state" role="alert" style={{ marginBottom: 16 }}>{error}</div>}
      <section className="panel"><div className="section-heading" style={{ marginBottom: 14 }}><div><h2>Your listings</h2><p>New listings enter review before publication.</p></div><div className="nav-actions"><button className="btn btn-secondary" onClick={() => setShowAccountForm((value) => !value)}>Add account</button><button className="btn btn-primary" disabled={!accounts.length} onClick={() => setShowListingForm((value) => !value)}>Create listing</button></div></div>
        {showAccountForm && <form className="panel" onSubmit={submitAccount} style={{ marginBottom: 18 }}><h2>Add a game account</h2><div className="toolbar"><input className="field" required minLength="2" placeholder="Account title" value={accountForm.title} onChange={(e) => setAccountForm({ ...accountForm, title: e.target.value })} /><select className="field" value={accountForm.platform} onChange={(e) => setAccountForm({ ...accountForm, platform: e.target.value })}><option>PlayStation</option><option>Xbox</option><option>PC</option><option>iOS</option><option>Android</option></select></div><div className="toolbar"><input className="field" type="number" required min="0" placeholder="Team strength" value={accountForm.team_strength} onChange={(e) => setAccountForm({ ...accountForm, team_strength: e.target.value })} /><input className="field" type="number" required min="0" placeholder="Player count" value={accountForm.player_count} onChange={(e) => setAccountForm({ ...accountForm, player_count: e.target.value })} /><input className="field" type="number" min="0" placeholder="Coin balance" value={accountForm.coin_balance} onChange={(e) => setAccountForm({ ...accountForm, coin_balance: e.target.value })} /></div><button className="btn btn-primary" disabled={busy}>Save account</button></form>}
        {showListingForm && <form className="panel" onSubmit={submitListing} style={{ marginBottom: 18 }}><h2>New listing</h2><div className="form-field"><label htmlFor="seller-account">Game account</label><select id="seller-account" className="field" required value={selectedAccount} onChange={(e) => setSelectedAccount(e.target.value)}>{accounts.map((account) => <option key={account.id} value={account.id}>{account.title} · strength {account.team_strength}</option>)}</select></div><div className="form-field"><label htmlFor="listing-title">Listing title</label><input id="listing-title" className="field" required minLength="3" value={listingForm.title} onChange={(e) => setListingForm({ ...listingForm, title: e.target.value })} /></div><div className="form-field"><label htmlFor="listing-description">Description</label><textarea id="listing-description" className="field" rows="3" value={listingForm.description} onChange={(e) => setListingForm({ ...listingForm, description: e.target.value })} /></div><div className="toolbar"><input aria-label="Price" className="field" type="number" min="0.01" step="0.01" required value={listingForm.price_amount} onChange={(e) => setListingForm({ ...listingForm, price_amount: e.target.value })} /><select aria-label="Currency" className="field" value={listingForm.currency} onChange={(e) => setListingForm({ ...listingForm, currency: e.target.value })}><option>USD</option><option>EUR</option><option>GBP</option></select></div><button className="btn btn-primary" disabled={busy || !selectedAccount}>Submit for review</button></form>}
        {listings.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th>Listing</th><th>Price</th><th>Status</th><th>Strength</th><th /></tr></thead><tbody>{listings.map((listing) => <tr key={listing.id}><td><Link className="text-link" to={`/listings/${listing.id}`}>{listing.title}</Link></td><td>{listing.currency} {Number(listing.price_amount).toFixed(2)}</td><td><span className={`pill ${listing.status === 'PENDING_REVIEW' ? 'gold' : ''}`}>{listing.status.replaceAll('_', ' ')}</span></td><td>{listing.team_strength}</td><td>{!['SOLD', 'RESERVED', 'ARCHIVED'].includes(listing.status) && <button className="btn btn-quiet" onClick={() => archiveListing(listing.id)}>Archive</button>}</td></tr>)}</tbody></table></div> : <div className="empty-state"><strong>No listings yet</strong><p>Add an account, then submit it as a listing for review.</p><button className="btn btn-primary" onClick={() => setShowAccountForm(true)}>Add your first account</button></div>}
      </section>
      <section className="panel" style={{ marginTop: 20 }}><h2>Recent orders</h2>{orders.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th>Order</th><th>Total</th><th>Status</th><th>Date</th></tr></thead><tbody>{orders.map((order) => <tr key={order.id}><td><Link className="text-link" to={`/dashboard/buyer/orders/${order.id}`}>{order.id.slice(0, 8)}</Link></td><td>{order.currency} {Number(order.total_amount).toFixed(2)}</td><td><span className="pill">{order.status.replaceAll('_', ' ')}</span></td><td>{new Date(order.created_at).toLocaleDateString()}</td></tr>)}</tbody></table></div> : <div className="empty-state"><strong>No orders yet</strong><p>Orders for your listings will appear here.</p></div>}</section>
    </>}
  </DashboardShell>
}
