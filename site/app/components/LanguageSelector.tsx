"use client";

import { Languages } from "lucide-react";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTranslations } from '../providers/TranslationProvider';
import { SupportedLanguage } from '../hooks/useRLPFPTranslations';

export default function LanguageSelector() {
  const { currentLanguage, changeLanguage, getAvailableLanguages } = useTranslations();
  const availableLanguages = getAvailableLanguages();

  const currentLangInfo = availableLanguages.find(lang => lang.code === currentLanguage);

  const handleLanguageChange = (value: string) => {
    changeLanguage(value as SupportedLanguage);
  };

  return (
    <div className="flex items-center space-x-2"> 
      <Languages className="hidden md:block w-4 h-4 text-white/60" />
      <Select value={currentLanguage} onValueChange={handleLanguageChange}>
        <SelectTrigger className="w-[50px] md:w-[140px] bg-slate-800/50 border-white/10 text-white hover:bg-slate-700/50 transition-colors">
          <SelectValue>
            {currentLangInfo && (
              <div className="flex items-center space-x-2">
                <span>{currentLangInfo.flag}</span>
                {/* Nome della lingua solo su desktop */}
                <span className="hidden md:block text-sm">{currentLangInfo.name}</span>
              </div>
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent className="bg-slate-900/95 backdrop-blur-md border-white/10">
          {availableLanguages.map((language) => (
            <SelectItem 
              key={language.code} 
              value={language.code}
              className="text-white hover:bg-white/10 focus:bg-white/10"
            >
              <div className="flex items-center space-x-2">
                <span>{language.flag}</span>
                <span>{language.name}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}