import { Link } from 'react-router-dom'

export default function ListingCard({ item }) {
  const listingId = item.id
  const name = item.name || item.title
  const rating = item.rating ?? item.team_strength
  const price = item.price ?? item.price_amount
  return (
    <Link to={`/listings/${listingId}`} className="listing-card" style={{ color: 'inherit', textDecoration: 'none' }}>
      <div className={`listing-art ${item.tone}`}>
        <span className="listing-badge">{item.badge}</span>
        <div className="listing-rating"><strong>{rating}</strong><span>TEAM STRENGTH</span></div>
      </div>
      <div className="listing-body">
        <h3>{name}</h3>
        <div className="listing-meta"><span>⚽ {item.players} players</span><span>★ {item.coins} coins</span></div>
        <div className="listing-bottom"><span className="listing-price">${Number(price).toFixed(2)}</span><span className="rating">{item.currency || 'USD'} · {item.status || item.badge}</span></div>
      </div>
    </Link>
  )
}
