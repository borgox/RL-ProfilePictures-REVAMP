# RLProfilePicturesREVAMP - Website

> Next.js landing page for the RLProfilePicturesREVAMP plugin.

## 🎯 Overview

Modern, responsive landing page featuring:
- Plugin download with SHA-256 verification
- Multi-language support (EN, IT, regional dialects)
- Installation guides (automatic & manual)
- Changelog display
- Animated UI with Framer Motion

## 🏗️ Architecture

```
site/
├── app/
│   ├── page.tsx                    # Main landing page
│   ├── layout.tsx                  # Root layout
│   ├── components/
│   │   └── RLPFPLandingPage.tsx   # Main component
│   ├── locales/
│   │   ├── en.json                # English
│   │   ├── it.json                # Italian
│   │   ├── vec.json               # Venetian dialect
│   │   └── to.json                # Tuscan dialect
│   └── changelogs/
│       ├── 1.1.0.ts
│       └── 1.1.1.ts
├── public/
│   └── assets/                    # Images, downloads
├── components.json                # shadcn/ui config
├── tailwind.config.js
├── next.config.ts
└── package.json
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- pnpm (recommended)

### Installation

```bash
cd site

# Install dependencies
pnpm install

# Development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

## 🌐 Internationalization

Supported locales:

| Code | Language |
|------|----------|
| `en` | English (default) |
| `it` | Italian |
| `vec` | Venetian dialect |
| `to` | Tuscan dialect |

Translations are stored in `app/locales/*.json`.

## 🎨 UI Components

Built with:
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Animations
- **shadcn/ui** - Component library
- **Lucide Icons** - Icon set

## 📦 Key Features

### Download Section
- Direct plugin download
- SHA-256 hash verification
- Version display

### Installation Guides
- Automatic installation (batch script)
- Manual installation steps
- Security notes 

### Changelog
- Markdown-based changelogs
- Emoji support
- Version history

## 🔧 Configuration

### `next.config.ts`
```typescript
const nextConfig = {
  // Configuration options
};
```

### `tailwind.config.js`
```javascript
module.exports = {
  // Tailwind configuration
};
```

## 📄 Pages

| Route | Description |
|-------|-------------|
| `/` | Main landing page |


## 👥 Credits

- **Design & Development**: [@exelvi](https://exelvi.xyz/)
- **Project Lead**: [@borgox](https://github.com/borgox)

---

*Part of the RLProfilePicturesREVAMP project*