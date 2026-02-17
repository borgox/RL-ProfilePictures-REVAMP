"use client";

import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Clock, Download, Star } from "lucide-react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import twemoji from "twemoji";
import { useTranslations } from '../providers/TranslationProvider';

interface ChangelogEntry {
  version: string;
  content: string;
  date?: string;
}
 
function TwemojiWrapper({ children, className }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) { 
      twemoji.parse(ref.current, {
        folder: 'svg',
        ext: '.svg',
        className: 'twemoji',
        base: 'https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/'
      });
    }
  }, []);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
 
const emojiMap: Record<string, string> = {
  ':fire:': '🔥',
  ':sparkles:': '✨',
  ':frame_photo:': '🖼️',
  ':globe_with_meridians:': '🌐',
  ':information_source:': 'ℹ️',
  ':open_file_folder:': '📁',
  ':art:': '🎨',
  ':tools:': '🔧',
  ':point_right:': '👉',
  ':heart:': '❤️',
  ':rocket:': '🚀',
  ':bug:': '🐛',
  ':zap:': '⚡',
  ':tada:': '🎉',
  ':construction:': '🚧',
  ':heavy_check_mark:': '✅',
  ':warning:': '⚠️',
  ':memo:': '📝',
  ':wrench:': '🔧',
  ':gear:': '⚙️'
};
 
