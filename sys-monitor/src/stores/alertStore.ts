import { create } from 'zustand';

/**
 * 警报级别
 */
export enum AlertLevel {
  Info = 'info',
  Warning = 'warning',
  Error = 'error',
  Critical = 'critical',
}

/**
 * 警报类型
 */
export enum AlertType {
  System = 'system',
  Disk = 'disk',
  Memory = 'memory',
  CPU = 'cpu',
  Network = 'network',
  Folder = 'folder',
  Database = 'database',
  Custom = 'custom',
}

/**
 * 警报接口
 */
export interface Alert {
  id: string;
  level: AlertLevel;
  type: AlertType;
  title: string;
  message: string;
  timestamp: number;
  resolved: boolean;
  acknowledged: boolean;
  metadata?: Record<string, any>;
}

interface AlertState {
  // 状态
  alerts: Alert[];
  unreadCount: number;
  
  // Actions - 警报管理
  addAlert: (alert: Omit<Alert, 'id' | 'timestamp' | 'resolved' | 'acknowledged'>) => void;
  resolveAlert: (id: string) => void;
  acknowledgeAlert: (id: string) => void;
  removeAlert: (id: string) => void;
  clearResolved: () => void;
  clearAll: () => void;
  
  // Actions - 批量操作
  acknowledgeAll: () => void;
  resolveAll: () => void;
  
  // Actions - 查询
  getUnresolvedAlerts: () => Alert[];
  getAlertsByLevel: (level: AlertLevel) => Alert[];
  getAlertsByType: (type: AlertType) => Alert[];
}

const ALERT_LIMIT = 100;

export const useAlertStore = create<AlertState>((set, get) => ({
  // 初始状态
  alerts: [],
  unreadCount: 0,
  
  // Actions - 警报管理
  addAlert: (alertData) => set((state) => {
    const alert: Alert = {
      ...alertData,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      resolved: false,
      acknowledged: false,
    };
    
    const newAlerts = [alert, ...state.alerts].slice(0, ALERT_LIMIT);
    return {
      alerts: newAlerts,
      unreadCount: state.unreadCount + 1,
    };
  }),
  
  resolveAlert: (id) => set((state) => ({
    alerts: state.alerts.map(alert =>
      alert.id === id ? { ...alert, resolved: true } : alert
    ),
  })),
  
  acknowledgeAlert: (id) => set((state) => {
    const alert = state.alerts.find(a => a.id === id);
    const unreadDecrease = alert && !alert.acknowledged ? 1 : 0;
    
    return {
      alerts: state.alerts.map(alert =>
        alert.id === id ? { ...alert, acknowledged: true } : alert
      ),
      unreadCount: Math.max(0, state.unreadCount - unreadDecrease),
    };
  }),
  
  removeAlert: (id) => set((state) => {
    const alert = state.alerts.find(a => a.id === id);
    const unreadDecrease = alert && !alert.acknowledged ? 1 : 0;
    
    return {
      alerts: state.alerts.filter(alert => alert.id !== id),
      unreadCount: Math.max(0, state.unreadCount - unreadDecrease),
    };
  }),
  
  clearResolved: () => set((state) => {
    const resolvedCount = state.alerts.filter(a => a.resolved && !a.acknowledged).length;
    return {
      alerts: state.alerts.filter(alert => !alert.resolved),
      unreadCount: Math.max(0, state.unreadCount - resolvedCount),
    };
  }),
  
  clearAll: () => set({ alerts: [], unreadCount: 0 }),
  
  // Actions - 批量操作
  acknowledgeAll: () => set((state) => ({
    alerts: state.alerts.map((alert) => ({ ...alert, acknowledged: true })),
    unreadCount: 0,
  })),
  
  resolveAll: () => set((state) => ({
    alerts: state.alerts.map((alert) => ({ ...alert, resolved: true })),
  })),
  
  // Actions - 查询
  getUnresolvedAlerts: () => {
    const { alerts } = get();
    return alerts.filter(alert => !alert.resolved);
  },
  
  getAlertsByLevel: (level) => {
    const { alerts } = get();
    return alerts.filter(alert => alert.level === level);
  },
  
  getAlertsByType: (type) => {
    const { alerts } = get();
    return alerts.filter(alert => alert.type === type);
  },
}));
