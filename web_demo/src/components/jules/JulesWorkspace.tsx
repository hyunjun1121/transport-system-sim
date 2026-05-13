import React from 'react';
import { Card, Elevation, Tag, ProgressBar, Button, Intent } from '@blueprintjs/core';
import { Terminal, GitBranch, GitPullRequest, GitCommit, CheckCircle2, CircleDashed, Clock, Loader2, Play, GitMerge } from 'lucide-react';

export const JulesWorkspace: React.FC = () => {
  return (
    <div className="p-6 h-full flex flex-col space-y-6 overflow-y-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-100 flex items-center">
            <Terminal className="mr-3 text-palantir-blue" size={28} />
            Jules Agent Workspace
          </h1>
          <p className="text-gray-400 mt-1">Autonomous reasoning and background task execution context</p>
        </div>
        <div className="flex space-x-3">
          <Tag intent="primary" large round>Agent Status: ACTIVE</Tag>
          <Button icon={<Play size={14} />} intent="success" text="Run Analysis" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">

        {/* Task Queue Panel */}
        <Card className="flex flex-col h-full bg-dark-800 border border-dark-600 rounded-lg shadow-lg overflow-hidden p-0" elevation={Elevation.TWO}>
          <div className="p-4 border-b border-dark-600 bg-dark-900 flex justify-between items-center">
            <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center">
              <Clock className="mr-2" size={16} />
              Task Queue
            </h2>
            <Tag minimal>4 Pending</Tag>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            <TaskItem
              title="Compile phase1_results.csv"
              status="running"
              progress={78}
              time="02:14"
            />
            <TaskItem
              title="Run multimodal baseline scenario"
              status="pending"
              progress={0}
            />
            <TaskItem
              title="Generate policy_pareto.png"
              status="pending"
              progress={0}
            />
            <TaskItem
              title="Parse config.yaml params"
              status="completed"
              progress={100}
              time="00:45"
            />
            <TaskItem
              title="Audit formal evidence paths"
              status="completed"
              progress={100}
              time="01:12"
            />
          </div>
        </Card>

        {/* Agent Reasoning Log */}
        <Card className="flex flex-col h-full bg-dark-800 border border-dark-600 rounded-lg shadow-lg overflow-hidden p-0 lg:col-span-2" elevation={Elevation.TWO}>
          <div className="p-4 border-b border-dark-600 bg-dark-900 flex justify-between items-center">
            <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center">
              <Terminal className="mr-2" size={16} />
              Reasoning Log
            </h2>
            <div className="flex space-x-2">
              <Tag minimal intent="warning" className="font-mono text-xs">MODEL: GEMINI-PRO</Tag>
              <Button minimal icon="clipboard" title="Copy Log" />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-4 bg-[#111418] font-mono text-sm space-y-4">
            <LogEntry time="14:02:11" type="info" message="Initializing transport simulation analysis..." />
            <LogEntry time="14:02:12" type="thought" message="I need to parse the results from phase1_results.csv to compare the bus_only and multimodal scenarios." />
            <LogEntry time="14:02:14" type="action" message="Executing task: Compile phase1_results.csv" />
            <LogEntry time="14:02:18" type="thought" message="The data indicates a significant delay in the bus_only scenario under disrupted conditions. I should generate a comparative visualization." />
            <LogEntry time="14:02:22" type="action" message="Queueing task: Generate policy_pareto.png" />
            <LogEntry time="14:02:25" type="thought" message="Let's also review the GitHub status for any pending PRs related to scenario configurations." />
            <div className="flex items-start">
              <span className="text-gray-500 mr-3 w-20 flex-shrink-0">14:02:26</span>
              <span className="text-palantir-blue font-bold mr-2">[JULES]</span>
              <span className="text-gray-300 flex items-center">
                <Loader2 size={14} className="animate-spin mr-2 text-gray-400" />
                Analyzing repository diffs...
              </span>
            </div>
          </div>
        </Card>

      </div>

      {/* GitHub Integration Panel */}
      <div className="h-64">
        <Card className="flex flex-col h-full bg-dark-800 border border-dark-600 rounded-lg shadow-lg overflow-hidden p-0" elevation={Elevation.TWO}>
          <div className="p-4 border-b border-dark-600 bg-dark-900 flex justify-between items-center">
            <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center">
              <GitMerge className="mr-2" size={16} />
              Source Control Context
            </h2>
            <Button small rightIcon="refresh">Sync State</Button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 flex flex-row gap-6">
            <div className="flex-1 border border-dark-600 rounded-md p-4 bg-[#1c2127]">
              <h3 className="text-xs font-semibold text-gray-400 mb-3 uppercase flex items-center">
                <GitBranch size={14} className="mr-2" />
                Active Branch
              </h3>
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-palantir-blue">feat/multimodal-resilience-eval</span>
                <Tag intent="success">Up to date</Tag>
              </div>
              <p className="text-sm text-gray-400 mb-4">Last commit 2 hours ago by Jules</p>

              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <GitCommit size={14} className="text-gray-500 mr-2" />
                  <span className="font-mono text-xs text-gray-500 w-16">a1b2c3d</span>
                  <span className="text-gray-300 truncate">Update baseline parameters for disrupted network</span>
                </div>
                <div className="flex items-center text-sm">
                  <GitCommit size={14} className="text-gray-500 mr-2" />
                  <span className="font-mono text-xs text-gray-500 w-16">e4f5g6h</span>
                  <span className="text-gray-300 truncate">Implement multimodal phase 2 caching</span>
                </div>
              </div>
            </div>

            <div className="flex-1 border border-dark-600 rounded-md p-4 bg-[#1c2127]">
              <h3 className="text-xs font-semibold text-gray-400 mb-3 uppercase flex items-center">
                <GitPullRequest size={14} className="mr-2" />
                Pending PRs
              </h3>

              <div className="border border-dark-600 rounded p-3 bg-dark-800 hover:bg-dark-700 cursor-pointer transition-colors">
                <div className="flex justify-between items-start mb-1">
                  <span className="text-sm font-semibold text-gray-200">Refine fallback route metrics</span>
                  <span className="text-xs font-mono text-gray-500">#42</span>
                </div>
                <div className="flex justify-between items-center mt-2">
                  <div className="flex space-x-2">
                    <Tag minimal intent="primary" className="text-[10px]">ai-generated</Tag>
                    <Tag minimal intent="warning" className="text-[10px]">needs-review</Tag>
                  </div>
                  <div className="flex items-center text-xs text-gray-400">
                    <CheckCircle2 size={12} className="text-green-500 mr-1" />
                    Checks passed
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

const TaskItem = ({ title, status, progress, time }: { title: string, status: 'running' | 'pending' | 'completed', progress: number, time?: string }) => {
  return (
    <div className={`p-3 rounded border ${status === 'running' ? 'border-palantir-blue bg-palantir-blue bg-opacity-10' : 'border-dark-600 bg-[#1c2127]'} transition-colors`}>
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center">
          {status === 'running' && <Loader2 size={14} className="animate-spin text-palantir-blue mr-2" />}
          {status === 'pending' && <CircleDashed size={14} className="text-gray-500 mr-2" />}
          {status === 'completed' && <CheckCircle2 size={14} className="text-green-500 mr-2" />}
          <span className={`text-sm font-medium ${status === 'completed' ? 'text-gray-400 line-through' : 'text-gray-200'}`}>{title}</span>
        </div>
        {time && <span className="text-xs font-mono text-gray-500">{time}</span>}
      </div>
      {status === 'running' && (
        <ProgressBar intent={Intent.PRIMARY} value={progress / 100} className="h-1 mt-2" animate />
      )}
    </div>
  );
};

const LogEntry = ({ time, type, message }: { time: string, type: 'info' | 'thought' | 'action', message: string }) => {
  let color = 'text-gray-300';
  let prefix = '[SYS]';

  if (type === 'thought') {
    color = 'text-purple-400';
    prefix = '[THOUGHT]';
  } else if (type === 'action') {
    color = 'text-palantir-cyan';
    prefix = '[ACTION]';
  }

  return (
    <div className="flex items-start">
      <span className="text-gray-500 mr-3 w-20 flex-shrink-0">{time}</span>
      <span className={`${type === 'info' ? 'text-gray-500' : 'text-palantir-blue'} font-bold mr-2 flex-shrink-0 w-24`}>{prefix}</span>
      <span className={color}>{message}</span>
    </div>
  );
};