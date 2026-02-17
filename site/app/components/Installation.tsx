'use client'

import { useRef, useState } from 'react'
import { motion, useScroll, useTransform, useInView } from 'framer-motion'
import { Download, Terminal, Shield, CheckCircle, AlertTriangle, ExternalLink, Copy, Monitor } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
 
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
 
import { useTranslations } from '../providers/TranslationProvider'
 
function renderTextWithCode(text: string) {
  if (!text.includes('`')) {
    return text;
  }

  const parts = text.split('`');
  return parts.map((part, index) => {
    if (index % 2 === 1) { 
      return (
        <code 
          key={index} 
          className="bg-muted relative rounded px-[0.3rem] py-[0.2rem] font-mono text-sm font-semibold"
        >
          {part}
        </code>
      );
    } 
    return part;
  });
}

interface StepItemProps {
  step: React.ReactNode
  index: number
  delay: number
}

function StepItem({ step, index, delay }: StepItemProps) {
  const itemRef = useRef<HTMLDivElement>(null)
  const isInView = useInView(itemRef, { once: true, margin: "-50px" })

  return (
    <motion.div
      ref={itemRef}
      className="flex items-start space-x-4 group"
      initial={{ opacity: 0, x: -20 }}
      animate={isInView ? { opacity: 1, x: 0 } : {}}
      transition={{ duration: 0.5, delay }}
    >
      <motion.div
        className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg"
        whileHover={{ scale: 1.2, rotate: 360 }}
        transition={{ duration: 0.3 }}
      >
        {index + 1}
      </motion.div>
      <div className="min-w-0 flex-1">
        <p className="text-gray-300 group-hover:text-white transition-colors duration-200">
          {typeof step === 'string' ? renderTextWithCode(step) : step}
        </p>
      </div>
    </motion.div>
  )
}

interface CodeBlockProps {
  code: string
  language?: string
  title?: string
}

function CodeBlock({ code, language = 'bash', title }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const copyCode = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error('Failed to copy code:', error)
    }
  }

  return ( 
    <motion.div
      className="relative bg-slate-900/50 rounded-lg overflow-hidden border border-slate-700/50"
      whileHover={{ scale: 1.01 }}
      transition={{ duration: 0.2 }}
    >
      {title && (
        <div className="bg-slate-800/50 px-4 py-2 border-b border-slate-700/50">
          <span className="text-sm text-gray-400">{title}</span>
        </div>
      )}
      <div className="relative">
        <pre className="p-4 text-sm text-gray-300 overflow-x-auto">
          <code className={`language-${language}`}>{code}</code>
        </pre>
        <Button
          onClick={copyCode}
          variant="outline"
          size="sm"
          className="absolute top-2 right-2 bg-slate-800/50 border-slate-600/50 text-gray-300 hover:bg-slate-700/50"
        >
          <Copy className="w-4 h-4 mr-1" />
          {copied ? 'Copied!' : 'Copy'}
        </Button>
      </div>
    </motion.div>
 
  
  )
}

