import React from 'react';
import { CPUMonitor } from '../SystemMonitor/CPUMonitor';
import { MemoryMonitor } from '../SystemMonitor/MemoryMonitor';

export function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        SysMonitor Dashboard
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <CPUMonitor />
        <MemoryMonitor />
      </div>
    </div>
  );
}
