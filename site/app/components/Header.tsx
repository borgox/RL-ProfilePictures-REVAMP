'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X } from 'lucide-react'
import LanguageSelector from './LanguageSelector'

const navigation = [
  { name: 'Download', href: '#download' },
  { name: 'Features', href: '#features' },
  { name: 'Installation', href: '#installation' },
  { name: 'FAQ', href: '#faq' },
  { name: 'Support', href: '#support' },
  { name: 'Donate', href: '#donate' },
]

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (href: string) => {
    try {
      const target = document.querySelector(href)
      if (target) {
        const headerHeight = 110; // Same offset as above
        const elementPosition = target.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = elementPosition - headerHeight;
        
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
        setMobileMenuOpen(false)
      } else {
        // If target not found immediately, try again after a short delay
        setTimeout(() => {
          try {
            const retryTarget = document.querySelector(href);
            if (retryTarget) {
              const headerHeight = 110;
              const elementPosition = retryTarget.getBoundingClientRect().top + window.pageYOffset;
              const offsetPosition = elementPosition - headerHeight;
              
              window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
              });
              setMobileMenuOpen(false);
            }
          } catch (error) {
            console.warn('Invalid selector on retry:', href);
          }
        }, 100);
      }
    } catch (error) {
      console.warn('Invalid selector:', href);
    }
  }

  return (
    <motion.header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled 
          ? 'bg-slate-900/95 backdrop-blur-xl border-b border-purple-500/20 shadow-2xl' 
          : mobileMenuOpen
            ? 'backdrop-blur-md border-b border-purple-500/20 shadow-2xl'
            : 'bg-transparent border-b border-transparent shadow-none'
      }`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <div className="mx-auto max-w-7xl px-2 xs:px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between min-w-0">
          {/* Logo */}
          <motion.div
            className="flex items-center flex-shrink-0 min-w-0" 
          >
            <h1 className="text-base xs:text-lg sm:text-xl font-bold bg-gradient-to-r from-purple-400 via-blue-400 to-purple-600 bg-clip-text text-transparent transition-shadow duration-200 truncate">
              <span className="hidden sm:inline">RLProfilePicturesREVAMP</span>
              <span className="sm:hidden">RLPFP</span>
            </h1>
          </motion.div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-4 lg:space-x-8 flex-shrink-0">
            {navigation.map((item, index) => (
              <motion.button
                key={item.name}
                onClick={() => scrollToSection(item.href)}
                className="text-gray-300 hover:text-white transition-colors duration-200 font-medium relative group whitespace-nowrap text-sm lg:text-base"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                {item.name}
                <span className="absolute inset-x-0 -bottom-1 h-0.5 bg-gradient-to-r from-purple-400 to-blue-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-200" />
              </motion.button>
            ))}
          </nav>

          {/* Right side buttons */}
          <div className="flex items-center space-x-1 xs:space-x-2 sm:space-x-4 flex-shrink-0"> 
            <div className="hidden xs:block">
              <LanguageSelector />
            </div>

            {/* Mobile menu button */}
            <motion.button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-1.5 xs:p-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              {mobileMenuOpen ? (
                <X className="h-4 w-4 xs:h-5 xs:w-5 sm:h-6 sm:w-6 text-white" />
              ) : (
                <Menu className="h-4 w-4 xs:h-5 xs:w-5 sm:h-6 sm:w-6 text-white" />
              )}
            </motion.button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            className="md:hidden backdrop-blur-md border-b border-purple-500/20"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="px-4 py-6 space-y-4">
              {navigation.map((item, index) => (
                <motion.button
                  key={item.name}
                  onClick={() => scrollToSection(item.href)}
                  className="block w-full text-left text-gray-300 hover:text-white transition-colors duration-200 font-medium py-2"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  {item.name}
                </motion.button>
              ))}
              
              {/* Mobile Language Selector */}
              <motion.div
                className="pt-4 border-t border-white/10"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: navigation.length * 0.1 }}
              >
                <LanguageSelector />
              </motion.div>
       
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  )
}