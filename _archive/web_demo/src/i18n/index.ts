import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';
import { resources } from './resources';

export type DemoLanguage = 'ko' | 'en';

export const LANGUAGE_STORAGE_KEY = 'web_demo_language';

const isDemoLanguage = (value: string | null): value is DemoLanguage =>
  value === 'ko' || value === 'en';

const getInitialLanguage = (): DemoLanguage => {
  if (typeof window === 'undefined') {
    return 'ko';
  }

  const savedLanguage = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
  return isDemoLanguage(savedLanguage) ? savedLanguage : 'ko';
};

void i18next.use(initReactI18next).init({
  resources,
  lng: getInitialLanguage(),
  fallbackLng: 'ko',
  supportedLngs: ['ko', 'en'],
  interpolation: {
    escapeValue: false,
  },
});

i18next.on('languageChanged', (language) => {
  if (typeof window === 'undefined' || !isDemoLanguage(language)) {
    return;
  }

  window.localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
  window.document.documentElement.lang = language;
});

if (typeof window !== 'undefined') {
  window.document.documentElement.lang = i18next.language;
}

export default i18next;
