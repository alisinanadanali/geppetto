import { useTranslation } from 'react-i18next'

// Kabuk (sol modül rayı, üst bant) bölüm 7.4'te gelir. Sabit metin yok (ADR-0010).
function App() {
  const { t } = useTranslation()
  return (
    <main>
      <h1>{t('app.name')}</h1>
      <p>{t('app.tagline')}</p>
      <p>{t('status.skeleton')}</p>
    </main>
  )
}

export default App
