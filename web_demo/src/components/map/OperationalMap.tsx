import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker, Tooltip } from 'react-leaflet';
import { Card, Elevation, Button, ButtonGroup, Tag } from '@blueprintjs/core';
import { Map as MapIcon, AlertTriangle, ShieldAlert } from 'lucide-react';
import L from 'leaflet';
import yaml from 'js-yaml';

// Fix for default marker icons in react-leaflet.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

type ScenarioNode = {
  coords: [number, number];
  label: string;
  role: string;
  color: string;
  note: string;
  labelDirection: 'top' | 'right' | 'bottom' | 'left';
};

const scenarioTitle = 'Seoul/Suseo - Pyeongtaek-Jije Support Scenario';

// Public, generalized example coordinates for the competition demo. These are
// not operational pickup/drop-off points and must be presented as area-level
// decision-support markers.
const scenarioNodes: Record<string, ScenarioNode> = {
  A: {
    coords: [37.5300, 127.0300],
    label: 'Suseo Area Assembly Zone',
    role: 'Assembly',
    color: '#3b82f6',
    note: 'Generalized Seoul/Suseo-area staging marker for the demo.',
    labelDirection: 'left',
  },
  S: {
    coords: [37.4875, 127.1010],
    label: 'Suseo Rail Access Hub',
    role: 'Rail access',
    color: '#f59e0b',
    note: 'Public SRT/urban rail access area; not an operational instruction point.',
    labelDirection: 'right',
  },
  R: {
    coords: [37.0188, 127.0707],
    label: 'Pyeongtaek-Jije Transfer Area',
    role: 'Rail transfer',
    color: '#f59e0b',
    note: 'Generalized Pyeongtaek-Jije rail transfer area for the sample scenario.',
    labelDirection: 'left',
  },
  D: {
    coords: [36.9550, 127.1350],
    label: 'Pyeongtaek Support Zone',
    role: 'Destination zone',
    color: '#10b981',
    note: 'Area-level support-zone marker; not a sensitive facility location.',
    labelDirection: 'right',
  },
  D1: {
    coords: [37.3050, 127.1420],
    label: 'Road Contingency Waypoint A',
    role: 'Road waypoint',
    color: '#8b5cf6',
    note: 'Abstract waypoint used only to show corridor redundancy.',
    labelDirection: 'right',
  },
  D2: {
    coords: [37.2050, 126.9850],
    label: 'Road Contingency Waypoint B',
    role: 'Road waypoint',
    color: '#8b5cf6',
    note: 'Abstract waypoint used only to show corridor disruption sensitivity.',
    labelDirection: 'left',
  },
};

const nodeCoords = Object.fromEntries(
  Object.entries(scenarioNodes).map(([key, value]) => [key, value.coords])
) as Record<string, [number, number]>;

const customMarkerIcon = (color: string) => L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color:${color}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #1c2127; box-shadow: 0 0 6px rgba(0,0,0,0.55);"></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

