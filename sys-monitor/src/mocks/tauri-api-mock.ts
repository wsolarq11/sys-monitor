/**
 * Tauri API Mock for Web Mode (E2E Tests)
 * 
 * This file mocks @tauri-apps/api/core and @tauri-apps/api/event
 * to allow the app to run in web mode (Vite dev server) without Tauri.
 */

// Mock invoke function
export async function invoke<T = any>(command: string, args?: any): Promise<T> {
  console.log(`[TauriMock] invoke called: ${command}`, args);
  
  // Check for custom mocks set by tests via window.__TAURI_MOCKS__
  const customMocks = (window as any).__TAURI_MOCKS__;
  if (customMocks && customMocks[command]) {
    console.log(`[TauriMock] Using custom mock for ${command}`);
    return customMocks[command] as T;
  }
  
  // Return reasonable defaults for known commands
  if (command === 'get_system_metrics') {
    return {
      cpu_usage: 45.5,
      memory_usage: 8589934592,
      memory_total: 17179869184,
      disk_usage: 65.2,
      disk_total: 1099511627776,
      network_usage: 12.5
    } as unknown as T;
  }
  
  if (command === 'get_disk_info') {
    return {
      disks: [
        {
          name: 'C:',
          mount_point: 'C:\\',
          total_space: 1099511627776,
          available_space: 384829069721,
          is_removable: false,
          file_system: 'NTFS'
        }
      ]
    } as unknown as T;
  }
  
  if (command === 'get_process_list') {
    return [] as unknown as T;
  }
  
  if (command === 'get_network_info') {
    return {
      interfaces: []
    } as unknown as T;
  }
  
  if (command === 'get_gpu_info') {
    return null as unknown as T;
  }
  
  // Default: return empty object
  return {} as T;
}

// Mock event functions
export async function listen<T = any>(event: string, handler: (payload: T) => void): Promise<() => void> {
  console.log(`[TauriMock] listen called: ${event}`);
  // Return unlisten function
  return () => {
    console.log(`[TauriMock] Unlisten called: ${event}`);
  };
}

export async function emit(event: string, payload?: any): Promise<void> {
  console.log(`[TauriMock] emit called: ${event}`, payload);
}
