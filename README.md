# RLProfilePicturesREVAMP

> ⚠️ **Archive Notice**: This project is being open-sourced as a portfolio showcase. Due to Easy Anti-Cheat (EAC) integration in Rocket League, this mod is no longer functional. The codebase is provided for educational purposes and to demonstrate development skills.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Rocket League](https://img.shields.io/badge/Rocket%20League-Mod-orange)
![BakkesMod](https://img.shields.io/badge/BakkesMod-Plugin-green)

## 🎮 What is RLProfilePicturesREVAMP?

RLProfilePicturesREVAMP was a BakkesMod-using plugin that allowed Rocket League players to:

- **Set Custom Epic Avatars**: Epic Games users could upload and display custom profile pictures in-game
- **Cross-Platform Avatar Viewing**: See profile pictures from Steam, PlayStation, Xbox, and Nintendo Switch players
- **Configurable Settings**: Full control over avatar display preferences

## 📁 Project Structure

```
RLProfilePicturesREVAMP/
├── client/                 # C++ BakkesMod Plugin
│   └── RLProfilePicturesREVAMP/
│       ├── IMGUI/          # Dear ImGui for UI rendering
│       ├── RLSDK/          # Unofficial SDK Headers (thanks sslow)
│       ├── Memory/         # Memory reading utilities
│       └── ...
├── server/                 # Python FastAPI Backend
│   ├── routes/             # API endpoints
│   ├── services/           # Platform integrations
│   ├── cache/              # Caching layer
│   ├── database/           # Data persistence
│   └── ...
└── site/                   # Next.js Landing Page
    ├── app/                # Next.js App Router
    ├── components/         # React components
    └── ...
```

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Plugin** | C++17, BakkesMod SDK, RLSDK, Dear ImGui, DirectX 11 |
| **Backend** | Python 3.11+, FastAPI, Redis (caching) |
| **Website** | Next.js 14, React, TypeScript, Tailwind CSS |

## 🚀 Features

### Client Plugin
- Real-time avatar fetching and caching
- Memory pattern scanning for game data
- ImGui-based configuration interface
- Auto-update functionality
- Image brightness adjustment

### Backend API
- Multi-platform avatar resolution (Steam, Xbox, PSN, Switch, Epic)
- Rate limiting (40 req/min per IP)
- Response caching for performance
- Analytics and request tracking
- Custom Epic avatar uploads

### Website
- Internationalization (EN, IT, Venetian, Tuscan dialects for the meme 🤔)
- Download verification (SHA-256)
- Installation guides
- Changelog display

## 📖 Documentation

- [Client Plugin Documentation](./client/README.md)
- [Server API Documentation](./server/README.md)
- [Website Documentation](./site/README.md)

## 👥 Credits

- **[@borgox](https://github.com/borgox)** - Plugin development, backend, project lead
- **[@emiisu](https://github.com/ShinyEmii)** - RLSDK Help, Reverse Engineering
- **[@sslowdev](https://github.com/smallest-cock)** - RLSDK Updates, Setup Help, RLSDK Generator
- **[@exelvi](https://exelvi.xyz/)** - Website design and development
- **[Bakkesmod](https://discord.gg/jmzW3FYC)** - Discord server, Help with Bakkesmod SDK,  Introduction to black magic
- **[@hamter_rl](https://x.com/hamter_rl)** - Original plugin, Discord Server, Donations
- **[ItzBrank](https://github.com/ItsBrank) and [Feckless](https://www.unknowncheats.me/forum/unreal-engine-3-a/71911-thefeckless-ue3-sdk-generator.html)** - Original RLSDK Generator, UE3 SDK Generator
- **[Vinxzn](https://x.com/vinxznrl), f40** - Testing.
- **Atomic, Nazecham, Sun, Crimson (Uni/Swift)** - Player support
- **Huge thanks to every donator, I appreciate the support for the plugin ❤️**

## ⚖️ License

This project is open-sourced under the MIT License. See [LICENSE](./LICENSE) for details.

## ⚠️ Disclaimer

This project was designed for use with BakkesMod before Easy Anti-Cheat integration. It is no longer functional with current (or next) versions of Rocket League. The code is provided as-is for educational and portfolio purposes only.

---

*This project served thousands of Rocket League players, demonstrating practical experience in game modding, API development, and full-stack web development.*