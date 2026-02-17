'use client'

import { useRef, useState } from 'react'
import { motion, useScroll, useTransform, useInView, AnimatePresence } from 'framer-motion'
import { Play, X, ExternalLink, ZoomIn, Pause, Volume2, VolumeX, Maximize, Minimize } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Image from 'next/image'
import { useTranslations } from '../providers/TranslationProvider'



interface Screenshot {
  id: number;
  title: string;
  description: string;
  image: string;
  category: string;
  featured: boolean;
}

interface ScreenshotCardProps {
  screenshot: Screenshot;
  index: number;
  onOpen: (screenshot: Screenshot) => void;
  translations: any;
}

function ScreenshotCard({ screenshot, index, onOpen, translations }: ScreenshotCardProps) {
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
          duration: 0.8,
          delay: index * 0.2,
          ease: "easeOut"
        }
      } : {}}
      whileHover={{
        y: -15,
        rotateX: 10,
        rotateY: 5,
        scale: 1.02,
        transition: { duration: 0.4 }
      }}
      className="group perspective-1000"
    >
      <Card className="relative h-full bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300 overflow-hidden cursor-pointer"
           onClick={() => onOpen(screenshot)}>
        
        {/* Featured Badge */}
        {screenshot.featured && (
          <div className="absolute top-4 left-4 z-20">
            <span className="bg-gradient-to-r from-purple-500 to-blue-500 text-white text-xs font-bold px-3 py-1 rounded-full">
              {translations.screenshots.labels.featured}
            </span>
          </div>
        )}

        {/* Category Badge */}
        <div className="absolute top-4 right-4 z-20">
          <span className="bg-slate-900/80 text-purple-300 text-xs font-medium px-3 py-1 rounded-full border border-purple-500/30">
            {screenshot.category}
          </span>
        </div>

        {/* Image Container */}
        <div className="relative aspect-video overflow-hidden">
            <Image 
                src={screenshot.image}
                alt={screenshot.title}
                fill
                className="object-cover group-hover:scale-105 transition-transform duration-500"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
            />
          
          {/* Hover Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end">
            <div className="p-6 w-full">
              <div className="flex items-center justify-between">
                <Button
                  variant="secondary"
                  size="sm"
                  className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30"
                  onClick={(e) => {
                    e.stopPropagation()
                    onOpen(screenshot)
                  }}
                >
                  <ZoomIn className="w-4 h-4 mr-2" />
                  {translations.screenshots.labels.viewFull}
                </Button>
                
                {screenshot.image.endsWith('.gif') && (
                  <div className="flex items-center text-purple-300">
                    <Play className="w-4 h-4 mr-1" />
                    <span className="text-xs">{translations.screenshots.labels.animated}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Shimmer Effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out" />
        </div>

        {/* Content */}
        <div className="p-6">
          <h3 className="text-xl font-semibold text-white mb-3 group-hover:text-purple-300 transition-colors duration-300">
            {screenshot.title}
          </h3>
          <p className="text-gray-400 text-sm leading-relaxed group-hover:text-gray-300 transition-colors duration-300">
            {screenshot.description}
          </p>

          {/* Hover Action */}
          <motion.div
            className="mt-4 flex items-center text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            initial={{ x: -10 }}
            whileInView={{ x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <span className="text-sm font-medium mr-2">{translations.screenshots.labels.clickToExpand}</span>
            <ExternalLink className="w-4 h-4" />
          </motion.div>
        </div>

        {/* Border Effect */}
        <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-purple-500/0 via-purple-500/20 to-purple-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      </Card>
    </motion.div>
  )
}

interface LightboxProps {
  screenshot: Screenshot | null
  onClose: () => void
  translations: any
}