export default function Installation() {
  const { translations } = useTranslations();
  const sectionRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  })

  const y = useTransform(scrollYProgress, [0, 1], [100, -100])

  if (!translations) return null;

  const requirements = [
    { label: translations.installation.systemRequirements.system.windows, status: 'required' as const, icon: Monitor },
    { label: translations.installation.systemRequirements.system.rocketLeague, status: 'required' as const, icon: Shield },
    { label: translations.installation.systemRequirements.system.bakkesmod, status: 'required' as const, icon: CheckCircle },
    { label: translations.installation.systemRequirements.system.internet, status: 'required' as const, icon: CheckCircle },
  ]

  const avatarRequirements = [
    { label: translations.installation.systemRequirements.avatar.format, status: 'info' as const },
    { 
      label: (
        <div>
          <div className="mb-2">{translations.installation.systemRequirements.avatar.size}</div>
          <ul className="list-disc list-inside text-sm text-gray-400 space-y-1 ml-2">
            <li>48x48</li>
            <li>64x64</li>
            <li>84x84</li>
          </ul>
        </div>
      ), 
      status: 'info' as const 
    },
  ]

  return (
    <section 
      ref={sectionRef} 
      id="installation" 
      className="py-24 relative overflow-hidden bg-gradient-to-b from-transparent via-slate-900/30 to-transparent"
    >
      {/* Background Elements */}
      <motion.div
        className="absolute top-0 left-1/3 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl"
        style={{ y }}
      />
      <motion.div
        className="absolute bottom-0 right-1/3 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"
        style={{ y: useTransform(scrollYProgress, [0, 1], [-30, 80]) }}
      />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
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
              {translations.installation.title}
            </span>
          </motion.h2>
          
          <motion.p
            className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            viewport={{ once: true }}
          >
            {translations.installation.subtitle}
          </motion.p>
        </motion.div>

        {/* Requirements Section */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
        >
          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-sm p-8">
            <h3 className="text-2xl font-bold text-white mb-6">{translations.installation.systemRequirements.title}</h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* System Requirements */}
              <div>
                <h4 className="text-lg font-semibold text-purple-300 mb-4">{translations.installation.systemRequirements.system.title}</h4>
                <div className="space-y-3">
                  {requirements.map((req, index) => {
                    const Icon = req.icon
                    return (
                      <motion.div
                        key={req.label}
                        className="flex items-center space-x-3"
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: index * 0.1 }}
                        viewport={{ once: true }}
                      >
                        <Icon className="w-5 h-5 text-green-400" />
                        <span className="text-gray-300">{req.label}</span> 
                      </motion.div>
                    )
                  })}
                </div>
              </div>

              {/* Avatar Requirements */}
              <div>
                <h4 className="text-lg font-semibold text-blue-300 mb-4">{translations.installation.systemRequirements.avatar.title}</h4>
                <div className="space-y-3">
                  {avatarRequirements.map((req, index) => (
                    <motion.div
                      key={req.label}
                      className="flex items-center space-x-3"
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.4, delay: index * 0.1 + 0.2 }}
                      viewport={{ once: true }}
                    >
                      <CheckCircle className="w-5 h-5 text-blue-400" />
                      <span className="text-gray-300">{req.label}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Installation Methods */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          viewport={{ once: true }}
        >
          <Tabs defaultValue="automatic" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-slate-800/50 border border-slate-700/50">
              <TabsTrigger 
                value="automatic" 
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-blue-600"
              >
                <Download className="w-4 h-4 mr-2" />
                {translations.installation.tabs.automaticLabel}
              </TabsTrigger>
              <TabsTrigger 
                value="manual"
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-orange-600 data-[state=active]:to-red-600"
              >
                <Terminal className="w-4 h-4 mr-2" />
                { translations.installation.tabs.manualLabel}
              </TabsTrigger>
            </TabsList>

            <TabsContent value="automatic" className="mt-8">
              <Card className="bg-gradient-to-br from-green-900/20 to-emerald-900/20 border-green-700/50 backdrop-blur-sm p-8">
                <div className="flex items-center mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center mr-4">
                    <CheckCircle className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">{translations.installation.methods.automatic.title}</h3>
                    <p className="text-green-300">{translations.installation.methods.automatic.subtitle}</p>
                  </div>
                </div>

                <div className="space-y-6">
                  <StepItem
                    step={translations.installation.methods.automatic.steps.download}
                    index={0}
                    delay={0 * 0.1}
                  />
                  <StepItem
                    step={translations.installation.methods.automatic.steps.close}
                    index={1}
                    delay={1 * 0.1}
                  />
                  <StepItem
                    step={translations.installation.methods.automatic.steps.run}
                    index={2}
                    delay={2 * 0.1}
                  />
                  <StepItem
                    step={translations.installation.methods.automatic.steps.launch}
                    index={3}
                    delay={3 * 0.1}
                  />
                </div>

                <div className="mt-8 p-4 bg-green-900/20 rounded-lg border border-green-700/30">
                  <div className="flex items-start space-x-3">
                    <Shield className="w-5 h-5 text-green-400 mt-0.5" />
                    <div>
                      <p className="font-semibold text-green-300">{translations.installation.methods.automatic.securityNote.title}</p>
                      <p className="text-sm text-gray-300 mt-1">
                        {translations.installation.methods.automatic.securityNote.description}
                      </p>
                    </div>
                  </div>
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="manual" className="mt-8">
              <Card className="bg-gradient-to-br from-orange-900/20 to-red-900/20 border-orange-700/50 backdrop-blur-sm p-8">
                <div className="flex items-center mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center mr-4">
                    <Terminal className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">{translations.installation.methods.manual.title}</h3>
                    <p className="text-orange-300">{translations.installation.methods.manual.subtitle}</p>
                  </div>
                </div>

                <div className="space-y-6 mb-8">
                  <StepItem
                    step={translations.installation.methods.manual.steps.unzip}
                    index={0}
                    delay={0 * 0.1}
                  />
                  <StepItem
                    step={translations.installation.methods.manual.steps.close}
                    index={1}
                    delay={1 * 0.1}
                  />
                  <StepItem
                    step={translations.installation.methods.manual.steps.pluginsFolder}
                    index={2}
                    delay={2 * 0.1}
                  />
                  <StepItem
                    step={translations.installation.methods.manual.steps.moveDlls}
                    index={3}
                    delay={3 * 0.1}
                  />
                  <StepItem
                    step={translations.installation.methods.manual.steps.cfgFolder}
                    index={4}
                    delay={4 * 0.1}
                  />
                  <StepItem
                    step={
                      <>
                        {renderTextWithCode(translations.installation.methods.manual.steps.editCfg)}
                        <div className="mt-4">
                           <CodeBlock
                    title="Add to plugins.cfg"
                    code={"plugin load rlprofilepicturesrevamp \nplugin load rlpfpmanager"}
                  />
                        </div>
                      </>
                    }
                    index={5}
                    delay={5 * 0.1}
                  />
                  <StepItem
                    step={translations.installation.methods.manual.steps.launch}
                    index={6}
                    delay={6 * 0.1}
                  />
                </div>
 
              </Card>
            </TabsContent>
          </Tabs>
        </motion.div>

        {/* Verification Section */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          viewport={{ once: true }}
        >
          <Card className="bg-gradient-to-br from-blue-900/20 to-purple-900/20 border-blue-700/50 backdrop-blur-sm p-8">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mr-4">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">{translations.installation.verification.title}</h3>
                <p className="text-blue-300">{translations.installation.verification.subtitle}</p>
              </div>
            </div>

            <div className="space-y-6">
              <StepItem
                step={translations.installation.verification.steps.console}
                index={0}
                delay={0 * 0.1}
              />
              <StepItem
                step={translations.installation.verification.steps.checkPlugins}
                index={1}
                delay={1 * 0.1}
              />
              <StepItem
                step={translations.installation.verification.steps.accessMenu}
                index={2}
                delay={2 * 0.1}
              />
              <StepItem
                step={translations.installation.verification.steps.upload}
                index={3}
                delay={3 * 0.1}
              />
            </div>
          </Card>
        </motion.div>

        {/* Troubleshooting Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          viewport={{ once: true }}
        >
          <Card className="bg-gradient-to-br from-yellow-900/20 to-yellow-800/20 border-yellow-700/50 backdrop-blur-sm p-8">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5" />
                <div>
                  <h1 className="font-semibold text-yellow-300">{translations.installation.troubleshooting.title}</h1>
                  <p className="text-sm text-gray-300 mt-1">
                    {renderTextWithCode(translations.installation.troubleshooting.description)}
                  </p>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => window.open('https://discord.gg/g3ReJDCr2h', '_blank')}
                    className="mt-3 border-yellow-500/50 text-yellow-400 hover:bg-yellow-500/20"
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    {translations.installation.troubleshooting.joinDiscord}
                  </Button>
                </div>
              </div>
           
          </Card>
        </motion.div>
      </div>
    </section>
  )
}