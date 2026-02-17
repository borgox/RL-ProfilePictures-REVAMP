import { Metadata } from 'next'
import RLPFPLandingPage from './components/RLPFPLandingPage'

// Default metadata (English)
export const metadata: Metadata = {
  title: 'RLProfilePicturesREVAMP - Custom Rocket League Avatars',
  description: 'RLProfilePicturesREVAMP lets Epic Games users set custom profile pictures in Rocket League and view cross‑platform avatars. Easy install, configurable, and free.',
  keywords: ['Rocket League', 'Bakkesmod', 'Epic Games', 'profile pictures', 'avatars', 'plugin', 'RLProfilePicturesREVAMP'],
  authors: [{ name: 'borgox' }],
  creator: 'borgox',
  publisher: 'borgox',
  alternates: {
    canonical: 'https://rlpfp.borgox.tech',
  },
  openGraph: {
    title: 'RLProfilePicturesREVAMP - Custom Rocket League Avatars',
    description: 'Upload a custom Epic avatar and see Steam/console avatars in Rocket League with Bakkesmod.',
    type: 'website',
    url: 'https://rlpfp.borgox.tech/',
    siteName: 'RLProfilePicturesREVAMP',
    locale: 'en_US',
    images: [
      {
        url: '/assets/plugin_ingame.png',
        width: 1200,
        height: 630,
        alt: 'RLProfilePicturesREVAMP In-Game Screenshot',
        type: 'image/png',
      }
    ]
  },
  twitter: {
    card: 'summary_large_image',
    title: 'RLProfilePicturesREVAMP - Custom Rocket League Avatars',
    description: 'Upload a custom Epic avatar and see Steam/console avatars in Rocket League with Bakkesmod.',
    creator: '@borgox',
    images: {
      url: '/assets/plugin_ingame.png',
      alt: 'RLProfilePicturesREVAMP In-Game Screenshot',
    },
  },
  robots: {
    index: true,
    follow: true,
  },
  other: {
    'theme-color': '#6366f1'
  }
}

export default function RLPFPPage() {
  return <RLPFPLandingPage />
}