function convertEmojiCodes(text: string): string {
  let result = text;
  Object.entries(emojiMap).forEach(([code, emoji]) => {
    result = result.replace(new RegExp(code.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'), emoji);
  });
  return result;
}
 
async function loadChangelogs(): Promise<ChangelogEntry[]> {
  try { 
    const changelog_1_1_0 = await import('../changelogs/1.1.0');

    const changelogs: ChangelogEntry[] = [
      {
        version: "1.1.0",
        content: convertEmojiCodes(changelog_1_1_0.default),
        date: "2025-10-02"  
      },
      {
        version: "1.1.1",
        content: convertEmojiCodes((await import('../changelogs/1.1.1')).default),
        date: "2025-10-11"
      },
      {
        version: "1.1.2",
        content: convertEmojiCodes((await import('../changelogs/1.1.2')).default),
        date: "2025-10-15"
      }
    ];
    
    return changelogs.sort((a, b) => b.version.localeCompare(a.version));
  } catch (error) {
    console.error("Errore nel caricamento dei changelog:", error);
    return [];
  }
}
 
const MarkdownComponents = {
  p: ({ children, ...props }: any) => (
    <p {...props} className="mb-4 text-gray-300 leading-relaxed">{children}</p>
  ),
  h1: ({ children, ...props }: any) => (
    <h1 {...props} className="text-2xl font-bold mb-4 text-white">{children}</h1>
  ),
  h2: ({ children, ...props }: any) => (
    <h2 {...props} className="text-xl font-semibold mb-3 text-purple-300">{children}</h2>
  ),
  h3: ({ children, ...props }: any) => (
    <h3 {...props} className="text-lg font-medium mb-2 text-purple-200">{children}</h3>
  ),
  ul: ({ children, ...props }: any) => (
    <ul {...props} className="list-none space-y-2 mb-4">{children}</ul>
  ),
  li: ({ children, ...props }: any) => (
    <li {...props} className="flex items-start gap-2 text-gray-300">
      <span className="text-purple-400 mt-1">•</span>
      <span className="flex-1">{children}</span>
    </li>
  ),
  strong: ({ children, ...props }: any) => (
    <strong {...props} className="font-semibold text-white">{children}</strong>
  ),
  code: ({ children, ...props }: any) => (
    <code {...props} className="bg-purple-900/50 text-purple-300 px-1 py-0.5 rounded text-sm">
      {children}
    </code>
  ),
  a: ({ children, ...props }: any) => (
    <a {...props} className="text-purple-400 hover:text-purple-300 underline" target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  ),
};

export default function Changelog() {
  const { translations } = useTranslations();
  const [changelogs, setChangelogs] = useState<ChangelogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchChangelogs() {
      const logs = await loadChangelogs();
      setChangelogs(logs);
      setIsLoading(false);
    }
    fetchChangelogs();
  }, []);

  if (isLoading) {
    return (
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="py-16 px-4 sm:px-6 lg:px-8"
      >
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <Skeleton className="h-12 w-64 mx-auto mb-4" />
            <Skeleton className="h-6 w-96 mx-auto" />
          </div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="bg-slate-900/50">
                <CardHeader>
                  <Skeleton className="h-8 w-32" />
                  <Skeleton className="h-4 w-48" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-32 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </motion.section>
    );
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="py-16 px-4 sm:px-6 lg:px-8"
      id="changelog"
    >
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent mb-4">
            {translations?.changelog?.title || "Changelog"}
          </h2>
          <p className="text-gray-300 text-lg max-w-2xl mx-auto">
            {translations?.changelog?.subtitle}
          </p>
        </motion.div>

        {/* Changelog Items */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          {changelogs.length > 0 ? (
            <Accordion type="single" collapsible className="space-y-4">
              {changelogs.map((changelog, index) => (
                <AccordionItem
                  key={changelog.version}
                  value={changelog.version}
                  className="border-none"
                  id={`v-${changelog.version.replace(/\./g, "-")}`}
                >
                  <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm hover:bg-slate-900/70 transition-all duration-300">
                    <AccordionTrigger className="px-6 py-4 hover:no-underline">
                      <div className="flex items-center justify-between w-full">
                        <div className="flex items-center gap-4">
                          <Badge 
                            variant="outline" 
                            className="bg-purple-900/50 border-purple-500/50 text-purple-300 hover:bg-purple-900/70"
                          >
                            <Star className="w-3 h-3 mr-1" />
                            v{changelog.version}
                          </Badge>
                          {changelog.date && (
                            <div className="flex items-center gap-1 text-gray-400 text-sm">
                              <Clock className="w-3 h-3" />
                              {new Date(changelog.date).toLocaleDateString('it-IT')}
                            </div>
                          )}
                          {index === 0 && (
                            <Badge className="bg-gradient-to-r from-green-500 to-emerald-500 text-white">
                              {translations?.changelog?.latestVersion}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="px-6 pb-6">
                      <TwemojiWrapper className="prose prose-invert prose-purple max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={MarkdownComponents}
                        >
                          {changelog.content}
                        </ReactMarkdown>
                      </TwemojiWrapper>
                    </AccordionContent>
                  </Card>
                </AccordionItem>
              ))}
            </Accordion>
          ) : (
            <Card className="bg-slate-900/50 border-slate-700/50 backdrop-blur-sm">
              <CardHeader className="text-center py-8">
                <CardTitle className="text-gray-300">{translations?.changelog?.noChangelogAvailable }</CardTitle>
                <CardDescription className="text-gray-500">
                  {translations?.changelog?.changelogComingSoon }
                </CardDescription>
              </CardHeader>
            </Card>
          )}
        </motion.div>
      </div>

      {/* Custom CSS for twemoji */}
      <style jsx global>{`
        .twemoji {
          height: 1.2em !important;
          width: 1.2em !important;
          margin: 0 0.1em !important;
          vertical-align: -0.1em !important;
          display: inline-block !important;
        }
        
        .prose-purple a {
          color: #c084fc;
          text-decoration: none;
        }
        
        .prose-purple a:hover {
          color: #a855f7;
          text-decoration: underline;
        }

        /* Assicurati che le emoji siano sempre visibili */
        img.emoji {
          height: 1.2em !important;
          width: 1.2em !important;
          margin: 0 0.1em !important;
          vertical-align: -0.1em !important;
          display: inline-block !important;
        }
      `}</style>
    </motion.section>
  );
}