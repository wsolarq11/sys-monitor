import { useEffect } from 'react';
import { listen } from '@tauri-apps/api/event';
import { useAlertStore, AlertLevel, AlertType } from '../stores/alertStore';
import { toast } from 'sonner';

interface AggregatedChangeEvent {
  folder_id: number;
  folder_path: string;
  create_count: number;
  delete_count: number;
  modify_count: number;
  total_count: number;
  summary: string;
  detail: string;
  sample_files: string[];
  timestamp: number;
}

export function useFolderWatcher() {
  const addAlert = useAlertStore(state => state.addAlert);
  
  useEffect(() => {
    // 请求通知权限
    const checkPermission = async () => {
      let permissionGranted = await isPermissionGranted();
      if (!permissionGranted) {
        const permission = await requestPermission();
        permissionGranted = permission === 'granted';
      }
      return permissionGranted;
    };
    
    // 监听聚合的文件变化事件
    const unlistenAggregated = listen<AggregatedChangeEvent>('folder-change-aggregated', async (event) => {
      const { folder_path, summary, detail, sample_files, delete_count } = event.payload;
      
      // 1. 添加到警报store
      const alertLevel = delete_count > 0 ? AlertLevel.Warning : AlertLevel.Info;
      addAlert({
        level: alertLevel,
        type: AlertType.Folder,
        title: `📁 ${folder_path.split('/').pop() || folder_path}`,
        message: `${summary}${detail}`,
        metadata: {
          folderPath: folder_path,
          sampleFiles: sample_files,
          totalCount: event.payload.total_count,
        },
      });
      
      // 2. 显示Toast通知(智能聚合)
      showAggregatedToast(event.payload);
      
      // 3. 发送Tauri系统通知
      const permissionGranted = await checkPermission();
      if (permissionGranted) {
        const folderName = folder_path.split(/[\\/]/).pop() || folder_path;
        sendNotification({
          title: `${folderName} - 文件变化`,
          body: summary,
        });
      }
    });
    
    return () => {
      unlistenAggregated.then(fn => fn());
    };
  }, [addAlert]);
}

function showAggregatedToast(data: AggregatedChangeEvent) {
  const { folder_path, summary, sample_files, total_count } = data;
  
  const folderName = folder_path.split(/[\\/]/).pop() || folder_path;
  
  let description = summary;
  if (sample_files.length > 0) {
    description += `\n示例: ${sample_files.map(f => f.split(/[\\/]/).pop()).join(', ')}`;
  }
  
  toast(`${folderName} - ${total_count} 个文件变化`, {
    description,
    duration: 6000,
  });
}
}
