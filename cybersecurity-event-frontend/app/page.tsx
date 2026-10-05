'use client'

import { useEffect, useState } from 'react'
import EleventhDayPage from './EleventhDayPage'

export default function RootPage() {
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted) {
    return null // or a loading spinner
  }

  return <EleventhDayPage />
}
