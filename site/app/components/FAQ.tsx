'use client'

import { useRef, useState } from 'react'
import { motion, useScroll, useTransform, useInView } from 'framer-motion'
import { Search, HelpCircle, MessageCircle, ExternalLink, Play } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { FaDiscord } from 'react-icons/fa6'
import { useTranslations } from '../providers/TranslationProvider'

interface FAQItemProps {
  faq: {
    id: number
    question: string
    answer: string
    category: string
    popular: boolean
  }
  index: number
  isOpen: boolean
  onToggle: () => void
  translations: any
}


const getFAQs = (translations: any) => [
  {
    id: 1,
    question: translations.faq.questions.uploadProfilePicture.question,
    answer: translations.faq.questions.uploadProfilePicture.answer,
    category: 'Setup',
    popular: true
  },
  {
    id: 2,
    question: translations.faq.questions.otherPlayersSeeAvatar.question,
    answer: translations.faq.questions.otherPlayersSeeAvatar.answer,
    category: 'General',
    popular: true
  },
  {
    id: 3,
    question: translations.faq.questions.avatarNotShowing.question,
    answer: translations.faq.questions.avatarNotShowing.answer,
    category: 'Troubleshooting',
    popular: false
  },
  {
    id: 4,
    question: translations.faq.questions.errorRemoveDll.question,
    answer: translations.faq.questions.errorRemoveDll.answer,
    category: 'Troubleshooting',
    popular: false
  },
  {
    id: 5,
    question: translations.faq.questions.beforeBugReport.question,
    answer: translations.faq.questions.beforeBugReport.answer,
    category: 'Support',
    popular: false
  },
  {
    id: 6,
    question: translations.faq.questions.errorMissingFiles.question,
    answer: translations.faq.questions.errorMissingFiles.answer,
    category: 'Installation',
    popular: true
  },
  {
    id: 7,
    question: translations.faq.questions.shareLogs.question,
    answer: translations.faq.questions.shareLogs.answer,
    category: 'Support',
    popular: false
  },
  {
    id: 8,
    question: translations.faq.questions.windowsDefenderUnsafe.question,
    answer: translations.faq.questions.windowsDefenderUnsafe.answer,
    category: 'Security',
    popular: true
  }
]


function FAQItem({ faq, index, isOpen, onToggle, translations }: FAQItemProps) {
  const itemRef = useRef<HTMLDivElement>(null)
  const isInView = useInView(itemRef, { once: true, margin: "-50px" })

  const getCategoryColor = (category: string) => {
    const colors = {
      'General': 'from-blue-500 to-cyan-500',
      'Setup': 'from-green-500 to-emerald-500',
      'Installation': 'from-purple-500 to-violet-500',
      'Troubleshooting': 'from-orange-500 to-red-500',
      'Support': 'from-pink-500 to-rose-500',
      'Security': 'from-yellow-500 to-amber-500'
    }
    return colors[category as keyof typeof colors] || 'from-gray-500 to-slate-500'
  }

  return (
    <motion.div
      ref={itemRef}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: index * 0.1 }}
    >
      <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-sm hover:border-purple-500/50 transition-all duration-300 overflow-hidden">
        <motion.div
          className="p-6 cursor-pointer"
          onClick={onToggle}
          whileHover={{ scale: 1.01 }}
          transition={{ duration: 0.2 }}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 mr-4">
              <div className="flex items-center space-x-3 mb-2">
                <Badge 
                  className={`bg-gradient-to-r ${getCategoryColor(faq.category)} text-white text-xs`}
                >
                  {faq.category}
                </Badge>
                {faq.popular && (
                  <Badge variant="outline" className="border-yellow-500/50 text-yellow-400 text-xs">
                    Popular
                  </Badge>
                )}
              </div>
              <h3 className="text-lg font-semibold text-white mb-2 hover:text-purple-300 transition-colors duration-200">
                {faq.question}
              </h3>
            </div>
            
            <motion.div
              className="flex-shrink-0 w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center"
              animate={{ rotate: isOpen ? 45 : 0 }}
              transition={{ duration: 0.3 }}
            >
              <HelpCircle className="w-5 h-5 text-purple-400" />
            </motion.div>
          </div>

          <motion.div
            initial={false}
            animate={{ 
              height: isOpen ? 'auto' : 0,
              opacity: isOpen ? 1 : 0 
            }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            {isOpen && (
              <motion.div
                initial={{ y: -10 }}
                animate={{ y: 0 }}
                transition={{ duration: 0.3 }}
                className="pt-4 border-t border-slate-700/50 mt-4"
              >
                <p className="text-gray-300 leading-relaxed">
                  {faq.answer}
                </p>
                
                {faq.category === 'Security' && (
                  <div className="mt-4 p-3 bg-yellow-900/20 rounded-lg border border-yellow-700/30">
                    <a className="flex items-center space-x-2 cursor-pointer hover:text-yellow-200 transition-colors">
                      <Play className="w-4 h-4 text-yellow-400" />
                      <span className="text-sm text-yellow-300 font-medium">
                        {translations.faq.questions.pleaseWatchTutorial || "Please watch our tutorial for more details"}
                      </span>
                    </a>
                  </div>
                )}
              </motion.div>
            )}
          </motion.div>
        </motion.div>
      </Card>
    </motion.div>
  )
}