export const OperationalMap: React.FC = () => {
  const [activeRoute, setActiveRoute] = useState<'bus' | 'multi'>('multi');
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [config, setConfig] = useState<any>(null);
  const isCompact = window.innerWidth < 768;

  useEffect(() => {
    fetch('/data/config.yaml')
      .then(res => res.text())
      .then(text => {
        const parsed = yaml.load(text);
        setConfig(parsed);
      })
      .catch(err => console.error('Error loading config:', err));
  }, []);

  if (!config) return null;

  const busEdges = config.network.variants.bus_single_corridor.road_links;
  const multiRoadEdges = config.network.road_links;
  const multiRailEdges = config.network.rail_link;

  return (
    <div className="h-full flex flex-col relative">
      <div className="absolute top-4 left-4 right-4 z-[1000] flex flex-col md:flex-row gap-3 justify-between pointer-events-none">
        <Card className="pointer-events-auto bg-dark-900 border border-dark-600 bg-opacity-95 p-3 flex flex-col md:flex-row md:items-center gap-3" elevation={Elevation.TWO}>
          <div className="flex items-center min-w-0">
            <MapIcon className="mr-2 text-palantir-blue flex-shrink-0" size={20} />
            <div className="min-w-0">
              <div className="font-bold text-sm text-gray-200 tracking-wider truncate">SCENARIO MAP</div>
              <div className="text-[11px] text-gray-400 truncate">{scenarioTitle}</div>
            </div>
          </div>
          <div className="hidden md:block h-8 w-px bg-dark-600"></div>
          <ButtonGroup>
            <Button
              active={activeRoute === 'bus'}
              onClick={() => setActiveRoute('bus')}
              text="Bus Only"
              small
              intent={activeRoute === 'bus' ? 'primary' : 'none'}
            />
            <Button
              active={activeRoute === 'multi'}
              onClick={() => setActiveRoute('multi')}
              text="Rail-Bus"
              small
              intent={activeRoute === 'multi' ? 'primary' : 'none'}
            />
          </ButtonGroup>
        </Card>

        <Card className="pointer-events-auto bg-dark-900 border border-dark-600 bg-opacity-95 p-3 max-w-sm" elevation={Elevation.TWO}>
          <div className="flex items-start gap-2 mb-2">
            <ShieldAlert size={14} className="text-yellow-400 mt-0.5 flex-shrink-0" />
            <p className="text-[11px] text-yellow-100 leading-snug">
              Public-data, non-operational sample. Markers are generalized area labels,
              not pickup orders, dispatch guidance, or accepted field evidence.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-1">
            <LegendDot color="#3b82f6" label="Assembly area" />
            <LegendDot color="#f59e0b" label="Rail hubs" />
            <LegendDot color="#10b981" label="Support zone" />
            <LegendDot color="#8b5cf6" label="Road waypoints" />
            {activeRoute === 'bus' && (
              <div className="col-span-2 flex items-center text-xs text-red-400 mt-1 border-t border-dark-600 pt-1">
                <AlertTriangle size={12} className="mr-1" />
                Sample road-disruption corridor
              </div>
            )}
          </div>
        </Card>
      </div>

      <div className="flex-1 w-full bg-dark-900 z-0 relative">
        <MapContainer
          center={[37.2450, 127.0850]}
          zoom={isCompact ? 8 : 9}
          style={{ height: '100%', width: '100%', backgroundColor: '#1c2127' }}
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          {activeRoute === 'bus' && busEdges.map((edge: any, i: number) => {
            const startNode = edge[0];
            const endNode = edge[1];
            if (nodeCoords[startNode] && nodeCoords[endNode]) {
              return (
                <Polyline
                  key={`bus-${i}`}
                  positions={[nodeCoords[startNode], nodeCoords[endNode]]}
                  color="#ef4444"
                  weight={4}
                  dashArray="8, 8"
                  opacity={0.82}
                />
              );
            }
            return null;
          })}

          {activeRoute === 'multi' && (
            <>
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
              {multiRoadEdges.map((edge: any, i: number) => {
                const startNode = edge[0];
                const endNode = edge[1];
                if (nodeCoords[startNode] && nodeCoords[endNode]) {
                  return (
                    <Polyline
                      key={`multi-road-${i}`}
                      positions={[nodeCoords[startNode], nodeCoords[endNode]]}
                      color="#3b82f6"
                      weight={3}
                      opacity={0.72}
                      dashArray="4, 6"
                    />
                  );
                }
                return null;
              })}
              {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
              {multiRailEdges.map((edge: any, i: number) => {
                const startNode = edge[0];
                const endNode = edge[1];
                if (nodeCoords[startNode] && nodeCoords[endNode]) {
                  return (
                    <Polyline
                      key={`multi-rail-${i}`}
                      positions={[nodeCoords[startNode], nodeCoords[endNode]]}
                      color="#14b8a6"
                      weight={5}
                      opacity={0.9}
                    />
                  );
                }
                return null;
              })}
            </>
          )}

          {config.network.nodes.map((nodeId: string) => {
            const node = scenarioNodes[nodeId];
            if (!node) return null;
            return (
              <Marker key={nodeId} position={node.coords} icon={customMarkerIcon(node.color)}>
                <Tooltip direction={node.labelDirection} offset={[0, 0]} opacity={0.92} permanent={!isCompact}>
                  <span className="font-sans text-[11px]">{node.label}</span>
                </Tooltip>
                <Popup className="dark-popup">
                  <div className="p-1 font-sans">
                    <div className="font-bold text-sm mb-1">{node.label}</div>
                    <div className="text-xs text-gray-500 mb-1">{node.role}</div>
                    <div className="text-xs text-gray-500">{node.note}</div>
                    <div className="text-[11px] text-gray-500 font-mono mt-1">
                      Example coords: {node.coords[0]}, {node.coords[1]}
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}

          {activeRoute === 'multi' && (
            <>
              <CircleMarker center={[37.4550, 127.0960]} radius={4} pathOptions={{ color: '#14b8a6', fillColor: '#14b8a6', fillOpacity: 1 }} />
              <CircleMarker center={[37.2500, 127.0840]} radius={4} pathOptions={{ color: '#14b8a6', fillColor: '#14b8a6', fillOpacity: 1 }} />
              <CircleMarker center={[37.0600, 127.0730]} radius={4} pathOptions={{ color: '#14b8a6', fillColor: '#14b8a6', fillOpacity: 1 }} />
            </>
          )}
        </MapContainer>
      </div>

      <div className="absolute bottom-4 left-4 right-4 z-[1000] pointer-events-none">
        <Card className="pointer-events-auto bg-dark-900 border border-dark-600 bg-opacity-95 p-0 overflow-hidden" elevation={Elevation.TWO}>
          <div className="grid grid-cols-1 md:grid-cols-4 text-xs font-mono">
            <TelemetryCell
              label="ACTIVE SCENARIO"
              value={activeRoute === 'multi' ? 'Rail-Bus public sample' : 'Bus-only road sample'}
              valueClass="text-palantir-blue"
            />
            <TelemetryCell
              label="SAMPLE MAKESPAN"
              value={activeRoute === 'multi' ? '675.0m demo' : '645.0m demo'}
              valueClass="text-gray-200"
            />
            <TelemetryCell
              label="ROAD SERVICE MINUTES"
              value={activeRoute === 'multi' ? '577.1m demo' : '1150.3m demo'}
              valueClass={activeRoute === 'multi' ? 'text-green-400' : 'text-orange-400'}
            />
            <div className="p-3 flex justify-between items-center min-w-0">
              <div className="min-w-0">
                <div className="text-gray-500 mb-1">EVIDENCE BOUNDARY</div>
                <div className="text-yellow-100 truncate">non-operational scaffold</div>
              </div>
              <Tag minimal intent="warning">sample</Tag>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

const LegendDot = ({ color, label }: { color: string; label: string }) => (
  <div className="flex items-center text-xs text-gray-300">
    <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: color }}></div>
    {label}
  </div>
);

const TelemetryCell = ({ label, value, valueClass }: { label: string; value: string; valueClass: string }) => (
  <div className="p-3 border-b md:border-b-0 md:border-r border-dark-600 min-w-0">
    <div className="text-gray-500 mb-1 truncate">{label}</div>
    <div className={`${valueClass} font-bold truncate`}>{value}</div>
  </div>
);
