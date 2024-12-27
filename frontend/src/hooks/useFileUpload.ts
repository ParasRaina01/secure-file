import { useState } from 'react';
import { encryptFile, arrayBufferToBase64 } from '../lib/encryption';
import { api } from '../lib/api';
import { AxiosProgressEvent } from 'axios';

interface UploadProgress {
  uploaded: number;
  total: number;
}

interface UseFileUploadReturn {
  uploadFile: (file: File) => Promise<void>;
  progress: UploadProgress | null;
  error: string | null;
  isUploading: boolean;
}

export function useFileUpload(): UseFileUploadReturn {
  const [progress, setProgress] = useState<UploadProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  
  const uploadFile = async (file: File) => {
    try {
      setIsUploading(true);
      setError(null);
      setProgress({ uploaded: 0, total: file.size });
      
      // Encrypt the file
      const { encryptedFile, key, iv } = await encryptFile(file);
      
      // Create form data
      const formData = new FormData();
      formData.append('file', encryptedFile);
      formData.append('name', file.name);
      formData.append('encryption_key', arrayBufferToBase64(key));
      formData.append('encryption_iv', arrayBufferToBase64(iv));
      formData.append('mime_type', file.type);
      formData.append('size', file.size.toString());
      
      // Upload the encrypted file
      await api.post('/api/files/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent: AxiosProgressEvent) => {
          if (progressEvent.total) {
            setProgress({
              uploaded: progressEvent.loaded,
              total: progressEvent.total,
            });
          }
        },
      });
      
      setProgress({ uploaded: file.size, total: file.size });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    } finally {
      setIsUploading(false);
    }
  };
  
  return {
    uploadFile,
    progress,
    error,
    isUploading,
  };
} 