import { Navbar, NavbarGroup, NavbarHeading, NavbarDivider, Button, Alignment, Tag } from '@blueprintjs/core';
import { Search, Bell, ShieldAlert } from 'lucide-react';

export const TopBar = () => {
  return (
    <Navbar className="bp5-dark !bg-dark-900 border-b border-dark-600 shadow-sm" style={{ height: '48px' }}>
      <NavbarGroup align={Alignment.LEFT}>
        <NavbarHeading className="text-gray-300 font-semibold tracking-wide text-sm flex items-center">
          <ShieldAlert size={16} className="mr-2 text-yellow-500" />
          DISRUPTED REGIONAL TRANSPORT
        </NavbarHeading>
        <NavbarDivider />
        <Tag minimal intent="primary" className="font-mono text-xs">ENV: SIMULATION</Tag>
        <Tag minimal intent="warning" className="font-mono text-xs ml-2">STATUS: DISRUPTED</Tag>
      </NavbarGroup>
      <NavbarGroup align={Alignment.RIGHT}>
        <div className="relative flex items-center mr-4">
          <Search size={14} className="absolute left-2 text-gray-400" />
          <input
            type="text"
            placeholder="Search entities, coordinates..."
            className="bg-dark-800 border border-dark-600 text-sm rounded px-2 py-1 pl-7 text-gray-300 focus:outline-none focus:border-palantir-blue focus:ring-1 focus:ring-palantir-blue transition-colors w-64"
          />
        </div>
        <Button className="bp5-minimal" icon={<Bell size={16} />} />
        <NavbarDivider />
        <div className="flex items-center ml-2 cursor-pointer">
          <div className="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold mr-2 border border-indigo-400">
            JL
          </div>
          <span className="text-sm font-medium text-gray-300">Jules AI</span>
        </div>
      </NavbarGroup>
    </Navbar>
  );
};