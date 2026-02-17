"use client";

import React, { createContext, useContext, ReactNode } from 'react';
import { RLPFPTranslations, useRLPFPTranslations, SupportedLanguage } from '../hooks/useRLPFPTranslations';

interface TranslationContextType {
  translations: RLPFPTranslations | null;
  isLoading: boolean;
  currentLanguage: SupportedLanguage;
  changeLanguage: (language: SupportedLanguage) => void;
  getAvailableLanguages: () => { code: SupportedLanguage; name: string; flag: string }[];
}

const TranslationContext = createContext<TranslationContextType | undefined>(undefined);

export function useTranslations() {
  const context = useContext(TranslationContext);
  if (context === undefined) {
    throw new Error('useTranslations must be used within a TranslationProvider');
  }
  return context;
}

interface TranslationProviderProps {
  children: ReactNode;
}

export function TranslationProvider({ children }: TranslationProviderProps) {
  const { translations, isLoading, currentLanguage, changeLanguage, getAvailableLanguages } = useRLPFPTranslations();

  return (
    <TranslationContext.Provider value={{ 
      translations, 
      isLoading, 
      currentLanguage, 
      changeLanguage, 
      getAvailableLanguages 
    }}>
      {children}
    </TranslationContext.Provider>
  );
}

//FUNZIONAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 