import { Link, NavLink, Outlet } from 'react-router-dom'

export function SiteLayout() {
  return (
    <div className="app-shell">
      <header className="site-header">
        <Link to="/" className="brand"><span className="brand-mark">e</span>eFootball Market</Link>
        <nav aria-label="Main navigation">
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/marketplace">Marketplace</NavLink>
          <NavLink to="/dashboard/seller">Sell</NavLink>
        </nav>
        <div className="nav-actions">
          <Link className="btn btn-secondary" to="/login">Log in</Link>
          <Link className="btn btn-primary" to="/register">Get started</Link>
        </div>
      </header>
      <main className="page-content"><Outlet /></main>
      <footer className="site-footer"><div className="container footer-inner"><span>© 2026 eFootball Market</span><span>Built for the beautiful game.</span></div></footer>
    </div>
  )
}

export function PageContainer({ children, className = '' }) {
  return <div className={`container site-main ${className}`}>{children}</div>
}
