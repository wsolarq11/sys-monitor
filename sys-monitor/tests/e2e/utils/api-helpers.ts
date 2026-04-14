import { APIRequestContext } from '@playwright/test';

export async function setupFolderData(api: APIRequestContext, folderPath: string) {
  const response = await api.post('/api/folders', {
    data: {
      path: folderPath,
      name: folderPath.split('\\').pop() || 'Test Folder'
    }
  });
  
  return await response.json();
}

export async function cleanupFolderData(api: APIRequestContext, folderId: string) {
  await api.delete(`/api/folders/${folderId}`);
}

export async function getSystemMetrics(api: APIRequestContext) {
  const response = await api.get('/api/metrics');
  return await response.json();
}

export const mockMetrics = {
  cpu: {
    normal: { usage: 45.5 },
    high: { usage: 95.2 },
    low: { usage: 5.1 }
  },
  memory: {
    normal: { used: 8589934592, total: 17179869184 },
    high: { used: 15032385536, total: 17179869184 },
    low: { used: 2147483648, total: 17179869184 }
  },
  disk: {
    normal: { usage: 65.2, total: 1099511627776 },
    high: { usage: 95.8, total: 1099511627776 },
    low: { usage: 25.3, total: 1099511627776 }
  }
};

export const testPaths = {
  valid: [
    'C:\\Windows',
    'C:\\Program Files',
    'C:\\Users'
  ],
  invalid: [
    '',
    'Z:\\NonExistentFolder',
    'C:\\Invalid/Path\\With/Mixed\\Separators'
  ],
  special: [
    'C:\\测试文件夹\\中文路径',
    'C:\\folder with spaces',
    'C:\\very-long-folder-name-that-exceeds-normal-limits-and-tests-ui-behavior'
  ]
};
