import { Navbar, NavbarGroup, NavbarHeading, NavbarDivider, Button, Alignment, Tag } from '@blueprintjs/core';
import { Search, Bell, ShieldAlert } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { LanguageToggle } from '../language/LanguageToggle';

export const TopBar = () => {
  const { t } = useTranslation();

  return (
    <Navbar className="bp5-dark !bg-dark-900 border-b border-dark-600 shadow-sm relative z-[2000]" style={{ height: '48px' }}>
      <NavbarGroup align={Alignment.LEFT} className="min-w-0 flex-1">
        <NavbarHeading className="text-gray-300 font-semibold tracking-wide text-sm flex min-w-0 items-center">
          <ShieldAlert size={16} className="mr-2 shrink-0 text-yellow-500" />
          <span className="hidden truncate sm:inline">{t('topbar.title')}</span>
          <span className="truncate sm:hidden">{t('topbar.shortTitle')}</span>
        </NavbarHeading>
        <NavbarDivider className="hidden md:block" />
        <Tag minimal intent="primary" className="hidden font-mono text-xs md:inline-flex">{t('topbar.env')}</Tag>
        <Tag minimal intent="warning" className="ml-2 hidden font-mono text-xs xl:inline-flex">{t('topbar.status')}</Tag>
      </NavbarGroup>
      <NavbarGroup align={Alignment.RIGHT} className="flex shrink-0">
        <div className="relative hidden lg:flex items-center mr-4">
          <Search size={14} className="absolute left-2 text-gray-400" />
          <input
            type="text"
            placeholder={t('topbar.search')}
            className="bg-dark-800 border border-dark-600 text-sm rounded px-2 py-1 pl-7 text-gray-300 focus:outline-none focus:border-palantir-blue focus:ring-1 focus:ring-palantir-blue transition-colors w-64"
          />
        </div>
        <LanguageToggle />
        <Button className="bp5-minimal hidden md:inline-flex" icon={<Bell size={16} />} />
        <NavbarDivider className="hidden md:block" />
        <div className="hidden items-center ml-2 cursor-pointer md:flex">
          <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold mr-2 border border-indigo-400">
            RV
          </div>
          <span className="hidden text-sm font-medium text-gray-300 lg:inline">{t('topbar.reviewMode')}</span>
        </div>
      </NavbarGroup>
    </Navbar>
  );
};
