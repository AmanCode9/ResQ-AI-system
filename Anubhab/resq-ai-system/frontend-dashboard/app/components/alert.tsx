import { Incident } from "../page";

export default function Alerts({ incidents = [] }: { incidents: Incident[] }) {
  return (
    <div className="w-80 bg-gray-900 border-l border-gray-800 p-5 overflow-y-auto flex flex-col gap-4 shadow-xl">
      <div className="flex items-center justify-between pb-2 border-b border-gray-800">
        <h2 className="text-lg font-bold flex items-center gap-2">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
          Active Alerts
        </h2>
        <span className="text-xs font-mono bg-gray-800 text-gray-400 px-2 py-1 rounded">
          {incidents.length} EVENTS
        </span>
      </div>

      <div className="space-y-4">
        {incidents.length === 0 ? (
          <div className="text-gray-500 text-sm italic text-center animate-pulse">
            Monitoring channels... No active incidents.
          </div>
        ) : (
          incidents.map((incident) => {
            const isCritical = incident.severity === 'CRITICAL';
            const isHigh = incident.severity === 'HIGH';
            
            let colorTheme = "bg-gray-800 border-gray-600";
            if (isCritical) colorTheme = "bg-red-950/40 border-red-600";
            else if (isHigh) colorTheme = "bg-orange-950/40 border-orange-500";
            else colorTheme = "bg-yellow-950/40 border-yellow-600";

            return (
              <div 
                key={incident.id} 
                className={`border p-4 rounded-lg shadow-sm animate-in fade-in slide-in-from-right-4 duration-500 ${colorTheme}`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className={`px-2 py-1 rounded text-[10px] font-black tracking-wider uppercase ${isCritical ? 'bg-red-600' : isHigh ? 'bg-orange-600' : 'bg-yellow-600'}`}>
                    {incident.severity}
                  </span>
                  <span className="text-[10px] text-gray-400 font-mono">
                    {new Date(incident.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                
                <div className="font-semibold text-gray-100 flex items-center gap-2 mb-1 text-sm">
                  {incident.source === 'vision' ? '🚁 UAV Detect' : '📻 Comms Intercept'}
                </div>
                
                <div className="text-[11px] font-bold text-gray-300 mb-2 leading-relaxed uppercase tracking-wider">
                  {incident.status}
                </div>
                
                <div className="flex items-center text-[11px] text-gray-400 gap-1 font-mono bg-gray-950/50 p-1.5 rounded">
                  <span>📍</span> {incident.location}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}