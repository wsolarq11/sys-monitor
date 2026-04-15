import { useEffect } from 'react';
import { useAlertStore } from '../stores/alertStore';
import { toast } from 'sonner';

// 检测是否在 Tauri 环境中
const isTauri = () => {
  return typeof window !== 'undefined' && 
         '__TAURI_INTERNALS__' in window || '__TAURI__' in window;
};

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
    // 在非 Tauri 环境中跳过文件夹监听
    if (!isTauri()) {
      console.log('[useFolderWatcher] 非 Tauri 环境,跳过文件夹监听');
      return;
    }

    // 动态导入 Tauri 模块
    const setupListener = async () => {
      try {
        const { listen } = await import('@tauri-apps/api/event');
        const { AlertLevel, AlertType } = await import('../stores/alertStore');

        const unlistenAggregated = await listen<AggregatedChangeEvent>('folder-change-aggregated', async (event) => {
          const { folder_path, summary, detail, sample_files, delete_count } = event.payload;
          
          const alertLevel = delete_count > 0 ? AlertLevel.Warning : AlertLevel.Info;
          addAlert({
            level: alertLevel,
            type: AlertType.Folder,
            title: `\ud83d\udcc1 ${folder_path.split('/').pop() || folder_path}`,
            message: `${summary}${detail}`,
            metadata: {
              folderPath: folder_path,
              sampleFiles: sample_files,
              totalCount: event.payload.total_count,
            },
          });
          
          showAggregatedToast(event.payload);
        });
        
        return unlistenAggregated;
      } catch (error) {
        console.error('[useFolderWatcher] 设置监听器失败:', error);
      }
    };

    let cleanupFn: (() => void) | undefined;
    
    setupListener().then(cleanup => {
      cleanupFn = cleanup;
    });
    
    return () => {
      if (cleanupFn) {
        cleanupFn();
      }
    };
  }, [addAlert]);
}

function showAggregatedToast(data: AggregatedChangeEvent) {
  const { folder_path, summary, sample_files, total_count } = data;
  
  const folderName = folder_path.split(/[\\/]/).pop() || folder_path;
  
  let description = summary;
  if (sample_files.length > 0) {
    description += `\n\u793a\u4f8b: ${sample_files.map((f: string) => f.split(/[\\/]/).pop()).join(', ')}`;
  }
  
  toast(`${folderName} - ${total_count} \u4e2a\u6587\u4ef6\u53d8\u5316`, {
    description,
    duration: 6000,
  });
}
