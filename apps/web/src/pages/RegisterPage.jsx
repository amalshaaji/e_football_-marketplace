import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import FormShell from '../components/FormShell.jsx'
import { apiRequest } from '../lib/api.js'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function handleSubmit(event) {
    event.preventDefault(); setError(''); setBusy(true)
    const form = new FormData(event.currentTarget)
    try {
      const result = await apiRequest('/auth/register', { method: 'POST', body: JSON.stringify({ display_name: form.get('name'), email: form.get('email'), password: form.get('password') }) })
      localStorage.setItem('access_token', result.access_token)
      localStorage.setItem('refresh_token', result.refresh_token)
      localStorage.setItem('current_user', JSON.stringify(result.user))
      navigate('/dashboard/buyer')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <FormShell onSubmit={handleSubmit} title="Create your account" intro="Join the community to discover or list a squad." footer={<>Already have an account? <Link className="text-link" to="/login">Log in</Link></>}>
    {error && <div className="error-state" role="alert">{error}</div>}
    <div className="form-field"><label htmlFor="name">Display name</label><input id="name" name="name" type="text" placeholder="Your name" autoComplete="name" required /></div>
    <div className="form-field"><label htmlFor="email">Email address</label><input id="email" name="email" type="email" placeholder="you@example.com" autoComplete="email" required /></div>
    <div className="form-field"><label htmlFor="password">Password</label><input id="password" name="password" type="password" placeholder="At least 10 characters" autoComplete="new-password" minLength="10" required /></div>
    <button className="btn btn-primary btn-block" type="submit" disabled={busy}>{busy ? 'Creating account…' : 'Create account'}</button>
  </FormShell>
}