export default function FAQ() {
  const { translations } = useTranslations();
  const sectionRef = useRef<HTMLDivElement>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [openItems, setOpenItems] = useState<number[]>([])

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  })

  const y = useTransform(scrollYProgress, [0, 1], [100, -100])

  if (!translations) return null;

  const faqs = getFAQs(translations);
 
  const categories = [
    { value: 'All', label: 'All' },  
    { value: 'General', label: translations.faq.questions.tags?.general || 'General' },
    { value: 'Setup', label: translations.faq.questions.tags?.setup || 'Setup' },
    { value: 'Installation', label: translations.faq.questions.tags?.installation || 'Installation' },
    { value: 'Troubleshooting', label: translations.faq.questions.tags?.troubleshooting || 'Troubleshooting' },
    { value: 'Support', label: translations.faq.questions.tags?.support || 'Support' },
    { value: 'Security', label: translations.faq.questions.tags?.security || 'Security' }
  ];

  const filteredFAQs = faqs.filter(faq => {
    const matchesSearch = faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || faq.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const toggleItem = (id: number) => {
    setOpenItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    )
  }

  const popularFAQs = faqs.filter(faq => faq.popular)

  return (
    <section 
      ref={sectionRef} 
      id="faq" 
      className="py-24 relative overflow-hidden"
    >
      {/* Background Elements */}
      <motion.div
        className="absolute top-20 left-10 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl"
        style={{ y }}
      />
      <motion.div
        className="absolute bottom-20 right-10 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"
        style={{ y: useTransform(scrollYProgress, [0, 1], [-30, 50]) }}
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
              {translations.faq.title}
            </span>
          </motion.h2>
          
          <motion.p
            className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            viewport={{ once: true }}
          >
            {translations.faq.subtitle}
          </motion.p>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          className="mb-12"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          viewport={{ once: true }}
        >
          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-sm p-6">
            {/* Search Bar */}
            <div className="relative mb-6">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder={(translations.faq as any).search?.placeholder || "Search questions..."}
                value={searchQuery}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
                className="pl-10 bg-slate-900/50 border-slate-600/50 text-white placeholder-gray-400 focus:border-purple-500"
              />
            </div>

            {/* Category Filters */}
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <Button
                  key={category.value}
                  variant={selectedCategory === category.value ? "default" : "outline"}
                  size="sm"
                  onClick={() => setSelectedCategory(category.value)}
                  className={`${
                    selectedCategory === category.value
                      ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                      : 'border-slate-600/50 text-gray-300 hover:bg-slate-700/50'
                  } transition-all duration-200`}
                >
                  {category.label}
                </Button>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* Popular FAQs, avevo voglia, in caso la abiliti
        {selectedCategory === 'All' && searchQuery === '' && (
          <motion.div
            className="mb-12"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            viewport={{ once: true }}
          >
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
              <span className="mr-3">🔥</span>
              Popular Questions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {popularFAQs.map((faq, index) => (
                <motion.div
                  key={faq.id}
                  className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 border border-purple-500/30 rounded-lg p-4 cursor-pointer hover:border-purple-400/50 transition-all duration-300"
                  onClick={() => toggleItem(faq.id)}
                  whileHover={{ scale: 1.02 }}
                  transition={{ duration: 0.2 }}
                >
                  <h4 className="font-semibold text-white text-sm mb-2">{faq.question}</h4>
                  <p className="text-xs text-gray-400 line-clamp-2">{faq.answer}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}*/}

        {/* FAQ List */}
        <motion.div
          className="space-y-4"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          viewport={{ once: true }}
        >
          {filteredFAQs.length > 0 ? (
            filteredFAQs.map((faq, index) => (
              <FAQItem
                key={faq.id}
                faq={faq}
                index={index}
                isOpen={openItems.includes(faq.id)}
                onToggle={() => toggleItem(faq.id)}
                translations={translations}
              />
            ))
          ) : (
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-sm p-12 text-center">
              <MessageCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">
                {(translations.faq as any).search?.noResults || "No Results Found"}
              </h3>
              <p className="text-gray-400 mb-6">
                {(translations.faq as any).search?.noResultsDescription || "Couldn't find any FAQs matching your search. Try different keywords or browse all categories."}
              </p>
              <Button
                onClick={() => {
                  setSearchQuery('')
                  setSelectedCategory('All')
                }}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white"
              >
                {(translations.faq as any).search?.clearFilters || "Clear Filters"}
              </Button>
            </Card>
          )}
        </motion.div>

        {/* Help Section */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          viewport={{ once: true }}
        >
          <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-700/50 backdrop-blur-sm p-8">
            <h3 className="text-2xl font-bold text-white mb-4">
              {(translations.faq as any).moreQuestions?.title || "Still need help?"}
            </h3>
            <p className="text-gray-300 mb-6 max-w-2xl mx-auto">
              {(translations.faq as any).moreQuestions?.description || "Our community and developers are here to help! Join our Discord server for real-time support, feature discussions, and the latest updates."}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
              onClick={() => window.open('https://discord.gg/g3ReJDCr2h', '_blank')}
                className="bg-gradient-to-r from-purple-600 to-blue-600 text-white"
              >
                <FaDiscord className="w-4 h-4 mr-2" />
                {(translations.faq as any).moreQuestions?.joinDiscord || "Join Discord Community"}
              </Button>
            </div>
          </Card>
        </motion.div>
      </div>

      <style jsx>{`
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </section>
  )
}