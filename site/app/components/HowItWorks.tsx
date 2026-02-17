'use client'

import { useRef } from 'react'
import { motion, useScroll, useTransform, useInView } from 'framer-motion'
import { Upload, Server, Eye, Globe, ArrowRight, Settings } from 'lucide-react'
import { Card } from '@/components/ui/card'
import Image from 'next/image'
import { useTranslations } from '../providers/TranslationProvider'

interface Step {
  number: number;
  icon: any;
  title: string;
  description: string;
  color: string;
  delay: number;
}

interface StepCardProps {
  step: Step;
  index: number;
  isLast: boolean;
}

function StepCard({ step, index, isLast }: StepCardProps) {
  const cardRef = useRef<HTMLDivElement>(null)
  const isInView = useInView(cardRef, { once: true, margin: "-100px" })
  
  const Icon = step.icon

  return (
    <div className="relative">
      {/* Connection Line */}
      {!isLast && (
        <motion.div
          className="hidden lg:block absolute top-1/2 left-full w-16 h-0.5 bg-gradient-to-r from-purple-500 to-transparent z-10"
          initial={{ scaleX: 0 }}
          animate={isInView ? { scaleX: 1 } : {}}
          transition={{ duration: 0.6, delay: step.delay + 0.3 }}
        />
      )}

      <motion.div
        ref={cardRef}
        initial={{ opacity: 0, y: 50, scale: 0.8 }}
        animate={isInView ? {
          opacity: 1,
          y: 0,
          scale: 1,
          transition: {
            duration: 0.6,
            delay: step.delay,
            ease: "easeOut"
          }
        } : {}}
        whileHover={{
          y: -10,
          scale: 1.05,
          transition: { duration: 0.3 }
        }}
        className="group"
      >
        <Card className="relative h-full bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300 overflow-hidden">
          {/* Animated Background */}
          <div className={`absolute inset-0 bg-gradient-to-br ${step.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
          
          {/* Step Number */}
          <div className="absolute top-6 right-6">
            <motion.div
              className={`w-12 h-12 rounded-full bg-gradient-to-br ${step.color} flex items-center justify-center text-white font-bold text-lg shadow-lg`}
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
            >
              {step.number}
            </motion.div>
          </div>

          <div className="p-8">
            {/* Icon */}
            <motion.div
              className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center mb-6 shadow-xl`}
              whileHover={{
                scale: 1.1,
                rotate: 5,
                transition: { duration: 0.3 }
              }}
            >
              <Icon className="w-10 h-10 text-white" />
            </motion.div>

            {/* Content */}
            <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-purple-300 transition-colors duration-300">
              {step.title}
            </h3>
            <p className="text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors duration-300">
              {step.description}
            </p>

            {/* Hover Arrow */}
            <motion.div
              className="mt-6 flex items-center text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
              initial={{ x: -10 }}
              whileInView={{ x: 0 }}
              transition={{ duration: 0.3 }}
            >
            </motion.div>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}

export default function HowItWorks() {
  const { translations } = useTranslations();
  const sectionRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  })

  const y = useTransform(scrollYProgress, [0, 1], [100, -100])

  if (!translations) return null;

  const t = translations as any;

  const steps: Step[] = [
    {
      number: 1,
      icon: Upload,
      title: t.howItWorks.step1.title,
      description: t.howItWorks.step1.description,
      color: 'from-pink-500 to-purple-600',
      delay: 0.1
    },
    {
      number: 2,
      icon: Server,
      title: t.howItWorks.step2.title,
      description: t.howItWorks.step2.description,
      color: 'from-blue-500 to-cyan-600',
      delay: 0.2
    },
    {
      number: 3,
      icon: Eye,
      title: t.howItWorks.step3.title,
      description: t.howItWorks.step3.description,
      color: 'from-emerald-500 to-teal-600',
      delay: 0.3
    },
    {
      number: 4,
      icon: Globe,
      title: t.howItWorks.step4.title,
      description: t.howItWorks.step4.description,
      color: 'from-orange-500 to-red-600',
      delay: 0.4
    }
  ]

  return (
    <section ref={sectionRef} className="py-24 relative overflow-hidden bg-gradient-to-b from-transparent via-slate-900/50 to-transparent">
      {/* Background Elements */}
      <motion.div
        className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl"
        style={{ y }}
      />
      <motion.div
        className="absolute bottom-0 right-1/4 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl"
        style={{ y: useTransform(scrollYProgress, [0, 1], [-50, 100]) }}
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
              {t.howItWorks.title}
            </span>
          </motion.h2>
          
          <motion.p
            className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            viewport={{ once: true }}
          >
            {t.howItWorks.subtitle}
          </motion.p>
        </motion.div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 lg:gap-4 mb-16">
          {steps.map((step: Step, index: number) => (
            <StepCard
              key={step.number}
              step={step}
              index={index}
              isLast={index === steps.length - 1}
            />
          ))}
        </div>

        {/* Demo Section */}
        <motion.div
          className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
        >
          {/* Left - Image Showcase */}
          <div className="relative group">
            <motion.div
              className="relative rounded-2xl overflow-hidden shadow-2xl border border-slate-700/50"
              whileHover={{ scale: 1.02, rotateY: 5 }}
              transition={{ duration: 0.4 }}
            >
              <Image
                src="/assets/plugin_menu.png"
                alt="Rocket League Profile Picture Demo"
                width={600}
                height={400}
                className="w-full h-auto object-cover"
              />
              
              {/* Overlay on hover */}
              <div className="absolute inset-0 bg-gradient-to-t from-purple-900/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end">
                <div className="p-6 text-white">
                  <h4 className="font-semibold mb-2">Easy Configuration</h4>
                  <p className="text-sm text-purple-200">Intuitive interface for all settings</p>
                </div>
              </div>
            </motion.div>

            {/* Floating Elements */}
            <motion.div
              className="absolute -top-4 -right-4 w-20 h-20 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full opacity-20"
              animate={{
                scale: [1, 1.2, 1],
                rotate: [0, 180, 360]
              }}
              transition={{
                duration: 8,
                repeat: Infinity,
                ease: "linear"
              }}
            />
            <motion.div
              className="absolute -bottom-6 -left-6 w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-full opacity-20"
              animate={{
                scale: [1.2, 1, 1.2],
                rotate: [360, 180, 0]
              }}
              transition={{
                duration: 6,
                repeat: Infinity,
                ease: "linear"
              }}
            />
          </div>

          {/* Right - Process Details */}
          <div className="space-y-8">
            <motion.div
              className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-2xl p-6 border border-slate-700/50 backdrop-blur-sm"
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <h3 className="text-2xl font-bold text-white mb-4">{t.howItWorks.card1.title}</h3>
              <p className="text-gray-300 mb-4">
                {t.howItWorks.card1.description}
              </p>
              <div className="flex items-center text-purple-400">
                <div className="w-2 h-2 bg-purple-400 rounded-full mr-3"></div>
                <span className="text-sm">{t.howItWorks.card1.details}</span>
              </div>
            </motion.div>

             
            <motion.div
              className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-2xl p-6 border border-slate-700/50 backdrop-blur-sm"
              initial={{ opacity: 0, x: 50 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              viewport={{ once: true }}
            >
              <h3 className="text-2xl font-bold text-white mb-4">{t.howItWorks.card2.title}</h3>
              <p className="text-gray-300 mb-4">
                {t.howItWorks.card2.description}
              </p>
              <div className="flex items-center text-blue-400">
                <div className="w-2 h-2 bg-blue-400 rounded-full mr-3"></div>
                <span className="text-sm">{t.howItWorks.card2.details}</span>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}