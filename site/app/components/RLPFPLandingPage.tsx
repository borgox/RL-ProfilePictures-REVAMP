"use client";

import { useState, useEffect, useRef } from "react"; 
import {
    Heart,
    ArrowUp,
    ExternalLink,
} from "lucide-react"; 
import { motion, AnimatePresence, useScroll, useTransform } from "framer-motion";
import "../rlpfp-styles.css";

import ParticleBackground from "./ParticleBackground";
import Header from "./Header";
import Hero from "./Hero";
import Features from "./Features";
import HowItWorks from "./HowItWorks";
import Screenshots from "./Screenshots";
import WhatPlayersSays from "./WhatPlayersSays";
import Installation from "./Installation";
import FAQ from "./FAQ";
import Changelog from "./Changelog";
import Support from "./Support";
import { TranslationProvider, useTranslations } from "../providers/TranslationProvider";

interface ParticleProps {
    id: number;
    x: number;
    y: number;
    vx: number;
    vy: number;
    size: number;
    color: string;
    life: number;
}
 
function RLPFPLandingPageContent() {
    const [isLoading, setIsLoading] = useState(true); 
    const [scrollProgress, setScrollProgress] = useState(0); 
    const [showBackToTop, setShowBackToTop] = useState(false);
    const { translations, isLoading: translationsLoading } = useTranslations(); 
 
    useEffect(() => {
        const timer = setTimeout(() => setIsLoading(false), 1500);
        return () => clearTimeout(timer);
    }, []);
    
    useEffect(() => {
        const handleScroll = () => {
            const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = Math.min((window.scrollY / totalHeight) * 100, 100);
            setScrollProgress(progress);
            setShowBackToTop(window.scrollY > 400);
        };

        window.addEventListener("scroll", handleScroll, { passive: true });
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    useEffect(() => {
            if (!isLoading && !translationsLoading && translations) {
                const hash = window.location.hash;
                if (hash) {
                    const tryScroll = () => {
                        let targetSelector = hash;
                        
                        // Handle version changelog hashes - convert dots to dashes
                        if (hash.startsWith('#v-') && hash.includes('.')) {
                            targetSelector = hash.replace(/\./g, '-');
                        }
                        
                        try {
                            const element = document.querySelector(targetSelector);
                            if (element) {
                                // Calculate offset for fixed header
                                const headerHeight = 110; // Adjust based on your header height
                                const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
                                const offsetPosition = elementPosition - headerHeight;
                                
                                window.scrollTo({
                                    top: offsetPosition,
                                    behavior: 'smooth'
                                });
                                return true;
                            }
                        } catch (error) {
                            console.warn('Invalid hash selector:', hash);
                        }
                        return false;
                    };

                    // Try immediately
                    if (!tryScroll()) {
                        // Retry a few times until React finishes rendering
                        let attempts = 0;
                        const interval = setInterval(() => {
                            attempts++;
                            if (tryScroll() || attempts > 10) {
                                clearInterval(interval);
                            }
                        }, 200);
                    }
                }
            }
        }, [isLoading, translationsLoading, translations]);

 

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

  
    if (isLoading || translationsLoading || !translations) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center relative overflow-hidden">
 
                <div className="absolute inset-0">
                    {[...Array(20)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="absolute w-2 h-2 bg-purple-500/30 rounded-full"
                            animate={{
                                x: [
                                    Math.random() * (typeof window !== "undefined" ? window.innerWidth : 1920),
                                    Math.random() * (typeof window !== "undefined" ? window.innerWidth : 1920)
                                ],
                                y: [
                                    Math.random() * (typeof window !== "undefined" ? window.innerHeight : 1080),
                                    Math.random() * (typeof window !== "undefined" ? window.innerHeight : 1080)
                                ],
                                scale: [0, 1, 0],
                                opacity: [0, 0.6, 0]
                            }}
                            transition={{
                                duration: 4 + Math.random() * 4,
                                repeat: Infinity,
                                delay: Math.random() * 2
                            }}
                        />
                    ))}
                </div>

                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                    className="text-center space-y-8 relative z-10"> 
                 
                        <div className="flex justify-center space-x-2">
                            {[0, 1, 2].map((i) => (
                                <motion.div
                                    key={i}
                                    className="w-3 h-3 bg-purple-500 rounded-full"
                                    animate={{
                                        y: [-8, 8, -8],
                                        opacity: [0.3, 1, 0.3],
                                        scale: [0.8, 1.2, 0.8]
                                    }}
                                    transition={{
                                        duration: 1.5,
                                        repeat: Infinity,
                                        delay: i * 0.2,
                                        ease: "easeInOut"
                                    }}
                                />
                            ))}
                        </div>


                    <div className="space-y-4">
                        <motion.h2
                            className="text-white text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent"
                            animate={{
                                backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"]
                            }}
                            transition={{
                                duration: 3,
                                repeat: Infinity
                            }}
                            style={{ backgroundSize: "200% 200%" }}>
                            {translations?.loading.title || "Loading RLProfilePicturesREVAMP"}
                        </motion.h2> 
                        <div className="w-64 h-1 bg-gray-800 rounded-full mx-auto overflow-hidden">
                            <motion.div
                                className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                                initial={{ width: 0 }}
                                animate={{ width: "100%" }}
                                transition={{ duration: 1.5, ease: "easeInOut" }}
                            />
                        </div>

                    </div>
                </motion.div>
            </div>
        );
    }
 
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white relative overflow-x-hidden">
            <ParticleBackground /> 
            <motion.div
                className="fixed top-0 left-0 h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 z-50 shadow-lg shadow-purple-500/50"
                style={{ width: `${scrollProgress}%` }}
                initial={{ width: 0 }}
                animate={{ width: `${scrollProgress}%` }}
                transition={{ ease: "easeOut", duration: 0.2 }}
            />

            <Header />
            {/* Main Content */}
            <main className="relative z-10"> 
                {/* Hero Section */}
                <Hero />    
                {/* Features Section */}
                <Features />
                {/* How It Works Section */}
                <HowItWorks />
                {/* Screenshots Section */}
                <Screenshots />  
                {/* Testimonials Section */}
                <WhatPlayersSays />
                {/* Installation Guide */}
                <Installation />
                {/* FAQ Section */}
                <FAQ/>
                {/* Changelog Section */}
                <Changelog />
                {/* Support Section */}
                <Support />
                {/* Donation Section */}
                <section className="py-32 px-4 sm:px-6 lg:px-8" id="donate">
                    <div className="max-w-4xl mx-auto text-center">
                        <motion.div
                            initial={{ opacity: 0, y: 50 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8 }}
                            className="space-y-8">
                            <div className="space-y-6">
                                <h2 className="text-5xl sm:text-6xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent">
                                    {translations.donation.title}
                                </h2>
                                <div className="space-y-4 max-w-2xl mx-auto">
                                    <p className="text-xl text-white/80">
                                        {translations.donation.description}
                                    </p>
                                    <p className="text-lg text-white/60">
                                        {translations.donation.subtitle}
                                    </p>
                                </div>
                            </div>

                            <motion.a
                                href="https://paypal.me/BornzGenZ"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-block relative group"
                                whileHover={{ scale: 1.05, y: -5 }}
                                whileTap={{ scale: 0.95 }}>
                                <div className="absolute -inset-2 bg-gradient-to-r from-pink-500 via-red-500 to-orange-500 rounded-2xl blur-xl opacity-60 group-hover:opacity-100 transition-opacity duration-500" />

                                <div className="relative bg-gradient-to-r from-pink-600 to-orange-600 text-white font-bold py-6 px-12 rounded-xl text-xl shadow-2xl flex items-center space-x-3">
                                    <Heart className="w-7 h-7" />
                                    <span>{translations.donation.button}</span>
                                    <ExternalLink className="w-5 h-5" />
                                </div>
                            </motion.a>
                        </motion.div>
                    </div>
                </section>

                {/* Footer */}
                <footer className="border-t border-white/10 bg-black/20 py-12 px-4 sm:px-6 lg:px-8">
                    <div className="max-w-6xl mx-auto text-center">
                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8 }}
                            className="space-y-4">
                          <div>
                              <p className="text-white/60">{translations.footer.copyright}</p>
                            <p className="text-white/60">
                                {translations.footer.websiteBy} <a href="https://exelvi.xyz/" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:text-purple-300 transition-colors">EXELVI</a>
                            </p>
                          </div>
                            <div className="flex justify-center space-x-8">
                                <a
                                    href="https://api.borgox.tech/privacy"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-purple-400 hover:text-purple-300 transition-colors">
                                    {translations.footer.privacyPolicy}
                                </a>
                                <a
                                    href="https://api.borgox.tech/tos"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-purple-400 hover:text-purple-300 transition-colors">
                                    {translations.footer.termsOfService}
                                </a>
                            </div>
                        </motion.div>
                    </div>
                </footer>
            </main>

            {/* Back to top button  */}
            <AnimatePresence>
                {showBackToTop && (
                    <motion.button
                        onClick={scrollToTop}
                        className="fixed bottom-6 right-6 bg-gradient-to-r from-purple-500 to-pink-500 text-white p-4 rounded-full shadow-lg hover:shadow-xl z-40 backdrop-blur-sm border border-white/10"
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        exit={{ scale: 0, rotate: 180 }}
                        whileHover={{ scale: 1.1, y: -5 }}
                        whileTap={{ scale: 0.9 }}
                        transition={{ type: "spring", stiffness: 400, damping: 10 }}>
                        <ArrowUp className="w-6 h-6" aria-label={translations.backToTop} />
                    </motion.button>
                )}
            </AnimatePresence>
        </div>
    );
}

export default function RLPFPLandingPage() {
    return (
        <div className="dark">
            <TranslationProvider>
                <RLPFPLandingPageContent />
            </TranslationProvider>
        </div>
    );
}
