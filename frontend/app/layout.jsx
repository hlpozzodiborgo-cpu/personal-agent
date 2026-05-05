import './globals.css'

export const metadata = {
  title: 'Investor AI - Personal Financial Analyst',
  description: 'Votre analyste financier personnel pour suivre vos investissements',
}

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  )
}
