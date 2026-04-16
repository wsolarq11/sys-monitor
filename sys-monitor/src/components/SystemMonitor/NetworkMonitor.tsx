import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Card } from '../common/Card';

interface NetworkInterface {
  name: string;
  bytes_received: number;
  bytes_sent: number;
  download_speed: number;  // bytes/s
  upload_speed: number;    // bytes/s
}

interface NetworkData {
  interface_count: number;
  interfaces: NetworkInterface[];
}

export function NetworkMonitor() {
  const [networkData, setNetworkData] = useState<NetworkData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<{ time: number; download: number; upload: number }[]>([]);

  const fetchNetworkInfo = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await invoke<NetworkData>('get_network_info');
      setNetworkData(result);

      // Update history for chart (keep last 30 data points)
      if (result.interfaces.length > 0) {
        const primaryInterface = result.interfaces[0]; // Use first interface
        const now = Date.now();
        setHistory((prev) => {
          const newHistory = [
            ...prev,
            {
              time: now,
              download: primaryInterface.download_speed,
              upload: primaryInterface.upload_speed,
            },
          ];
          // Keep only last 30 points
          return newHistory.slice(-30);
        });
      }
    } catch (err) {
      console.error('Failed to fetch network info:', err);
      setError('获取网络信息失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchNetworkInfo();

    // Poll every 2 seconds
    const interval = setInterval(fetchNetworkInfo, 2000);
    return () => clearInterval(interval);
  }, []);

  const formatSpeed = (bytesPerSecond: number): string => {
    if (bytesPerSecond >= 1024 * 1024 * 1024) {
      return `${(bytesPerSecond / (1024 * 1024 * 1024)).toFixed(2)} GB/s`;
    } else if (bytesPerSecond >= 1024 * 1024) {
      return `${(bytesPerSecond / (1024 * 1024)).toFixed(2)} MB/s`;
    } else if (bytesPerSecond >= 1024) {
      return `${(bytesPerSecond / 1024).toFixed(2)} KB/s`;
    }
    return `${bytesPerSecond.toFixed(0)} B/s`;
  };

  const formatBytes = (bytes: number): string => {
    if (bytes >= 1024 * 1024 * 1024) {
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    } else if (bytes >= 1024 * 1024) {
      return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    } else if (bytes >= 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    }
    return `${bytes} B`;
  };

  // Simple SVG chart for network traffic
  const renderTrafficChart = () => {
    if (history.length < 2) return null;

    const width = 500;
    const height = 150;
    const padding = 20;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    const maxSpeed = Math.max(
      ...history.map((h) => Math.max(h.download, h.upload)),
      1
    );

    const getX = (index: number) => padding + (index / (history.length - 1)) * chartWidth;
    const getY = (speed: number) =>
      padding + chartHeight - (speed / maxSpeed) * chartHeight;

    // Generate path for download speed
    const downloadPath = history
      .map((h, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(h.download)}`)
      .join(' ');

    // Generate path for upload speed
    const uploadPath = history
      .map((h, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(h.upload)}`)
      .join(' ');

    return (
      <svg width={width} height={height} className="w-full">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => (
          <line
            key={ratio}
            x1={padding}
            y1={padding + chartHeight * ratio}
            x2={width - padding}
            y2={padding + chartHeight * ratio}
            stroke="#e5e7eb"
            strokeWidth="1"
          />
        ))}

        {/* Download line */}
        <path d={downloadPath} fill="none" stroke="#3b82f6" strokeWidth="2" />

        {/* Upload line */}
        <path d={uploadPath} fill="none" stroke="#10b981" strokeWidth="2" />

        {/* Legend */}
        <text x={padding} y={padding - 5} fontSize="12" fill="#3b82f6">
          ↓ Download
        </text>
        <text x={padding + 100} y={padding - 5} fontSize="12" fill="#10b981">
          ↑ Upload
        </text>
      </svg>
    );
  };

  return (
    <Card title="Network Monitor">
      {loading && !networkData && (
        <div className="text-center py-4 text-gray-500">Loading...</div>
      )}

      {error && <div className="text-center py-4 text-red-500">{error}</div>}

      {!loading && !error && networkData && networkData.interfaces.length > 0 && (
        <div>
          {/* Speed display */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-blue-50 p-3 rounded">
              <div className="text-sm text-gray-600 mb-1">↓ Download</div>
              <div className="text-2xl font-bold text-blue-600 font-mono">
                {formatSpeed(networkData.interfaces[0].download_speed)}
              </div>
            </div>
            <div className="bg-green-50 p-3 rounded">
              <div className="text-sm text-gray-600 mb-1">↑ Upload</div>
              <div className="text-2xl font-bold text-green-600 font-mono">
                {formatSpeed(networkData.interfaces[0].upload_speed)}
              </div>
            </div>
          </div>

          {/* Traffic chart */}
          {history.length > 1 && (
            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-2">Real-time Traffic (last 60s)</div>
              {renderTrafficChart()}
            </div>
          )}

          {/* Interface details */}
          <div className="border-t pt-3">
            <div className="text-sm font-medium text-gray-700 mb-2">
              Interface: {networkData.interfaces[0].name}
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-gray-500">Total Received:</span>{' '}
                <span className="font-mono">{formatBytes(networkData.interfaces[0].bytes_received)}</span>
              </div>
              <div>
                <span className="text-gray-500">Total Sent:</span>{' '}
                <span className="font-mono">{formatBytes(networkData.interfaces[0].bytes_sent)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {!loading && !error && (!networkData || networkData.interfaces.length === 0) && (
        <div className="text-center py-4 text-gray-500">No network interfaces found</div>
      )}
    </Card>
  );
}
