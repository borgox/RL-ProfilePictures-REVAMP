"use client";

import { useRef, useState, useEffect } from "react";
import { motion, useScroll, useTransform, useInView } from "framer-motion";
import { MessageCircle, Bug, Lightbulb, Heart, ExternalLink, Users, Shield, Zap } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useTranslations } from '../providers/TranslationProvider';

export default function Support() {
    const { translations } = useTranslations();
    const [serverStatus, setServerStatus] = useState<"online" | "offline" | "checking">("checking");

    if (!translations) return null; 
    useEffect(() => {
        const checkServerStatus = async () => {
            try {
                const response = await fetch("https://api.borgox.tech/", {
                    signal: AbortSignal.timeout(3000)
                });
                if (response.ok) {
                    const data = await response.json();
                    setServerStatus(data.status === "online" ? "online" : "offline");
                } else {
                    setServerStatus("offline");
                }
            } catch {
                setServerStatus("offline");
            }
        };

        checkServerStatus();
        const interval = setInterval(checkServerStatus, 60000);
        return () => clearInterval(interval);
    }, []);

    return (
        <section id="support" className="py-32 px-4 sm:px-6 lg:px-8 bg-black/20">
            <div className="max-w-4xl mx-auto text-center">
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="mb-12">
                    <h2 className="text-5xl sm:text-6xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        {translations.support.title}
                    </h2>
                    <p className="text-xl text-white/60 mb-8">
                        {translations.support.subtitle}
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-12">
                    {[
                        {
                            label: translations.support.buttons.joinDiscord,
                            color: "from-indigo-500 to-purple-500",
                            href: "https://discord.gg/g3ReJDCr2h"
                        },
                        {
                            label: translations.support.buttons.reportBug,
                            color: "from-red-500 to-pink-500",
                            href: "https://discord.gg/g3ReJDCr2h"
                        },
                        {
                            label: translations.support.buttons.suggestions,
                            color: "from-green-500 to-emerald-500",
                            href: "https://discord.gg/g3ReJDCr2h"
                        }
                    ].map((button, index) => (
                        <motion.a
                            key={index}
                            href={button.href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`block bg-gradient-to-r ${button.color} text-white font-semibold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105`}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            whileHover={{ y: -5, scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}>
                            {button.label}
                        </motion.a>
                    ))}
                </div>

                {/* Server Status */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="inline-block">
                    <Card className="bg-black/40 backdrop-blur-xl border border-white/20 rounded-2xl p-6">
                        <div className="flex items-center justify-center space-x-4">
                            <div className="flex items-center space-x-3">
                                <motion.div
                                    className={`w-4 h-4 rounded-full ${
                                        serverStatus === "online"
                                            ? "bg-green-400"
                                            : serverStatus === "offline"
                                              ? "bg-red-400"
                                              : "bg-yellow-400"
                                    }`}
                                    animate={{ scale: [1, 1.2, 1] }}
                                    transition={{ duration: 2, repeat: Infinity }}
                                />
                                <span className="text-white/60">Server Status:</span>
                                <span
                                    className={`font-semibold ${
                                        serverStatus === "online"
                                            ? "text-green-400"
                                            : serverStatus === "offline"
                                              ? "text-red-400"
                                              : "text-yellow-400"
                                    }`}>
                                    {serverStatus === "online"
                                        ? translations.support.serverStatus.online
                                        : serverStatus === "offline"
                                          ? translations.support.serverStatus.offline
                                          : translations.support.serverStatus.checking}
                                </span>
                            </div>
                            <div className="text-white/40">|</div>
                            <span className="text-white/60">{serverStatus === "online" ? translations.support.serverStatus.onlineMessage : serverStatus === "offline" ? translations.support.serverStatus.offlineMessage : translations.support.serverStatus.checkingMessage}</span>
                        </div>
                    </Card>
                </motion.div>

                {/* Discord Widget Section */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="mt-12 flex justify-center"
                >
                    <iframe 
                        src="https://discord.com/widget?id=1307557024921419866&theme=dark" 
                        width="350" 
                        height="500" 
                        allowtransparency="true" 
                        frameBorder="0" 
                        sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"
                        className="rounded-xl shadow-2xl border border-white/10"
                    ></iframe>
                </motion.div>
            </div>
        </section>
    );
}
