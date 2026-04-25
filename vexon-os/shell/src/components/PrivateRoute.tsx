import { Navigate, Outlet } from 'react-router-dom'
import { isLoggedIn } from '../lib/auth'

const PrivateRoute = () => {
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

export default PrivateRoute
