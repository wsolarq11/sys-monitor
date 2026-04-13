import React from 'react';
import { Card } from '../common/Card';

function formatBytes(bytes: number): string {
  const gb = bytes / (1024 * 1024 * 1024);
  return `${gb.toFixed(2)} GB`;
}

export function MemoryMonitor() {
  return (
    <Card title="Memory Usage">
      <div className="text-4xl font-bold text-green-600">
        0.00 GB
      </div>
      <div className="mt-2 text-sm text-gray-500">
        System memory in use
      </div>
    </Card>
  );
}
