'use client'

import { useRef } from 'react'
import { motion, useScroll, useTransform, useInView } from 'framer-motion'
import { Quote, Star, Heart } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { useTranslations } from '../providers/TranslationProvider'

type Player = {
  name: string;
  comment: string;
};

function PlayerCard({ player, index }: { player: Player; index: number }) {
  const cardRef = useRef<HTMLDivElement>(null)
  const isInView = useInView(cardRef, { once: true, margin: "-100px" })

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 50, rotateX: -15 }}
      animate={isInView ? { 
        opacity: 1, 
        y: 0, 
        rotateX: 0,
        transition: {
          duration: 0.6,
          delay: index * 0.2,
          ease: "easeOut"
        }
      } : {}}
      whileHover={{ 
        y: -10, 
        rotateX: 5,
        rotateY: 5,
        scale: 1.05,
        transition: { duration: 0.3 }
      }}
      className="group perspective-1000"
    >
      <Card className="relative h-full bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300 overflow-hidden">
        {/* BG Gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-blue-500/20 opacity-0 group-hover:opacity-10 transition-opacity duration-300" />
        
        {/* Floating Quote Icon */}
        <div className="absolute top-4 right-4 opacity-10 group-hover:opacity-20 transition-opacity duration-300">
          <Quote size={60} className="text-white" />
        </div>

        <div className="relative p-6 h-full flex flex-col">
          {/* Quote Icon */}
          <motion.div
            className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mb-4 shadow-lg"
            whileHover={{ 
              rotate: 360,
              scale: 1.1,
              transition: { duration: 0.5 }
            }}
          >
            <Quote className="w-6 h-6 text-white" />
          </motion.div>

          {/* Player Comment */}
          <div className="flex-1 mb-4">
            <blockquote className="text-lg text-gray-300 leading-relaxed group-hover:text-white transition-colors duration-300 italic">
              "{player.comment}"
            </blockquote>
          </div>

          {/* Player Name */}
          <div className="flex items-center">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-blue-400 flex items-center justify-center mr-3">
              <span className="text-white font-semibold text-sm">
                {player.name.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h4 className="text-white font-semibold group-hover:text-purple-300 transition-colors duration-300">
                {player.name}
              </h4> 
            </div>
          </div>

          {/* Hover Effect Border */}
          <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none shimmer-border" />
        </div>
      </Card>
    </motion.div>
  )
}

export default function WhatPlayersSays() {
  const { translations } = useTranslations();
  const sectionRef = useRef<HTMLDivElement>(null)

  if (!translations) return null;

  const players = translations.testimonials.players; // Bepi, Toni, Joani
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  })

  const y = useTransform(scrollYProgress, [0, 1], [100, -100])
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0])

  return (
    <motion.section
      ref={sectionRef}
      id="testimonials"
      className="py-24 relative overflow-hidden"
      style={{ opacity }}
    >
      {/* Background Elements */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-900/10 to-transparent" />
      
      <motion.div
        className="absolute top-20 left-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"
        style={{ y }}
      />
      <motion.div
        className="absolute bottom-20 right-10 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"
        style={{ y: useTransform(scrollYProgress, [0, 1], [-50, 50]) }}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <motion.h2
            className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            viewport={{ once: true }}
          >
            <span className="bg-gradient-to-r from-purple-400 via-blue-400 to-purple-600 bg-clip-text text-transparent">
              {translations.testimonials.title}
            </span>
          </motion.h2>
          
          <motion.p
            className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            viewport={{ once: true }}
          >
            {translations.testimonials.subtitle}
          </motion.p>
        </motion.div>

        {/* Testimonials Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {players.map((player: Player, index: number) => (
            <PlayerCard key={player.name} player={player} index={index} />
          ))}
        </div>
      </div>

      {/*  shimmer effect */}
      <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
        .perspective-1000 {
          perspective: 1000px;
        }
        .shimmer-border::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(147, 51, 234, 0.4), transparent);
          animation: shimmer 2s infinite;
        }
      `}</style>
    </motion.section>
  )
}