import { useState } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { TopBar } from './components/layout/TopBar';
import { JulesWorkspace } from './components/jules/JulesWorkspace';
import { DataWorkspace } from './components/panels/DataWorkspace';
import { OperationalMap } from './components/map/OperationalMap';
import { CommandDashboard } from './components/panels/CommandDashboard';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <CommandDashboard setActiveTab={setActiveTab} />;
      case 'map':
        return <OperationalMap />;
      case 'data':
        return <DataWorkspace />;
      case 'jules':
        return <JulesWorkspace />;
      default:
        return <CommandDashboard setActiveTab={setActiveTab} />;
    }
  };

  return (
    <div className="flex h-screen bg-dark-900 text-gray-200 overflow-hidden bp5-dark">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
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