"use client";

import { useRef, useEffect, useState } from "react";
import { motion, useScroll, useTransform, useSpring, AnimatePresence } from "framer-motion";
import { Check, Copy, Download, Play, Star, Users, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere, MeshDistortMaterial, OrbitControls, Float } from "@react-three/drei";
import * as THREE from "three";
import { useTranslations } from "../providers/TranslationProvider";
 
function FloatingSphere() {
    const meshRef = useRef<THREE.Mesh>(null);

    useFrame((state) => {
        if (meshRef.current) {
            meshRef.current.rotation.x = Math.sin(state.clock.elapsedTime) * 0.3;
            meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.5;
        }
    });

    return (
        <Float speed={1.4} rotationIntensity={1} floatIntensity={2}>
            <Sphere ref={meshRef} args={[1, 100, 200]} scale={2.4}>
                <MeshDistortMaterial
                    color="#6366f1"
                    attach="material"
                    distort={0.5}
                    speed={2}
                    roughness={0.4}
                    metalness={0.8}
                />
            </Sphere>
        </Float>
    );
}

export default function Hero() {
    const { translations } = useTranslations();
    const containerRef = useRef<HTMLDivElement>(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start start", "end start"]
    });

    if (!translations) return null;

    const fadeInUp = {
        initial: { opacity: 0, y: 60 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] }
    };

    const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
    const opacity = useTransform(scrollYProgress, [0, 1], [1, 0]);
    const scale = useTransform(scrollYProgress, [0, 1], [1, 0.8]);

    const springConfig = { stiffness: 100, damping: 30, restDelta: 0.001 };
    const scaleSpring = useSpring(scale, springConfig);

    const [checksumCopied, setChecksumCopied] = useState(false);
    const [checksum, setChecksum] = useState<string>("Loading...");
 
    useEffect(() => {
        const fetchChecksum = async () => {
            try {
                const response = await fetch("/download/RLProfilePicturesREVAMP-1.1.2.zip.sha256");
                if (response.ok) {
                    const text = await response.text();
                    const hash = text.trim().split(/\s+/)[0];
                    if (/^[a-f0-9]{64}$/i.test(hash)) {
                        setChecksum(hash.toLowerCase());
                    } else {
                        setChecksum("Unavailable");
                    }
                } else {
                    setChecksum("Unavailable");
                }
            } catch {
                setChecksum("Unavailable");
            }
        };
        fetchChecksum();
    }, []);

    const copyChecksum = async () => {
        if (checksum && checksum !== "Loading..." && checksum !== "Unavailable") {
            try {
                await navigator.clipboard.writeText(checksum);
                setChecksumCopied(true);
                setTimeout(() => setChecksumCopied(false), 2000);
            } catch (error) {
                console.error("Failed to copy checksum:", error);
            }
        }
    };

    return (
        <motion.section
            ref={containerRef}
            className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16"
            style={{ y, opacity, scale: scaleSpring }}>
            {/* 3D Background */}
            <div className="absolute inset-0 z-0">
                <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
                    <ambientLight intensity={0.5} />
                    <pointLight position={[10, 10, 10]} />
                    <FloatingSphere />
                    <OrbitControls enableZoom={false} enablePan={false} enableRotate={false} />
                </Canvas>
            </div>

            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-slate-900/70 via-purple-900/50 to-slate-900/70 z-10" />

            {/* Content */}
            <div className="relative z-20 text-center px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
                {/* Main Title */}
                <motion.div
                    className="mb-8"
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2 }}>
                    <motion.h1
                        className="text-4xl sm:text-6xl lg:text-8xl font-black leading-tight mb-6"
                        initial={{ opacity: 0, y: 100, scale: 0.8 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}>
                        <motion.span
                            className="block bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent"
                            animate={{
                                backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"]
                            }}
                            transition={{
                                duration: 8,
                                repeat: Infinity,
                                ease: "linear"
                            }}
                            style={{
                                backgroundSize: "200% 200%"
                            }}>
                            {translations.hero.title}
                        </motion.span>
                        <motion.span
                            className="block text-2xl sm:text-4xl lg:text-6xl mt-4 text-white font-light"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.5, duration: 0.8 }}>
                            {translations.hero.subtitle}
                        </motion.span>
                    </motion.h1>

                     <motion.div variants={fadeInUp} className="space-y-4 max-w-4xl mx-auto">
                        <p className="text-xl sm:text-2xl text-white/90 font-medium leading-relaxed">
                            {translations.hero.descriptionBig}
                        </p>

                        <p className="text-lg text-white/70 leading-relaxed">
                            {translations.hero.description}
                        </p>
                    </motion.div>
                </motion.div>

                {/* Feature Highlights */}
                <motion.div
                    className="mb-12 space-y-4"
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.6 }}>
                    <div className="flex flex-wrap justify-center gap-6 text-lg text-gray-300">
                        <div className="flex items-center space-x-2">
                            <Zap className="h-6 w-6 text-yellow-400" />
                            <span>{translations.hero.features.customAvatars}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <Users className="h-6 w-6 text-blue-400" />
                            <span>{translations.hero.features.crossPlatform}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <Star className="h-6 w-6 text-purple-400" />
                            <span>{translations.hero.features.easyConfig}</span>
                        </div>
                    </div>
                </motion.div>

                {/* Download Section */}
                <motion.div
                    className="mb-12"
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.8 }}>
                    <div id="download" className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-6">
                        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                            <Button
                                size="lg"
                                  onClick={() => window.open('/download/RLProfilePicturesREVAMP-1.1.2.zip', '_blank')}
                                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-8 py-4 text-lg font-semibold rounded-xl shadow-2xl">
                                <Download className="mr-2 h-5 w-5" />
                                {translations.hero.downloadButton} v1.1.2
                            </Button>
                        </motion.div>

                        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                            <Button
                                variant="outline"
                                size="lg" 
                                onClick={() => {
                                    const tutorialSection = document.getElementById("tutorial-video");
                                    if (tutorialSection) {
                                        tutorialSection.scrollIntoView({ behavior: "smooth" });
                                    }
                                }}
                                className="border-purple-500 text-purple-400 hover:bg-purple-500 hover:text-white px-8 py-4 text-lg font-semibold rounded-xl">
                                <Play className="mr-2 h-5 w-5" />
                                {translations.hero.learnMoreButton}
                            </Button>
                        </motion.div>
                    </div>

                    {/* Checksum Display */}
                    <motion.div
                        className="max-w-2xl mx-auto bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-purple-500/20"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 1 }}>
                        <h3 className="text-sm font-medium text-gray-300 mb-3">{translations.hero.verifyDownload}</h3>
                        <div className="flex flex-col sm:flex-row gap-3">
                            <code className="flex-1 bg-slate-900/50 px-4 py-2 rounded-lg text-xs sm:text-sm text-purple-300 break-all">
                                {checksum}
                            </code>
                            <motion.button
                                className="px-3 py-2 text-sm border border-white/20 hover:bg-white/10 backdrop-blur-sm rounded-md text-white/80 hover:text-white transition-colors duration-200 flex items-center justify-center min-w-[60px]"
                                onClick={copyChecksum}
                                disabled={checksum === "Loading..." || checksum === "Unavailable"}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}>
                                <AnimatePresence mode="wait">
                                    {checksumCopied ? (
                                        <motion.div
                                            key="check"
                                            initial={{ scale: 0, rotate: -180 }}
                                            animate={{ scale: 1, rotate: 0 }}
                                            exit={{ scale: 0, rotate: 180 }}>
                                            <Check className="w-4 h-4 text-green-400" />
                                        </motion.div>
                                    ) : (
                                        <motion.div
                                            key="copy"
                                            initial={{ scale: 0, rotate: 180 }}
                                            animate={{ scale: 1, rotate: 0 }}
                                            exit={{ scale: 0, rotate: -180 }}>
                                            <Copy className="w-4 h-4" />
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </motion.button>
                        </div>
                    </motion.div>
                        <p className="text-sm text-gray-400 mt-2">
                        {translations.hero.optionalCheck}
                        </p>
                </motion.div>
            </div>

            {/* Scroll Indicator */}
            <motion.div
                className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 2, repeat: Infinity }}>
                <div className="w-6 h-10 border-2 border-purple-400 rounded-full flex justify-center">
                    <motion.div
                        className="w-1 h-3 bg-purple-400 rounded-full mt-2"
                        animate={{ y: [0, 12, 0] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    />
                </div>
            </motion.div>
        </motion.section>
    );
}
