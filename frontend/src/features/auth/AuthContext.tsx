import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { loginRequest, logoutRequest, meRequest } from './api'
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '../../lib/axios'
import type { UserWithRole } from '../../types/user'
import type { Permissions } from '../../types/role'

interface AuthContextValue {
  user: UserWithRole | null
  permissions: Permissions
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  hasPermission: (module: string, action: string) => boolean
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserWithRole | null>(null)
  const [permissions, setPermissions] = useState<Permissions>({})
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function bootstrap() {
      if (!getAccessToken()) {
        setIsLoading(false)
        return
      }
      try {
        const me = await meRequest()
        setUser(me.user)
        setPermissions(me.permissions)
      } catch {
        clearTokens()
      } finally {
        setIsLoading(false)
      }
    }
    void bootstrap()
  }, [])

  async function login(email: string, password: string) {
    const data = await loginRequest(email, password)
    setTokens(data.access_token, data.refresh_token)
    const me = await meRequest()
    setUser(me.user)
    setPermissions(me.permissions)
  }

  async function logout() {
    const refreshToken = getRefreshToken()
    if (refreshToken) {
      try {
        await logoutRequest(refreshToken)
      } catch {
        // El token ya pudo haber expirado; no bloquea el logout local.
      }
    }
    clearTokens()
    setUser(null)
    setPermissions({})
  }

  function hasPermission(module: string, action: string): boolean {
    if (user?.is_superadmin) return true
    return permissions[module]?.includes(action) ?? false
  }

  return (
    <AuthContext.Provider value={{ user, permissions, isLoading, login, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth debe usarse dentro de <AuthProvider>')
  return ctx
}
