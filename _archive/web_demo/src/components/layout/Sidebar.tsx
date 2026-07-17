import React from 'react';
import { LayoutDashboard, Map as MapIcon, Settings, Code, FileText } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const { t } = useTranslation();

  return (
    <div className="w-16 md:w-64 bg-dark-800 border-r border-dark-600 flex flex-col h-full overflow-hidden transition-all duration-300 z-10">
      <div className="p-4 border-b border-dark-600 flex items-center justify-center md:justify-start">
        <div className="w-8 h-8 rounded bg-palantir-blue flex items-center justify-center font-bold text-white shadow-md">
          TS
        </div>
        <div className="ml-3 hidden md:block">
          <div className="text-sm font-bold tracking-wider">{t('app.brand')}</div>
          <div className="text-xs text-gray-400">{t('app.brandSub')}</div>
        </div>
      </div>

      <div className="flex-1 py-4 overflow-y-auto">
        <div className="px-3 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-widest hidden md:block">
          {t('nav.workspace')}
        </div>
        <nav className="space-y-1 px-2">
          <SidebarItem
            icon={<LayoutDashboard size={18} />}
            label={t('nav.dashboard')}
            active={activeTab === 'dashboard'}
            onClick={() => setActiveTab('dashboard')}
          />
          <SidebarItem
            icon={<MapIcon size={18} />}
            label={t('nav.map')}
            active={activeTab === 'map'}
            onClick={() => setActiveTab('map')}
          />
          <SidebarItem
            icon={<FileText size={18} />}
            label={t('nav.data')}
            active={activeTab === 'data'}
            onClick={() => setActiveTab('data')}
          />
        </nav>

        <div className="px-3 mt-8 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-widest hidden md:block">
          {t('nav.review')}
        </div>
        <nav className="space-y-1 px-2">
          <SidebarItem
            icon={<Code size={18} />}
            label={t('nav.evidence')}
            active={activeTab === 'review'}
            onClick={() => setActiveTab('review')}
          />
        </nav>
      </div>

      <div className="p-4 border-t border-dark-600">
        <SidebarItem
          icon={<Settings size={18} />}
          label={t('nav.settings')}
          active={activeTab === 'settings'}
          onClick={() => setActiveTab('settings')}
        />
      </div>
    </div>
  );
};

const SidebarItem = ({ icon, label, active, onClick }: { icon: React.ReactNode, label: string, active: boolean, onClick: () => void }) => {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center px-3 py-2 rounded-md transition-colors ${
        active
          ? 'bg-palantir-blue bg-opacity-20 text-palantir-blue border-l-2 border-palantir-blue'
          : 'text-gray-400 hover:bg-dark-700 hover:text-gray-200 border-l-2 border-transparent'
      }`}
    >
      <div className="flex items-center justify-center">{icon}</div>
      <span className="ml-3 text-sm font-medium hidden md:block">{label}</span>
    </button>
  );
};
