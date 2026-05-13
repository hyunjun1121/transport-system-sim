import { useState } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { TopBar } from './components/layout/TopBar';
import { EvidenceReviewWorkspace } from './components/review/EvidenceReviewWorkspace';
import { DataWorkspace } from './components/panels/DataWorkspace';
import { OperationalMap } from './components/map/OperationalMap';
import { CommandDashboard } from './components/panels/CommandDashboard';

const tabs = ['dashboard', 'map', 'data', 'review'];

const getInitialTab = () => {
  const hash = window.location.hash.replace('#', '');
  return tabs.includes(hash) ? hash : 'map';
};

function App() {
  const [activeTab, setActiveTab] = useState(getInitialTab);

  const updateActiveTab = (tab: string) => {
    setActiveTab(tab);
    window.location.hash = tab;
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <CommandDashboard setActiveTab={updateActiveTab} />;
      case 'map':
        return <OperationalMap />;
      case 'data':
        return <DataWorkspace />;
      case 'review':
        return <EvidenceReviewWorkspace />;
      default:
        return <CommandDashboard setActiveTab={updateActiveTab} />;
    }
  };

  return (
    <div className="flex h-screen bg-dark-900 text-gray-200 overflow-hidden bp5-dark">
      <Sidebar activeTab={activeTab} setActiveTab={updateActiveTab} />
      <div className="flex flex-col flex-1 min-w-0">
        <TopBar />
        <main className="flex-1 overflow-auto bg-[#1c2127] relative">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default App;
