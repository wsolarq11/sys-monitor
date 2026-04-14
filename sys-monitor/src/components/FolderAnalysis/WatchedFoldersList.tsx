import { useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useWatchedFoldersStore, type WatchedFolder } from '../../stores/watchedFoldersStore';
import { toast } from 'sonner';

export function WatchedFoldersList() {
  const { folders, loading, error, fetchFolders, addFolder, removeFolder, toggleActive } = 
    useWatchedFoldersStore();
  
  useEffect(() => {
    fetchFolders();
  }, []);
  
  const handleAddFolder = async () => {
    try {
      const path = await invoke<string>('select_folder');
      if (!path) return; // 用户取消选择
      
      await addFolder(path);
      toast.success('已开始监控文件夹', { 
        description: path,
        duration: 3000,
      });
    } catch (error) {
      const errorMsg = String(error);
      if (!errorMsg.includes('No folder selected')) {
        toast.error('添加失败', { 
          description: errorMsg,
          duration: 5000,
        });
      }
    }
  };
  
  const handleRemoveFolder = async (folder: WatchedFolder) => {
    const displayName = folder.alias || folder.path;
    
    try {
      await removeFolder(folder.id);
      toast.success('已停止监控', { 
        description: displayName,
        duration: 3000,
      });
    } catch (error) {
      toast.error('移除失败', { 
        description: String(error),
        duration: 5000,
      });
    }
  };
  
  const handleToggleActive = async (folder: WatchedFolder) => {
    const displayName = folder.alias || folder.path;
    
    try {
      await toggleActive(folder.id);
      const newState = !folder.is_active;
      toast.success(newState ? '已激活监控' : '已停用监控', { 
        description: displayName,
        duration: 3000,
      });
    } catch (error) {
      toast.error('切换状态失败', { 
        description: String(error),
        duration: 5000,
      });
    }
  };
  
  if (loading) {
    return (
      <div className="p-6 bg-white rounded-lg shadow">
        <div className="animate-pulse text-center text-gray-500">加载中...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-700">加载失败: {error}</p>
      </div>
    );
  }
  
  return (
    <div className="p-6 bg-white rounded-lg shadow space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">监控文件夹列表</h3>
          <p className="text-sm text-gray-500 mt-1">
            共 {folders.length} 个文件夹
          </p>
        </div>
        <button 
          onClick={handleAddFolder}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <span>+</span>
          <span>添加监控文件夹</span>
        </button>
      </div>
      
      {folders.length === 0 ? (
        <div className="p-8 text-center text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
          <p className="text-lg">暂无监控文件夹</p>
          <p className="text-sm mt-2">点击上方按钮添加要监控的文件夹</p>
        </div>
      ) : (
        <ul className="space-y-2">
          {folders.map(folder => {
            const displayName = folder.alias || folder.path;
            return (
              <li 
                key={folder.id} 
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
              >
                <div className="flex justify-between items-start gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xl" title="文件夹">📁</span>
                      <div className="font-medium text-gray-900 truncate" title={displayName}>
                        {displayName}
                      </div>
                      <span 
                        className={`px-2 py-0.5 text-xs rounded-full ${
                          folder.is_active 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        {folder.is_active ? '运行中' : '已停用'}
                      </span>
                    </div>
                    <div className="text-sm text-gray-500 mt-1 truncate" title={folder.path}>
                      {folder.path}
                    </div>
                    {folder.last_event_timestamp && (
                      <div className="text-xs text-gray-400 mt-1">
                        最后活动: {new Date(folder.last_event_timestamp * 1000).toLocaleString('zh-CN')}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleToggleActive(folder)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                        folder.is_active ? 'bg-green-600' : 'bg-gray-300'
                      }`}
                      title={folder.is_active ? '点击停用监控' : '点击激活监控'}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          folder.is_active ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                    <button
                      onClick={() => handleRemoveFolder(folder)}
                      className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="停止监控此文件夹"
                    >
                      移除
                    </button>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