function Lightbox({ screenshot, onClose, translations }: LightboxProps) {
  if (!screenshot) return null

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        {/* Close Button */}
        <motion.button
          className="absolute top-6 right-6 text-white hover:text-purple-400 transition-colors z-60"
          onClick={onClose}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <X className="w-8 h-8" />
        </motion.button>

        {/* Content */}
        <motion.div
          className="max-w-6xl w-full"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          transition={{ duration: 0.3 }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Image */}
          <div className="relative mb-6 rounded-xl overflow-hidden shadow-2xl">
            <Image 
                src={screenshot.image}
                alt={screenshot.title}
                width={1280}
                height={720}
                className="w-full h-auto object-cover"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 60vw"
            />
          </div>

          {/* Info */}
          <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h3 className="text-2xl font-bold text-white mb-2">{screenshot.title}</h3>
                <p className="text-gray-300 mb-4 sm:mb-0">{screenshot.description}</p>
              </div>
              <div className="flex items-center space-x-4">
                <span className="bg-purple-500/20 text-purple-300 text-sm font-medium px-3 py-1 rounded-full border border-purple-500/30">
                  {screenshot.category}
                </span>
                {screenshot.featured && (
                  <span className="bg-gradient-to-r from-purple-500 to-blue-500 text-white text-sm font-bold px-3 py-1 rounded-full">
                    {translations.screenshots.labels.featured}
                  </span>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

export default function Screenshots() {
  const { translations } = useTranslations();
  const sectionRef = useRef<HTMLDivElement>(null)
  const [selectedScreenshot, setSelectedScreenshot] = useState<Screenshot | null>(null)
   
  //controlli birillo
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showControls, setShowControls] = useState(true)
  
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  })

  const y = useTransform(scrollYProgress, [0, 1], [100, -100])

  if (!translations) return null;

  const t = translations as any;

  const screenshots = [
    {
      id: 1,
      title: t.screenshots.gallery.screenshot1.title,
      description: t.screenshots.gallery.screenshot1.description,
      image: '/assets/plugin_menu.png',
      category: t.screenshots.gallery.screenshot1.category,
      featured: true
    },
    {
      id: 2,
      title: t.screenshots.gallery.screenshot2.title,
      description: t.screenshots.gallery.screenshot2.description,
      image: '/assets/plugin_ingame.png',
      category: t.screenshots.gallery.screenshot2.category,
      featured: true
    },
    {
      id: 3,
      title: t.screenshots.gallery.screenshot3.title,
      description: t.screenshots.gallery.screenshot3.description,
      image: '/assets/plugin_usage.gif',
      category: t.screenshots.gallery.screenshot3.category,
      featured: false
    }
  ]
 
  //controlli di nuovo
  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
    }
  }

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value)
    if (videoRef.current) {
      videoRef.current.currentTime = time
      setCurrentTime(time)
    }
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value)
    if (videoRef.current) {
      videoRef.current.volume = newVolume
      setVolume(newVolume)
      setIsMuted(newVolume === 0)
    }
  }

  const toggleMute = () => {
    if (videoRef.current) {
      if (isMuted) {
        videoRef.current.volume = volume
        setIsMuted(false)
      } else {
        videoRef.current.volume = 0
        setIsMuted(true)
      }
    }
  }

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      videoRef.current?.parentElement?.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <>
      <section ref={sectionRef} className="py-24 relative overflow-hidden">
        {/* Background Elements */}
        <motion.div
          className="absolute top-20 right-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"
          style={{ y }}
        />
        <motion.div
          className="absolute bottom-20 left-10 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"
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
                {t.screenshots.title}
              </span>
            </motion.h2>
            
            <motion.p
              className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              viewport={{ once: true }}
            >
              {t.screenshots.subtitle}
            </motion.p>
          </motion.div>

          {/* Screenshots Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
            {screenshots.map((screenshot, index) => (
              <ScreenshotCard
                key={screenshot.id}
                screenshot={screenshot}
                index={index}
                onOpen={setSelectedScreenshot}
                translations={t}
              />
            ))}
          </div>

          {/* Video Section */}
          <motion.div
            className="max-w-4xl mx-auto"
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            viewport={{ once: true }}
          >
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-sm overflow-hidden"   id="tutorial-video">
              <div className="p-4 sm:p-6">
                <div className="text-center mb-4 sm:mb-6">
                  <h3 className="text-2xl sm:text-3xl font-bold text-white mb-2 sm:mb-3">{t.screenshots.tutorial.title}</h3>
                  <p className="text-gray-300 text-sm sm:text-base px-2 sm:px-0">
                    {t.screenshots.tutorial.description}
                  </p>
                </div>
                
                <div className="relative aspect-video bg-gradient-to-br from-slate-700 to-slate-800 rounded-xl overflow-hidden group"
                   
                     onMouseEnter={() => setShowControls(true)}
                     onMouseLeave={() => setShowControls(false)}
                     onMouseMove={() => setShowControls(true)}>
                  <video
                    ref={videoRef}
                    className="w-full h-full object-contain"
                    onTimeUpdate={handleTimeUpdate}
                    onLoadedMetadata={handleLoadedMetadata}
                    onPlay={() => setIsPlaying(true)}
                    onPause={() => setIsPlaying(false)}
                    onClick={togglePlay}
                    preload="metadata"
                  >
                    <source src="/assets/Tutorial.mp4" type="video/mp4" />
                    {t.screenshots.tutorial.videoNotSupported}
                  </video>

                  {/* Custom Controls */}
                  <AnimatePresence>
                    {(showControls || !isPlaying) && (
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        {/* Center Play/Pause Button */}
                        {!isPlaying && (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <motion.button
                              className="bg-white/20 backdrop-blur-sm rounded-full p-4 sm:p-6 hover:bg-white/30 transition-colors touch-manipulation"
                              onClick={togglePlay}
                              whileHover={{ scale: 1.1 }}
                              whileTap={{ scale: 0.9 }}
                            >
                              <Play className="w-8 h-8 sm:w-12 sm:h-12 text-white ml-0.5 sm:ml-1" />
                            </motion.button>
                          </div>
                        )}

                        {/* Bottom Controls */}
                        <div className="absolute bottom-0 left-0 right-0 p-2 sm:p-4">
                          <div className="bg-black/60 backdrop-blur-sm rounded-lg p-2 sm:p-3">
                            {/* Progress Bar */}
                            <div className="mb-2 sm:mb-3">
                              <input
                                type="range"
                                min="0"
                                max={duration}
                                value={currentTime}
                                onChange={handleSeek}
                                className="w-full h-3 sm:h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer slider touch-manipulation"
                              />
                            </div>

                            {/* Controls Row */}
                            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-0">
                              <div className="flex items-center space-x-3 sm:space-x-4">
                                {/* Play/Pause */}
                                <button
                                  onClick={togglePlay}
                                  className="text-white hover:text-purple-400 transition-colors p-1 touch-manipulation"
                                >
                                  {isPlaying ? <Pause className="w-5 h-5 sm:w-6 sm:h-6" /> : <Play className="w-5 h-5 sm:w-6 sm:h-6" />}
                                </button>

                                {/* Time Display */}
                                <span className="text-white text-xs sm:text-sm font-mono whitespace-nowrap">
                                  {formatTime(currentTime)} / {formatTime(duration)}
                                </span>
                              </div>

                              <div className="flex items-center space-x-3 sm:space-x-4">
                                {/* Volume */}
                                <div className="flex items-center space-x-2">
                                  <button
                                    onClick={toggleMute}
                                    className="text-white hover:text-purple-400 transition-colors p-1 touch-manipulation"
                                  >
                                    {isMuted || volume === 0 ? <VolumeX className="w-4 h-4 sm:w-5 sm:h-5" /> : <Volume2 className="w-4 h-4 sm:w-5 sm:h-5" />}
                                  </button>
                                  <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    value={isMuted ? 0 : volume}
                                    onChange={handleVolumeChange}
                                    className="w-16 sm:w-20 h-2 sm:h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer slider touch-manipulation"
                                  />
                                </div>

                                {/* Fullscreen */}
                                <button
                                  onClick={toggleFullscreen}
                                  className="text-white hover:text-purple-400 transition-colors p-1 touch-manipulation"
                                >
                                  {isFullscreen ? <Minimize className="w-4 h-4 sm:w-5 sm:h-5" /> : <Maximize className="w-4 h-4 sm:w-5 sm:h-5" />}
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* Lightbox */}
      <Lightbox 
        screenshot={selectedScreenshot} 
        onClose={() => setSelectedScreenshot(null)}
        translations={t}
      />

      <style jsx>{`
        .perspective-1000 {
          perspective: 1000px;
        }
        
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 16px;
          width: 16px;
          border-radius: 50%;
          background: #8b5cf6;
          cursor: pointer;
          border: 2px solid #ffffff;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .slider::-moz-range-thumb {
          height: 16px;
          width: 16px;
          border-radius: 50%;
          background: #8b5cf6;
          cursor: pointer;
          border: 2px solid #ffffff;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        @media (max-width: 640px) {
          .slider::-webkit-slider-thumb {
            height: 20px;
            width: 20px;
          }
          
          .slider::-moz-range-thumb {
            height: 20px;
            width: 20px;
          }
        }

        .touch-manipulation {
          touch-action: manipulation;
        }
      `}</style>
    </>
  )
}