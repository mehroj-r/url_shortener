import { Download } from 'lucide-react'
import QRCode from 'qrcode'
import { useEffect, useState } from 'react'

import { SHORT_HOST, shortLink } from '../../lib/format'
import { Button, Code, Dialog } from '../ui'
import styles from './link.module.css'

const COLORS = { dark: '#1b1e23', light: '#ffffff' }

function download(href: string, filename: string) {
  const anchor = document.createElement('a')
  anchor.href = href
  anchor.download = filename
  anchor.click()
}

export function QrDialog({ code, onClose }: { code: string | null; onClose: () => void }) {
  const [png, setPng] = useState<string | null>(null)

  useEffect(() => {
    if (!code) return
    let cancelled = false
    QRCode.toDataURL(shortLink(code), { width: 640, margin: 2, color: COLORS, errorCorrectionLevel: 'M' }).then(
      (url) => !cancelled && setPng(url),
    )
    return () => {
      cancelled = true
      setPng(null)
    }
  }, [code])

  const saveSvg = async () => {
    if (!code) return
    const svg = await QRCode.toString(shortLink(code), { type: 'svg', margin: 2, color: COLORS })
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml' }))
    download(url, `${code}-qr.svg`)
    URL.revokeObjectURL(url)
  }

  return (
    <Dialog
      open={code !== null}
      onClose={onClose}
      title="QR code"
      width={420}
      footer={
        <>
          <Button onClick={saveSvg}>
            <Download size={15} aria-hidden /> SVG
          </Button>
          <Button variant="primary" disabled={!png} onClick={() => png && download(png, `${code}-qr.png`)}>
            <Download size={15} aria-hidden /> PNG
          </Button>
        </>
      }
    >
      <div className={styles.qr}>
        {png ? (
          <img src={png} alt={`QR code for ${SHORT_HOST}/${code}`} width={280} height={280} />
        ) : (
          <div className={styles.qrPlaceholder} aria-hidden />
        )}
        {code && <Code code={code} host />}
      </div>
    </Dialog>
  )
}
