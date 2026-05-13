import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
import { Card, Elevation, Button, ButtonGroup } from '@blueprintjs/core';
import { Map as MapIcon, AlertTriangle } from 'lucide-react';
import L from 'leaflet';
import yaml from 'js-yaml';

// Fix for default marker icons in react-leaflet
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const customMarkerIcon = (color: string) => L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color:${color}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid #1c2127; box-shadow: 0 0 4px rgba(0,0,0,0.5);"></div>`,
  iconSize: [12, 12],
  iconAnchor: [6, 6]
});

// Since the config only provides edge definitions without coordinates, we use a mapping to attach generic coordinates
const nodeCoords: Record<string, [number, number]> = {
  A: [37.5665, 126.9780],
  S: [37.5500, 127.0000],
  R: [37.3500, 127.1000],
  D: [37.3000, 127.1500],
  D1: [37.4500, 127.0500],
  D2: [37.4000, 126.9000]
};

const nodeColors: Record<string, string> = {
  A: '#3b82f6', // Blue
  S: '#f59e0b', // Yellow
  R: '#f59e0b', // Yellow
  D: '#10b981', // Green
  D1: '#8b5cf6', // Purple
  D2: '#8b5cf6'  // Purple
};

export const OperationalMap: React.FC = () => {
  const [activeRoute, setActiveRoute] = useState<'bus' | 'multi'>('multi');
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [config, setConfig] = useState<any>(null);

  useEffect(() => {
    fetch('/data/config.yaml')
      .then(res => res.text())
      .then(text => {
        const parsed = yaml.load(text);
        setConfig(parsed);
      })
      .catch(err => console.error("Error loading config:", err));
  }, []);

  if (!config) return null;

  // Extract edges from parsed config.yaml
  const busEdges = config.network.variants.bus_single_corridor.road_links;
  const multiRoadEdges = config.network.road_links;
  const multiRailEdges = config.network.rail_link;

  return (
    <div className="h-full flex flex-col relative">
      {/* Map Header Overlay */}
      <div className="absolute top-4 left-4 right-4 z-[1000] flex justify-between pointer-events-none">
        <Card className="pointer-events-auto bg-dark-900 border border-dark-600 bg-opacity-90 p-3 flex items-center space-x-4" elevation={Elevation.TWO}>
          <div className="flex items-center">
            <MapIcon className="mr-2 text-palantir-blue" size={20} />
            <span className="font-bold text-sm text-gray-200 tracking-wider">SCENARIO MAP</span>
          </div>
          <div className="h-6 w-px bg-dark-600"></div>
          <ButtonGroup>
            <Button
              active={activeRoute === 'bus'}
              onClick={() => setActiveRoute('bus')}
              text="Bus Only (Disrupted)"
              small
              intent={activeRoute === 'bus' ? 'primary' : 'none'}
            />
            <Button
              active={activeRoute === 'multi'}
              onClick={() => setActiveRoute('multi')}
              text="Multimodal (Active)"
              small
              intent={activeRoute === 'multi' ? 'primary' : 'none'}
            />
          </ButtonGroup>
        </Card>

        <Card className="pointer-events-auto bg-dark-900 border border-dark-600 bg-opacity-90 p-3" elevation={Elevation.TWO}>
          <div className="flex flex-col space-y-2">
            <div className="flex items-center text-xs text-gray-300">
              <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
              Assembly
            </div>
            <div className="flex items-center text-xs text-gray-300">
              <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div>
              Rail Transfer
            </div>
            <div className="flex items-center text-xs text-gray-300">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
              Destination
            </div>
            {activeRoute === 'bus' && (
              <div className="flex items-center text-xs text-red-400 mt-1 border-t border-dark-600 pt-1">
                <AlertTriangle size={12} className="mr-1" />
                Scenario Congestion
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Map Container */}
      <div className="flex-1 w-full bg-dark-900 z-0 relative">
        <MapContainer
          center={[37.4500, 127.0500]}
          zoom={11}
          style={{ height: '100%', width: '100%', backgroundColor: '#1c2127' }}
          zoomControl={false}
        >
          {/* Dark Matter Tile Layer */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {/* Render Routes based on parsed config selection */}
          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
          {activeRoute === 'bus' && busEdges.map((edge: any, i: number) => {
            const startNode = edge[0];
            const endNode = edge[1];
            if (nodeCoords[startNode] && nodeCoords[endNode]) {
              return (
                <Polyline
                  key={`bus-${i}`}
                  positions={[nodeCoords[startNode], nodeCoords[endNode]]}
                  color="#ef4444" // Red for disrupted bus route
                  weight={4}
                  dashArray="8, 8"
                  opacity={0.8}
                />
              )
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
                       opacity={0.7}
                       dashArray="4, 6"
                     />
                   )
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
                   )
                 }
                 return null;
              })}
            </>
          )}

          {/* Render Nodes parsed from config */}
          {config.network.nodes.map((nodeId: string) => {
             const coords = nodeCoords[nodeId];
             if (!coords) return null;
             const color = nodeColors[nodeId] || '#cbd5e1';
             return (
              <Marker key={nodeId} position={coords} icon={customMarkerIcon(color)}>
                <Popup className="dark-popup">
                  <div className="p-1 font-sans">
                    <div className="font-bold text-sm mb-1">Node {nodeId}</div>
                    <div className="text-xs text-gray-500 font-mono">Coords: {coords[0]}, {coords[1]}</div>
                  </div>
                </Popup>
              </Marker>
             )
          })}

          {/* Add some abstract moving entities for the active route to simulate operation */}
          {activeRoute === 'multi' && (
            <>
              <CircleMarker center={[37.5200, 126.9900]} radius={4} pathOptions={{ color: '#14b8a6', fillColor: '#14b8a6', fillOpacity: 1 }} />
              <CircleMarker center={[37.4500, 127.0500]} radius={4} pathOptions={{ color: '#14b8a6', fillColor: '#14b8a6', fillOpacity: 1 }} />
              <CircleMarker center={[37.3800, 127.0800]} radius={4} pathOptions={{ color: '#14b8a6', fillColor: '#14b8a6', fillOpacity: 1 }} />
            </>
          )}
        </MapContainer>
      </div>

      {/* Bottom Telemetry Overlay */}
      <div className="absolute bottom-4 left-4 right-4 z-[1000] pointer-events-none">
        <Card className="pointer-events-auto bg-dark-900 border border-dark-600 bg-opacity-90 p-0 overflow-hidden" elevation={Elevation.TWO}>
           <div className="flex items-center text-xs font-mono">
              <div className="flex-1 p-3 border-r border-dark-600">
                 <div className="text-gray-500 mb-1">ACTIVE SCENARIO</div>
                 <div className="text-palantir-blue font-bold">{activeRoute === 'multi' ? 'Multimodal Resilience Baseline' : 'Bus Only Disrupted Baseline'}</div>
              </div>
              <div className="flex-1 p-3 border-r border-dark-600">
                 <div className="text-gray-500 mb-1">SAMPLE MAKESPAN</div>
                 <div className="text-gray-200">{activeRoute === 'multi' ? '675.0m (sample)' : '645.0m (sample)'}</div>
              </div>
              <div className="flex-1 p-3 border-r border-dark-600">
                 <div className="text-gray-500 mb-1">NETWORK CONGESTION</div>
                 <div className={activeRoute === 'multi' ? 'text-yellow-400' : 'text-red-400'}>{activeRoute === 'multi' ? 'Moderate (Rail Bypass)' : 'Severe (Gridlock)'}</div>
              </div>
              <div className="flex-1 p-3 flex justify-between items-center">
                 <div>
                   <div className="text-gray-500 mb-1">COMPLETION RATE</div>
                   <div className="text-green-400">100.0% sample</div>
                 </div>
                 <Button rightIcon="arrow-right" intent="primary" minimal>View Details</Button>
              </div>
           </div>
        </Card>
      </div>
    </div>
  );
};
