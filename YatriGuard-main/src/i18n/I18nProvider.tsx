import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { defaultLang, languages, translations, type LangCode } from './translations';

const STORAGE_KEY = 'yg.lang';

type I18nContextType = {
  lang: LangCode;
  setLang: (code: LangCode) => void;
  t: (key: string) => string;
  languages: typeof languages;
};

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [lang, setLangState] = useState<LangCode>(() => {
    const fromStorage = typeof window !== 'undefined' ? (localStorage.getItem(STORAGE_KEY) as LangCode | null) : null;
    return fromStorage && translations[fromStorage] ? fromStorage : defaultLang;
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch {}
  }, [lang]);

  const setLang = (code: LangCode) => {
    if (translations[code]) setLangState(code);
  };

  const t = useMemo(() => {
    return (key: string) => {
      const dict = translations[lang] || translations[defaultLang];
      return dict[key] ?? key;
    };
  }, [lang]);

  const value = useMemo(() => ({ lang, setLang, t, languages }), [lang, setLang, t]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
};

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error('useI18n must be used within I18nProvider');
  return ctx;
}
