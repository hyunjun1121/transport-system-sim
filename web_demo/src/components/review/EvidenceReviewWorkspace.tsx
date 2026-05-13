import React from 'react';
import { Card, Elevation, Tag, ProgressBar, Button, Intent } from '@blueprintjs/core';
import {
  CheckCircle2,
  CircleDashed,
  Clock,
  FileText,
  GitBranch,
  GitCommit,
  GitMerge,
  GitPullRequest,
  Loader2,
  Play,
  ShieldAlert,
} from 'lucide-react';

export const EvidenceReviewWorkspace: React.FC = () => {
  return (
    <div className="p-6 h-full flex flex-col space-y-6 overflow-y-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-gray-100 flex items-center">
            <FileText className="mr-3 text-palantir-blue" size={28} />
            Evidence Review Workspace
          </h1>
          <p className="text-gray-400 mt-1">Non-operational review context for the Suseo-Pyeongtaek sample scenario</p>
        </div>
        <div className="flex space-x-3">
          <Tag intent="warning" large round>Review Status: IN PROGRESS</Tag>
          <Button icon={<Play size={14} />} intent="primary" text="Open Audit View" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        <Card className="flex flex-col h-full bg-dark-800 border border-dark-600 rounded-lg shadow-lg overflow-hidden p-0" elevation={Elevation.TWO}>
          <div className="p-4 border-b border-dark-600 bg-dark-900 flex justify-between items-center">
            <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center">
              <Clock className="mr-2" size={16} />
              Review Queue
            </h2>
            <Tag minimal>4 Blockers</Tag>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            <ReviewItem
              title="Public corridor and area-label evidence"
              status="running"
              progress={78}
              time="P1"
            />
            <ReviewItem
              title="Suseo and Pyeongtaek-Jije source notes"
              status="pending"
              progress={0}
            />
            <ReviewItem
              title="Parameter acceptance worksheet"
              status="pending"
              progress={0}
            />
            <ReviewItem
              title="Graph-scale decision packet"
              status="completed"
              progress={100}
              time="drafted"
            />
            <ReviewItem
              title="Formal target file hygiene"
              status="completed"
              progress={100}
              time="clean"
            />
          </div>
        </Card>

        <Card className="flex flex-col h-full bg-dark-800 border border-dark-600 rounded-lg shadow-lg overflow-hidden p-0 lg:col-span-2" elevation={Elevation.TWO}>
          <div className="p-4 border-b border-dark-600 bg-dark-900 flex justify-between items-center">
            <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center">
              <ShieldAlert className="mr-2" size={16} />
              Audit Notes
            </h2>
            <div className="flex space-x-2">
              <Tag minimal intent="warning" className="font-mono text-xs">MODE: EVIDENCE REVIEW</Tag>
              <Button minimal icon="clipboard" title="Copy Notes" />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-4 bg-[#111418] font-mono text-sm space-y-4">
            <AuditEntry time="14:02:11" type="info" message="Loaded Seoul/Suseo to Pyeongtaek-Jije support-zone demo context." />
            <AuditEntry time="14:02:12" type="note" message="Formal acceptance remains blocked until source-backed human review closes the required gates." />
            <AuditEntry time="14:02:14" type="action" message="Checking public source notes, area labels, and scenario assumptions." />
            <AuditEntry time="14:02:18" type="note" message="Simulation outputs are shown as scaffold evidence and cannot be promoted to final operational claims." />
            <AuditEntry time="14:02:22" type="action" message="Queueing follow-up review for reproducibility and graph-scale acceptance." />
            <AuditEntry time="14:02:25" type="note" message="Manuscript language must stay aligned with the accepted evidence boundary." />
            <div className="flex items-start">
              <span className="text-gray-500 mr-3 w-20 flex-shrink-0">14:02:26</span>
              <span className="text-palantir-blue font-bold mr-2">[REVIEW]</span>
              <span className="text-gray-300 flex items-center">
                <Loader2 size={14} className="animate-spin mr-2 text-gray-400" />
                Reviewing blocker traceability...
              </span>
            </div>
          </div>
        </Card>
      </div>

      <div className="h-64">
        <Card className="flex flex-col h-full bg-dark-800 border border-dark-600 rounded-lg shadow-lg overflow-hidden p-0" elevation={Elevation.TWO}>
          <div className="p-4 border-b border-dark-600 bg-dark-900 flex justify-between items-center">
            <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center">
              <GitMerge className="mr-2" size={16} />
              Review Package Context
            </h2>
            <Button small rightIcon="refresh">Refresh Snapshot</Button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 flex flex-row gap-6">
            <div className="flex-1 border border-dark-600 rounded-md p-4 bg-[#1c2127]">
              <h3 className="text-xs font-semibold text-gray-400 mb-3 uppercase flex items-center">
                <GitBranch size={14} className="mr-2" />
                Active Package
              </h3>
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-palantir-blue">Suseo-Pyeongtaek demo</span>
                <Tag intent="warning">Review only</Tag>
              </div>
              <p className="text-sm text-gray-400 mb-4">Area markers are generalized for report screenshots.</p>

              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <GitCommit size={14} className="text-gray-500 mr-2" />
                  <span className="font-mono text-xs text-gray-500 w-16">0/12</span>
                  <span className="text-gray-300 truncate">Formal acceptance gates ready</span>
                </div>
                <div className="flex items-center text-sm">
                  <GitCommit size={14} className="text-gray-500 mr-2" />
                  <span className="font-mono text-xs text-gray-500 w-16">1</span>
                  <span className="text-gray-300 truncate">Fixed scenario for the competition demo</span>
                </div>
              </div>
            </div>

            <div className="flex-1 border border-dark-600 rounded-md p-4 bg-[#1c2127]">
              <h3 className="text-xs font-semibold text-gray-400 mb-3 uppercase flex items-center">
                <GitPullRequest size={14} className="mr-2" />
                Next Reviewer Decisions
              </h3>

              <div className="border border-dark-600 rounded p-3 bg-dark-800 hover:bg-dark-700 cursor-pointer transition-colors">
                <div className="flex justify-between items-start mb-1">
                  <span className="text-sm font-semibold text-gray-200">Keep demo claims within public-data scope</span>
                  <span className="text-xs font-mono text-gray-500">P1</span>
                </div>
                <div className="flex justify-between items-center mt-2">
                  <div className="flex space-x-2">
                    <Tag minimal intent="primary" className="text-[10px]">review-needed</Tag>
                    <Tag minimal intent="warning" className="text-[10px]">not-accepted</Tag>
                  </div>
                  <div className="flex items-center text-xs text-gray-400">
                    <CheckCircle2 size={12} className="text-green-500 mr-1" />
                    Hygiene check passed
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

const ReviewItem = ({ title, status, progress, time }: { title: string, status: 'running' | 'pending' | 'completed', progress: number, time?: string }) => {
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

const AuditEntry = ({ time, type, message }: { time: string, type: 'info' | 'note' | 'action', message: string }) => {
  let color = 'text-gray-300';
  let prefix = '[SYS]';

  if (type === 'note') {
    color = 'text-purple-400';
    prefix = '[NOTE]';
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
