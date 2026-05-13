import React from 'react';
import { Card, Elevation, Tag, Button, Intent, ProgressBar } from '@blueprintjs/core';
import { Activity, ShieldAlert, FileText, CheckCircle, Clock, Zap, Map as MapIcon } from 'lucide-react';

export const CommandDashboard: React.FC<{ setActiveTab: (tab: string) => void }> = ({ setActiveTab }) => {
  return (
    <div className="p-6 h-full flex flex-col space-y-6 overflow-y-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-100 flex items-center">
            <Activity className="mr-3 text-palantir-blue" size={28} />
            Decision Support Center
          </h1>
          <p className="text-gray-400 mt-1">AI Emergency Transport Decision-Support Demo Overview</p>
        </div>
        <div className="flex space-x-3">
          <Tag intent="warning" large round icon="warning-sign">SCENARIO: DISRUPTION SAMPLE</Tag>
          <Button icon="document" text="Open Evidence View" />
        </div>
      </div>

      <Card className="bg-dark-800 border border-yellow-700/60 p-3" elevation={Elevation.ONE}>
        <p className="text-xs text-yellow-100">
          Research prototype view. This demo is not an operational route plan, real-world forecast,
          automated command system, or final acceptance record.
        </p>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Study Status" value="SCOPED DEMO" sub="Not operational routing" intent="warning" icon={<CheckCircle />} />
        <MetricCard title="Active Scenario" value="MULTIMODAL" sub="Rail-bus comparison view" intent="primary" icon={<Zap />} />
        <MetricCard title="Completion Rate" value="100.0%" sub="Sample rows only" intent="success" icon={<ShieldAlert />} />
        <MetricCard title="Makespan Delta" value="+30m" sub="multimodal vs bus sample" intent="warning" icon={<Clock />} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-[400px]">
        {/* Main Operational Overview */}
        <Card className="col-span-1 lg:col-span-2 bg-dark-800 border border-dark-600 p-0 flex flex-col shadow-lg" elevation={Elevation.TWO}>
          <div className="p-4 border-b border-dark-600 bg-dark-900 flex justify-between items-center">
            <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center">
              <MapIcon className="mr-2" size={16} />
              Simulation Pipeline Status
            </h2>
            <Button small rightIcon="arrow-right" onClick={() => setActiveTab('map')} minimal>View Map</Button>
          </div>
          <div className="p-6 flex-1 flex flex-col justify-center space-y-8">
            <PipelineStage
              name="1. Quasi-Real Data Ingestion"
              status="complete"
              details="Parsed region manifests and constraints"
            />
            <PipelineStage
              name="2. Route & Parameter Generation"
              status="complete"
              details="Generated baseline scenarios (Bus Only vs Multimodal)"
            />
            <PipelineStage
              name="3. Microsimulation Execution"
              status="complete"
              details="Loaded sample phase 1 rows for visual comparison"
            />
            <PipelineStage
              name="4. Analysis & Evidence Generation"
              status="running"
              details="Displaying scaffold evidence with final-gate caveats"
              progress={78}
            />
          </div>
        </Card>

        {/* AI Agent Summary */}
        <Card className="col-span-1 bg-dark-800 border border-dark-600 p-0 flex flex-col shadow-lg" elevation={Elevation.TWO}>
          <div className="p-4 border-b border-dark-600 bg-dark-900 flex justify-between items-center">
            <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center">
              <FileText className="mr-2" size={16} />
              Recent Intelligence
            </h2>
            <Button small rightIcon="arrow-right" onClick={() => setActiveTab('data')} minimal>View Data</Button>
          </div>
          <div className="p-4 flex-1 space-y-4">
             <div className="border border-dark-600 p-3 rounded bg-dark-900 relative overflow-hidden">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-palantir-cyan"></div>
                <h3 className="text-sm font-bold text-gray-200 mb-1">Sample: Multimodal Tradeoff</h3>
                <p className="text-xs text-gray-400 mb-2">The sample rows show multimodal routing reducing road vehicle service minutes while adding rail and transfer time. Final claims remain blocked until evidence review closes.</p>
                <div className="flex space-x-2">
                  <Tag minimal intent="primary" className="text-[10px]">demo-derived</Tag>
                  <Tag minimal className="text-[10px]">phase1_results</Tag>
                </div>
             </div>

             <div className="border border-dark-600 p-3 rounded bg-dark-900 relative overflow-hidden mt-4">
                <div className="absolute left-0 top-0 bottom-0 w-1 bg-orange-500"></div>
                <h3 className="text-sm font-bold text-gray-200 mb-1">Alert: Formal Acceptance Blocked</h3>
                <p className="text-xs text-gray-400 mb-2">Audit snapshot indicates `final_study_ready=false`. 12 gates remain blocked awaiting source-backed human review of evidence paths.</p>
                <Button small minimal intent="warning" onClick={() => setActiveTab('review')}>Open Review Workspace</Button>
             </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string;
  sub: string;
  intent: 'success' | 'primary' | 'warning' | 'danger';
  icon: React.ReactNode;
}

const MetricCard = ({ title, value, sub, intent, icon }: MetricCardProps) => {
  let color = 'text-gray-300';
  if (intent === 'success') color = 'text-green-400';
  if (intent === 'primary') color = 'text-palantir-blue';
  if (intent === 'warning') color = 'text-orange-400';

  return (
    <Card className="bg-dark-800 border border-dark-600 p-4" elevation={Elevation.ONE}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{title}</h3>
        <span className={color}>{icon}</span>
      </div>
      <div className="mt-2">
        <div className={`text-2xl font-bold font-mono ${color}`}>{value}</div>
        <div className="text-xs text-gray-500 mt-1">{sub}</div>
      </div>
    </Card>
  );
};

interface PipelineStageProps {
  name: string;
  status: 'complete' | 'running' | 'pending';
  details: string;
  progress?: number;
}

const PipelineStage = ({ name, status, details, progress }: PipelineStageProps) => {
  return (
    <div className="flex items-start">
      <div className="mr-4 flex flex-col items-center">
        <div className={`w-6 h-6 rounded-full flex items-center justify-center border-2 ${
          status === 'complete' ? 'border-green-500 bg-green-500 bg-opacity-20 text-green-500' :
          status === 'running' ? 'border-palantir-blue bg-palantir-blue bg-opacity-20 text-palantir-blue' :
          'border-gray-600 bg-transparent text-gray-600'
        }`}>
          {status === 'complete' && <CheckCircle size={12} />}
          {status === 'running' && <Activity size={12} className="animate-pulse" />}
          {status === 'pending' && <Clock size={12} />}
        </div>
      </div>
      <div className="flex-1 pb-4">
        <h3 className={`text-sm font-bold ${status === 'pending' ? 'text-gray-500' : 'text-gray-200'}`}>{name}</h3>
        <p className="text-xs text-gray-400 mt-1">{details}</p>
        {status === 'running' && progress && (
          <ProgressBar intent={Intent.PRIMARY} value={progress / 100} className="h-1 mt-3" animate />
        )}
      </div>
    </div>
  );
};
