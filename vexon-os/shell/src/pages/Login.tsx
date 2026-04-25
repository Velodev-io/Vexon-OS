import { type FormEvent, useEffect, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { LockKeyhole } from 'lucide-react'
import { isLoggedIn, loginBypass } from '../lib/auth'

const Login = () => {
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setError(null)
  }, [password])

  if (isLoggedIn()) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (loading) {
      return
    }

    setLoading(true)
    setError(null)
    try {
      // BYPASS AUTH - commenting out actual login
      // await login(password)
      await loginBypass()
      navigate('/', { replace: true })
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex items-center justify-center px-6">
      <div className="w-full max-w-md rounded-[28px] glass glow border border-white/10 p-8 space-y-8">
        <div className="space-y-4 text-center">
          <div className="mx-auto w-14 h-14 rounded-2xl bg-white text-black flex items-center justify-center">
            <LockKeyhole size={24} />
          </div>
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">Enter Vexon OS</h1>
            <p className="text-sm text-white/45 mt-2">Local access only. Your session stays on this machine.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="password" className="text-xs uppercase tracking-[0.2em] text-white/35 font-semibold">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-2xl bg-white/[0.04] border border-white/10 px-4 py-4 text-white outline-none focus:border-white/30 focus:bg-white/[0.06]"
              placeholder="Enter anything (auth bypassed)"
              autoFocus
            />
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-2xl bg-white text-black py-4 font-semibold transition hover:opacity-90 disabled:opacity-40"
          >
            {loading ? 'Unlocking...' : 'Unlock Workspace'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
