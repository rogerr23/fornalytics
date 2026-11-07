import { useEffect } from 'react'

const APP = 'Fornalytics'

/** Browser tab title: "Page · Fornalytics" (or just the app name). */
export function useDocumentTitle(...parts: (string | null | undefined)[]) {
  const title = [...parts.filter(Boolean), APP].join(' · ')
  useEffect(() => {
    document.title = title
  }, [title])
}
