import { Incident } from "../page";

export default function IncidentViewer({ incident }: { incident: Incident }) {
  const isCritical = incident.severity === 'CRITICAL';
  const isHigh = incident.severity === 'HIGH';
  const isModerate = incident.severity === 'MODERATE';

  let borderColor = "border-gray-700";
  let bgGradient = "from-gray-900 to-gray-950";
  let textColor = "text-gray-400";
  let alertIcon = "✅";

  if (isCritical) {
    borderColor = "border-red-600";
    bgGradient = "from-red-950/60 to-gray-950";
    textColor = "text-red-400";
    alertIcon = "🚨";
  } else if (isHigh) {
    borderColor = "border-orange-500";
    bgGradient = "from-orange-950/60 to-gray-950";
    textColor = "text-orange-400";
    alertIcon = "⚠️";
  } else if (isModerate) {
    borderColor = "border-yellow-500";
    bgGradient = "from-yellow-950/60 to-gray-950";
    textColor = "text-yellow-400";
    alertIcon = "👀";
  }

  return (
    <div className={`w-full max-w-2xl border-2 rounded-2xl p-8 bg-gradient-to-br shadow-2xl animate-in flip-in-y zoom-in-95 duration-700 ${borderColor} ${bgGradient}`}>
      <div className="flex justify-between items-start border-b border-gray-800 pb-4 mb-6">
        <div>
          <h2 className="text-3xl font-black text-white tracking-wider flex items-center gap-3">
            <span className="text-4xl animate-pulse">{alertIcon}</span>
            NEW INCIDENT DETECTED
          </h2>
          <div className={`mt-2 text-sm font-bold tracking-widest uppercase ${textColor}`}>
            System Status: {incident.status}
          </div>
        </div>
        <div className="text-right">
          <div className={`px-4 py-1.5 rounded-full font-black text-sm uppercase ${
            isCritical ? 'bg-red-600 text-white shadow-[0_0_15px_rgba(220,38,38,0.6)]' : 
            isHigh ? 'bg-orange-600 text-white shadow-[0_0_15px_rgba(234,88,12,0.6)]' : 
            'bg-yellow-600 text-white shadow-[0_0_15px_rgba(202,138,4,0.6)]'
          }`}>
            SEVERITY: {incident.severity}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-8">
        <div className="space-y-6">
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Location / Zone</div>
            <div className="text-xl font-medium text-gray-200">
              📍 {incident.location}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Data Source</div>
            <div className="text-base font-mono text-gray-300 bg-gray-900 px-3 py-2 rounded inline-block border border-gray-800">
              {incident.source === 'nlp' ? '📻 Comms Intercept (NLP)' : '🚁 UAV Vision Feed (YOLOv8)'}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Time of Intercept</div>
            <div className="text-lg font-mono text-gray-300">
              {new Date(incident.timestamp).toLocaleString()}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Intercept ID</div>
            <div className="text-sm font-mono text-gray-500">
              {incident.id}
            </div>
          </div>
        </div>
      </div>
      
      {/* Footer / decorative grid lines */}
      <div className="mt-8 pt-4 border-t border-dashed border-gray-800 flex justify-between items-center opacity-50">
        <div className="font-mono text-xs text-gray-600">RESQ-AI // COMMAND // AUTO-GENERATED</div>
        <div className="font-mono text-xs text-gray-600 animate-pulse">● REC</div>
      </div>
    </div>
  );
}
