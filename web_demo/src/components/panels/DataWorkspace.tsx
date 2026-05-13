import React, { useState, useEffect } from 'react';
import { Card, Elevation, Tag, Button, Spinner, Intent } from '@blueprintjs/core';
import { Table2, Column, Cell, SelectionModes } from '@blueprintjs/table';
import { FileText, TrendingUp, TrendingDown, Clock, ShieldAlert, BarChart2 } from 'lucide-react';
import Papa from 'papaparse';

interface SimulationData {
  s: number;
  p_fail_scale: number;
  network_variant: string;
  failure_mode: string;
  bus_makespan: number;
  multi_makespan: number;
  delta_makespan: number;
  bus_success_rate: number;
  multi_success_rate: number;
  delta_success_rate: number;
  bus_total_service_minutes: number;
  multi_total_service_minutes: number;
}

export const DataWorkspace: React.FC = () => {
  const [data, setData] = useState<SimulationData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Papa.parse('/data/phase1_results.csv', {
      download: true,
      header: true,
      dynamicTyping: true,
      complete: (results) => {
        // Filter out empty rows or malformed data and take a subset for display
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const parsedData = (results.data as any[])
          .filter(row => row.s !== undefined && row.network_variant)
          .slice(0, 100)
          .map(row => ({
            s: row.s,
            p_fail_scale: row.p_fail_scale,
            network_variant: row.network_variant,
            failure_mode: row.failure_mode,
            bus_makespan: row.bus_makespan,
            multi_makespan: row.multi_makespan,
            delta_makespan: row.delta_makespan,
            bus_success_rate: row.bus_success_rate,
            multi_success_rate: row.multi_success_rate,
            delta_success_rate: row.delta_success_rate,
            bus_total_service_minutes: row.bus_total_service_minutes,
            multi_total_service_minutes: row.multi_total_service_minutes,
          }));
        setData(parsedData);
        setLoading(false);
      },
      error: (error) => {
        console.error('Error parsing CSV:', error);
        setLoading(false);
      }
    });
  }, []);

  const cellRenderer = (key: keyof SimulationData) => (rowIndex: number) => {
    const value = data[rowIndex][key];
    let displayValue = typeof value === 'number' ? value.toFixed(2) : String(value);

    // Formatting logic for specific columns
    if (key.includes('rate')) {
        displayValue = typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : String(value);
    }

    let intentClass = '';
    if (typeof value === 'number' && key.includes('delta')) {
        if (key === 'delta_makespan') intentClass = value > 0 ? 'text-green-400' : value < 0 ? 'text-red-400' : '';
        else if (key.includes('success')) intentClass = value > 0 ? 'text-green-400' : value < 0 ? 'text-red-400' : '';
    }

    return (
      <Cell className={`bg-[#1c2127] text-gray-300 border-b border-r border-dark-600 px-3 py-1 text-sm font-mono flex items-center`}>
        <span className={`truncate w-full ${intentClass}`}>{displayValue}</span>
      </Cell>
    );
  };

  const getAverages = () => {
    if (!data.length) return null;
    const avgBusM = data.reduce((acc, curr) => acc + curr.bus_makespan, 0) / data.length;
    const avgMultiM = data.reduce((acc, curr) => acc + curr.multi_makespan, 0) / data.length;
    const avgBusS = data.reduce((acc, curr) => acc + curr.bus_success_rate, 0) / data.length;
    const avgMultiS = data.reduce((acc, curr) => acc + curr.multi_success_rate, 0) / data.length;

    return { avgBusM, avgMultiM, avgBusS, avgMultiS };
  };

  const averages = getAverages();

  return (
    <div className="p-6 h-full flex flex-col space-y-6 overflow-hidden">
      <div className="flex justify-between items-center flex-shrink-0">
        <div>
          <h1 className="text-2xl font-semibold text-gray-100 flex items-center">
            <FileText className="mr-3 text-palantir-blue" size={28} />
            Simulation Data Intelligence
          </h1>
          <p className="text-gray-400 mt-1">Phase 1 Results: Bus vs. Multimodal Resilience</p>
        </div>
        <div className="flex space-x-3">
          <Button icon="export" text="Export Selection" disabled={loading} />
          <Button icon="refresh" intent="primary" text="Reload Data" disabled={loading} />
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex justify-center items-center">
          <Spinner intent={Intent.PRIMARY} size={50} />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 flex-shrink-0">
            <MetricCard
              title="Avg Bus Makespan"
              value={`${averages?.avgBusM.toFixed(1)}m`}
              icon={<Clock className="text-orange-400" size={20} />}
              trend="Baseline"
            />
            <MetricCard
              title="Avg Multimodal Makespan"
              value={`${averages?.avgMultiM.toFixed(1)}m`}
              icon={<TrendingDown className={averages && averages.avgMultiM < averages.avgBusM ? "text-green-400" : "text-red-400"} size={20} />}
              trend={averages ? `${((averages.avgMultiM - averages.avgBusM)/averages.avgBusM * 100).toFixed(1)}%` : ""}
            />
            <MetricCard
              title="Avg Bus Success Rate"
              value={`${((averages?.avgBusS || 0) * 100).toFixed(1)}%`}
              icon={<ShieldAlert className="text-orange-400" size={20} />}
              trend="Baseline"
            />
            <MetricCard
              title="Avg Multimodal Success Rate"
              value={`${((averages?.avgMultiS || 0) * 100).toFixed(1)}%`}
              icon={<TrendingUp className={averages && averages.avgMultiS > averages.avgBusS ? "text-green-400" : (averages && averages.avgMultiS === averages.avgBusS ? "text-gray-400" : "text-red-400")} size={20} />}
              trend={averages ? `${((averages.avgMultiS - averages.avgBusS) * 100).toFixed(1)}%` : ""}
            />
          </div>

          <Card className="flex-1 bg-dark-800 border border-dark-600 rounded-lg shadow-lg overflow-hidden p-0 flex flex-col min-h-0" elevation={Elevation.TWO}>
            <div className="p-4 border-b border-dark-600 bg-dark-900 flex justify-between items-center flex-shrink-0">
              <h2 className="text-sm font-bold text-gray-300 uppercase tracking-wider flex items-center">
                <BarChart2 className="mr-2" size={16} />
                Detailed Telemetry (Top 100 rows)
              </h2>
              <Tag minimal intent="primary">{data.length} Records</Tag>
            </div>
            <div className="flex-1 bg-[#1c2127]">
              <Table2
                numRows={data.length}
                selectionModes={SelectionModes.ROWS_AND_CELLS}
                className="w-full h-full custom-bp-table"
              >
                <Column name="Congestion (s)" cellRenderer={cellRenderer('s')} />
                <Column name="Fail Scale (p)" cellRenderer={cellRenderer('p_fail_scale')} />
                <Column name="Network" cellRenderer={cellRenderer('network_variant')} />
                <Column name="Failure Mode" cellRenderer={cellRenderer('failure_mode')} />
                <Column name="Bus Time" cellRenderer={cellRenderer('bus_makespan')} />
                <Column name="Multi Time" cellRenderer={cellRenderer('multi_makespan')} />
                <Column name="Bus-Multi Time" cellRenderer={cellRenderer('delta_makespan')} />
                <Column name="Bus Success" cellRenderer={cellRenderer('bus_success_rate')} />
                <Column name="Multi Success" cellRenderer={cellRenderer('multi_success_rate')} />
                <Column name="Bus-Multi Success" cellRenderer={cellRenderer('delta_success_rate')} />
              </Table2>
            </div>
          </Card>
        </>
      )}
    </div>
  );
};

const MetricCard = ({ title, value, icon, trend }: { title: string, value: string, icon: React.ReactNode, trend: string }) => {
  return (
    <Card className="bg-dark-800 border border-dark-600 p-4" elevation={Elevation.ONE}>
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{title}</h3>
        {icon}
      </div>
      <div className="flex items-end justify-between">
        <span className="text-2xl font-bold text-gray-200 font-mono">{value}</span>
        <span className={`text-xs font-mono font-medium ${trend.includes('-') ? 'text-green-400' : (trend.includes('+') ? 'text-blue-400' : 'text-gray-500')}`}>
          {trend}
        </span>
      </div>
    </Card>
  );
};
