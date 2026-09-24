import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ListingCard from '../components/ListingCard.jsx'
import { PageContainer } from '../components/SiteLayout.jsx'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const listings = [
  { id: 'elite', name: 'Elite Legends XI', rating: 3120, players: 28, coins: '1.2M', price: 189, stars: '4.9', reviews: 24, badge: 'Top rated', tone: '', },
  { id: 'classic', name: 'Classic Champions', rating: 2980, players: 31, coins: '850K', price: 145, stars: '4.8', reviews: 18, badge: 'Great value', tone: 'gold' },
  { id: 'rising', name: 'Rising Stars FC', rating: 3050, players: 26, coins: '640K', price: 119, stars: '5.0', reviews: 12, badge: 'New listing', tone: 'blue' },
]

export default function HomePage() {
  const [health, setHealth] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    fetch(`${API_URL}/health`).then(async (response) => {
      if (!response.ok) throw new Error(`Health check failed (${response.status})`)
      return response.json()
    }).then(setHealth).catch((err) => setError(err.message))
  }, [])

  return <>
    <section className="hero"><div className="container hero-grid">
      <div><span className="eyebrow">The eFootball account marketplace</span><h1>Your next dream team is waiting.</h1><p className="hero-copy">Find a squad that fits your style. Explore carefully curated eFootball accounts from a community of passionate players.</p><div className="hero-actions"><Link to="/marketplace" className="btn btn-primary">Explore accounts <span aria-hidden="true">→</span></Link><Link to="/register" className="btn btn-secondary">Start selling</Link></div></div>
      <div className="hero-art" aria-label="Abstract football pitch illustration"><div className="pitch"><span className="pitch-circle" /></div><div className="player-chip one"><strong>3120</strong>TEAM STRENGTH</div><div className="player-chip two"><strong>★ 4.9</strong>SELLER RATING</div></div>
    </div></section>
    <PageContainer>
      <section className="section" style={{ paddingBottom: 12 }}><div className="section-heading"><div><span className="eyebrow">A better way to trade</span><h2>Built around your game</h2></div><p>Clear details. Confident decisions.</p></div><div className="stats-grid"><article className="stat-card"><span className="stat-icon">◎</span><strong>Curated listings</strong><span>Every squad has the details you need.</span></article><article className="stat-card"><span className="stat-icon">♧</span><strong>Community sellers</strong><span>Find experienced sellers with a track record.</span></article><article className="stat-card"><span className="stat-icon">⌕</span><strong>Easy discovery</strong><span>Search by budget, team strength, and more.</span></article></div></section>
      <section className="section"><div className="section-heading"><div><span className="eyebrow">Hand-picked for you</span><h2>Featured accounts</h2></div><Link className="btn btn-quiet" to="/marketplace">View all accounts →</Link></div><div className="listing-grid">{listings.map((item) => <ListingCard key={item.id} item={item} />)}</div></section>
      <div className="status-card" style={{ padding: '13px 16px', marginBottom: 34, borderRadius: 12, color: 'var(--muted)', fontSize: 12 }}><strong style={{ color: 'var(--ink)' }}>API status · </strong>{health ? `${health.service} ${health.status} (${health.environment})` : error ? `Unavailable at ${API_URL}: ${error}` : 'Connecting to API…'}</div>
    </PageContainer>
  </>
}
