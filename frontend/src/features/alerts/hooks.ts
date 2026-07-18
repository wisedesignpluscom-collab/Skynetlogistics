import { useCallback, useEffect, useState } from 'react'
import { getUnreadAlertCount } from './api'

export function useUnreadAlertCount() {
  const [count, setCount] = useState(0)

  const reload = useCallback(() => {
    void getUnreadAlertCount()
      .then(setCount)
      .catch(() => {})
  }, [])

  useEffect(() => {
    reload()
  }, [reload])

  return { count, reload }
}
