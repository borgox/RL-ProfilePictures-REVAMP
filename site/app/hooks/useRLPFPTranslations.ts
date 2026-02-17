"use client";

import { useState, useEffect, useCallback } from 'react';

import en from "@/app/locales/en.json"; // English
import it from "@/app/locales/it.json"; // Italian
import vec from "@/app/locales/vec.json"; // Venetian
import to from "@/app/locales/to.json"; // Toscano

export type RLPFPTranslations = Record<string, any>;

export type SupportedLanguage = string;

const STORAGE_KEY = 'rlpfp-language';
const DEFAULT_LANGUAGE: SupportedLanguage = 'en';

export function useRLPFPTranslations() {
  const [currentLanguage, setCurrentLanguage] = useState<SupportedLanguage>(DEFAULT_LANGUAGE);
  const [translations, setTranslations] = useState<RLPFPTranslations | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

 //carica dalla localstorage
  useEffect(() => {
    try {
      const savedLanguage = localStorage.getItem(STORAGE_KEY) as SupportedLanguage;
      if (savedLanguage && ['en', 'it', 'vec', 'to'].includes(savedLanguage)) {
        setCurrentLanguage(savedLanguage);
      } else {
        // Detect browser language
        const browserLanguage = navigator.language.split('-')[0] as SupportedLanguage;
        const detectedLanguage = ['en', 'it', 'vec', 'to'].includes(browserLanguage)
          ? browserLanguage
          : DEFAULT_LANGUAGE;
        
        setCurrentLanguage(detectedLanguage);
         
        //salva nella localstorage
        try {
          localStorage.setItem(STORAGE_KEY, detectedLanguage);
        } catch (saveErr) {
          console.warn('Failed to save automatically detected language:', saveErr);
        }
      }
    } catch (err) {
      console.warn('Failed to load language preference:', err);
    }
  }, []);
 
  useEffect(() => {
    let isCancelled = false;

    const loadTranslations = async () => {
      console.log('Loading translations for language:', currentLanguage);

      //check  
      if (getAvailableLanguages().every(lang => lang.code !== currentLanguage)) {
        console.warn(`Unsupported language "${currentLanguage}", falling back to default "${DEFAULT_LANGUAGE}"`);
        setCurrentLanguage(DEFAULT_LANGUAGE);
        return;
      }
      
      setIsLoading(true);
      setError(null);

      try {
        let translationData: RLPFPTranslations;
        switch (currentLanguage) {
          case 'it':
            translationData = it as RLPFPTranslations;
            break;
          case 'vec':
            translationData = vec as RLPFPTranslations;
            break;
          case 'to':
            translationData = to as RLPFPTranslations;
            break;
          case 'en':
          default:
            translationData = en as RLPFPTranslations;
            break;
        }
        console.log('Loaded translations:', translationData);
        if (!isCancelled) {
          setTranslations(translationData);
        }

 
      } catch (err) {
        if (!isCancelled) {
          console.error('Error loading translations:', err);
          setError(err instanceof Error ? err.message : 'Failed to load translations');
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    loadTranslations();

    return () => {
      isCancelled = true;
    };
  }, [currentLanguage]);

  const changeLanguage = useCallback((language: SupportedLanguage) => {
    console.log('Changing language to:', language);
    setCurrentLanguage(language);
    try {
      localStorage.setItem(STORAGE_KEY, language);
    } catch (err) {
      console.warn('Failed to save language preference:', err);
    }
  }, []);

  const getAvailableLanguages = useCallback((): { code: SupportedLanguage; name: string; flag: string }[] => {
    return [
      { code: 'en', name: 'English', flag: '🇺🇸' },
      { code: 'it', name: 'Italiano', flag: '🇮🇹' },
      { code: 'vec', name: 'Veneto', flag: '🇮🇹' },
      { code: 'to', name: 'Toscano', flag: '🇮🇹' }
    ];
  }, []);

  return {
    currentLanguage,
    translations,
    isLoading,
    error,
    changeLanguage,
    getAvailableLanguages
  };
}