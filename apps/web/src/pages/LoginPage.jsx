import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import FormShell from '../components/FormShell.jsx'
import { apiRequest } from '../lib/api.js'

export default function LoginPage() {
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setBusy(true)
    const form = new FormData(event.currentTarget)
    try {
      const result = await apiRequest('/auth/login', { method: 'POST', body: JSON.stringify({ email: form.get('email'), password: form.get('password') }) })
      localStorage.setItem('access_token', result.access_token)
      localStorage.setItem('refresh_token', result.refresh_token)
      localStorage.setItem('current_user', JSON.stringify(result.user))
      navigate(result.user.role === 'ADMIN' ? '/dashboard/admin' : result.user.role === 'SELLER' ? '/dashboard/seller' : '/dashboard/buyer')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <FormShell onSubmit={handleSubmit} title="Welcome back" intro="Log in to continue to your marketplace account." footer={<>New to the marketplace? <Link className="text-link" to="/register">Create an account</Link></>}>
    {error && <div className="error-state" role="alert">{error}</div>}
    <div className="form-field"><label htmlFor="email">Email address</label><input id="email" name="email" type="email" placeholder="you@example.com" autoComplete="email" required /></div>
    <div className="form-field"><label htmlFor="password">Password</label><input id="password" name="password" type="password" placeholder="Enter your password" autoComplete="current-password" required /></div>
    <div className="form-links"><label><input type="checkbox" /> Remember me</label><a href="#forgot-password">Forgot password?</a></div>
    <button className="btn btn-primary btn-block" type="submit" disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
  </FormShell>
}
