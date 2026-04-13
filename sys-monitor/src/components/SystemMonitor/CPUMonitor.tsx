import React from 'react';
import { Card } from '../common/Card';

export function CPUMonitor() {
  return (
    <Card title="CPU Usage">
      <div className="text-4xl font-bold text-blue-600">
        0.0%
      </div>
      <div className="mt-2 text-sm text-gray-500">
        Current usage across all cores
      </div>
    </Card>
  );
}
