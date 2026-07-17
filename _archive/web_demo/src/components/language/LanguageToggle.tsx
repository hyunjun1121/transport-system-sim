import { Languages } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import type { DemoLanguage } from '../../i18n';

export const LanguageToggle = () => {
  const { i18n, t } = useTranslation();
  const currentLanguage = i18n.language === 'en' ? 'en' : 'ko';

  const setLanguage = (language: DemoLanguage) => {
    if (language !== currentLanguage) {
      void i18n.changeLanguage(language);
    }
  };

  return (
    <div className="flex items-center gap-2" aria-label={t('language.label')}>
      <Languages size={15} className="hidden text-gray-400 lg:block" aria-hidden />
      <div className="flex rounded border border-dark-600 bg-dark-800 p-0.5">
        <LanguageButton
          active={currentLanguage === 'ko'}
          label={t('language.korean')}
          shortLabel={t('language.koreanShort')}
          onClick={() => setLanguage('ko')}
        />
        <LanguageButton
          active={currentLanguage === 'en'}
          label={t('language.english')}
          shortLabel={t('language.englishShort')}
          onClick={() => setLanguage('en')}
        />
      </div>
    </div>
  );
};

const LanguageButton = ({
  active,
  label,
  shortLabel,
  onClick,
}: {
  active: boolean;
  label: string;
  shortLabel: string;
  onClick: () => void;
}) => (
  <button
    type="button"
    className={`h-7 min-w-8 rounded px-2 text-xs font-semibold transition-colors lg:min-w-16 ${
      active
        ? 'bg-palantir-blue text-white shadow-sm'
        : 'bg-transparent text-gray-300 hover:bg-dark-700 hover:text-white'
    }`}
    onClick={onClick}
  >
    <span className="hidden lg:inline">{label}</span>
    <span className="lg:hidden">{shortLabel}</span>
  </button>
);
