import { Link } from 'react-router-dom'
import { PageContainer } from './SiteLayout.jsx'

export default function FormShell({ title, intro, children, footer, onSubmit }) {
  return <PageContainer><section className="form-wrap"><span className="eyebrow">Welcome to the market</span><h1>{title}</h1><p className="form-intro">{intro}</p><form onSubmit={onSubmit || ((event) => event.preventDefault())}>{children}</form>{footer && <p className="form-bottom">{footer}</p>}<p className="form-bottom"><Link className="text-link" to="/">Back to home</Link></p></section></PageContainer>
}
