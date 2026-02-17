'use client'

import { useRef } from 'react'
import { motion, useScroll, useTransform, useInView } from 'framer-motion'
import { Palette, Eye, Settings, RotateCcw, Shield, Zap, Users, Globe, Sparkles, RefreshCw } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { useTranslations } from '../providers/TranslationProvider'

interface Feature {
  icon: any;
  title: string;
  description: string;
  color: string; 
  delay: number;
}

interface FeatureCardProps {
  feature: Feature;
  index: number;
}

function FeatureCard({ feature, index }: FeatureCardProps) {
  const cardRef = useRef<HTMLDivElement>(null)
  const isInView = useInView(cardRef, { once: true, margin: "-100px" })
  
  const Icon = feature.icon

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
          delay: feature.delay,
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
        {/* Animated Background Gradient */}
        <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
        
        {/* Floating Icon Background */}
        <div className="absolute top-4 right-4 opacity-10 group-hover:opacity-20 transition-opacity duration-300">
          <Icon size={80} className="text-white" />
        </div>

        <div className="relative p-6 h-full flex flex-col">
          {/* Icon Container */}
          <motion.div
            className={`w-16 h-16 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-4 shadow-lg`}
            whileHover={{ 
              rotate: 360,
              scale: 1.1,
              transition: { duration: 0.5 }
            }}
          >
            <Icon className="w-8 h-8 text-white" />
          </motion.div>

          {/* Content */}
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white mb-3 group-hover:text-purple-300 transition-colors duration-300">
              {feature.title}
            </h3>
            <p className="text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors duration-300">
              {feature.description}
            </p>
          </div>

          {/* Hover Effect Border */}
          <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-500/0 via-purple-500/50 to-purple-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" 
               style={{ 
                 background: 'linear-gradient(90deg, transparent, rgba(147, 51, 234, 0.3), transparent)',
                 transform: 'translateX(-100%)',
                 animation: 'shimmer 2s infinite'
               }} />
        </div>
      </Card>
    </motion.div>
  )
}

export default function Features() {
  const { translations } = useTranslations();
  const sectionRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  })

  const y = useTransform(scrollYProgress, [0, 1], [100, -100])
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0])

  if (!translations) return null;

  const features = [
    {
      icon: Sparkles,
      title: translations.features.customAvatar.title,
      description: translations.features.customAvatar.description,
      color: 'from-purple-500 to-pink-500', 
      delay: 0.1
    },
    {
      icon: Eye,
      title: translations.features.crossPlatform.title,
      description: translations.features.crossPlatform.description,
      color: 'from-blue-500 to-cyan-500', 
      delay: 0.2
    },
    {
      icon: Settings,
      title: translations.features.configurable.title,
      description: translations.features.configurable.description,
      color: 'from-green-500 to-emerald-500', 
      delay: 0.3
    },
    {
      icon: RefreshCw,
      title: translations.features.autoUpdates.title,
      description: translations.features.autoUpdates.description,
      color: 'from-orange-500 to-red-500', 
      delay: 0.4
    }
  ];

  return (
    <motion.section
      ref={sectionRef}
      id="features"
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
              {translations.features.title}
            </span>
          </motion.h2>
          
          <motion.p
            className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            viewport={{ once: true }}
          >
            {translations.features.subtitle}
          </motion.p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature: Feature, index: number) => (
            <FeatureCard key={feature.title} feature={feature} index={index} />
          ))}
        </div>

     
      </div>

      {/* Custom CSS for shimmer effect */}
      <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
        .perspective-1000 {
          perspective: 1000px;
        }
      `}</style>
    </motion.section>
  )
}