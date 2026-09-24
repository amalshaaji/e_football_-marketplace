import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import ListingCard from '../components/ListingCard.jsx'
import { PageContainer } from '../components/SiteLayout.jsx'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function MarketplacePage() {
  const [params, setParams] = useSearchParams()
  const [result, setResult] = useState({ items: [], total: 0, page: 1, page_size: 24 })
  const [state, setState] = useState('loading')
  const [retry, setRetry] = useState(0)
  const query = params.get('q') || ''
  const sort = params.get('sort') || 'newest'
  const page = Number(params.get('page') || 1)
  const minPrice = params.get('min_price') || ''
  const maxPrice = params.get('max_price') || ''

  useEffect(() => {
    const request = new URL(`${API_URL}/api/v1/listings`)
    for (const [key, value] of params.entries()) request.searchParams.set(key, value)
    if (!request.searchParams.has('page_size')) request.searchParams.set('page_size', '24')
    let cancelled = false
    fetch(request).then(async (response) => {
      if (!response.ok) throw new Error(`Marketplace request failed (${response.status})`)
      return response.json()
    }).then((data) => {
      if (!cancelled) { setResult(data); setState('ready') }
    }).catch(() => { if (!cancelled) setState('error') })
    return () => { cancelled = true }
  }, [params, retry])

  function updateParam(key, value) {
    setParams((current) => {
      const next = new URLSearchParams(current)
      if (value) next.set(key, value)
      else next.delete(key)
      next.delete('page')
      return next
    })
  }

  return <PageContainer>
    <div className="page-heading"><span className="eyebrow">Find your next squad</span><h1>Marketplace</h1><p>Explore community-listed eFootball accounts.</p></div>
    <div className="toolbar"><input className="field" type="search" value={query} onChange={(event) => updateParam('q', event.target.value)} placeholder="Search teams…" aria-label="Search teams" /><input className="field" type="number" min="0" value={minPrice} onChange={(event) => updateParam('min_price', event.target.value)} placeholder="Min price" aria-label="Minimum price" /><input className="field" type="number" min="0" value={maxPrice} onChange={(event) => updateParam('max_price', event.target.value)} placeholder="Max price" aria-label="Maximum price" /><select className="field" value={sort} onChange={(event) => updateParam('sort', event.target.value)} aria-label="Sort listings"><option value="newest">Newest</option><option value="price_asc">Price: low to high</option><option value="price_desc">Price: high to low</option><option value="strength_desc">Team strength</option></select></div>
    <p style={{ color: 'var(--muted)', fontSize: 13 }}>{result.total} account{result.total === 1 ? '' : 's'}</p>
    {state === 'loading' && <div className="loading-state" role="status">Loading marketplace…</div>}
    {state === 'error' && <div className="error-state" role="alert"><strong>Marketplace is unavailable</strong><p>Check your connection and try again.</p><button className="btn btn-secondary" onClick={() => setRetry((value) => value + 1)}>Try again</button></div>}
    {state === 'ready' && !result.items.length && <div className="empty-state"><strong>No accounts found</strong><p>Try different search or price filters.</p></div>}
    {state === 'ready' && result.items.length > 0 && <><div className="listing-grid">{result.items.map((item) => <ListingCard key={item.id} item={item} />)}</div><div className="hero-actions" style={{ justifyContent: 'center' }}><button className="btn btn-secondary" disabled={page <= 1} onClick={() => updateParam('page', String(page - 1))}>Previous</button><span style={{ alignSelf: 'center', color: 'var(--muted)' }}>Page {page} of {Math.max(1, Math.ceil(result.total / result.page_size))}</span><button className="btn btn-secondary" disabled={page * result.page_size >= result.total} onClick={() => updateParam('page', String(page + 1))}>Next</button></div></>}
  </PageContainer>
}
