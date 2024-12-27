import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileText, Upload, Share2, Trash2, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from '@/components/ui/use-toast';
import { useAppDispatch, useAppSelector } from '@/app/hooks';
import { uploadFile, deleteFile, downloadFile, fetchFiles } from './filesSlice';
import { Progress } from '@/components/ui/progress';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  uploaded_at: string;
  owner: {
    id: number;
    email: string;
    full_name: string;
  };
}

interface UploadingFile {
  id: string;
  name: string;
  size: number;
  progress: number;
}

async function encryptFile(file: File): Promise<{ encryptedData: ArrayBuffer; key: ArrayBuffer; iv: Uint8Array }> {
  // Generate a random key and IV
  const key = await window.crypto.subtle.generateKey(
    { name: 'AES-CBC', length: 256 },
    true,
    ['encrypt', 'decrypt']
  );
  const iv = window.crypto.getRandomValues(new Uint8Array(16));

  // Read the file as ArrayBuffer
  const fileData = await file.arrayBuffer();

  // Encrypt the file
  const encryptedData = await window.crypto.subtle.encrypt(
    { name: 'AES-CBC', iv },
    key,
    fileData
  );

  // Export the key
  const exportedKey = await window.crypto.subtle.exportKey('raw', key);

  return {
    encryptedData,
    key: exportedKey,
    iv,
  };
}

export default function FileList() {
  const dispatch = useAppDispatch();
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const { files, isLoading } = useAppSelector((state) => state.files);

  useEffect(() => {
    dispatch(fetchFiles());
  }, [dispatch]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const newUploadingFiles = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substring(7),
      name: file.name,
      size: file.size,
      progress: 0
    }));
    
    setUploadingFiles(prev => [...prev, ...newUploadingFiles]);
    
    try {
      for (let i = 0; i < acceptedFiles.length; i++) {
        const file = acceptedFiles[i];
        const uploadingFile = newUploadingFiles[i];
        
        // Update progress for encryption
        setUploadingFiles(prev => 
          prev.map(f => 
            f.id === uploadingFile.id 
              ? { ...f, progress: 10 } 
              : f
          )
        );

        // Encrypt the file
        const { encryptedData, key, iv } = await encryptFile(file);

        // Update progress after encryption
        setUploadingFiles(prev => 
          prev.map(f => 
            f.id === uploadingFile.id 
              ? { ...f, progress: 50 } 
              : f
          )
        );

        // Create form data with encrypted file and metadata
        const formData = new FormData();
        formData.append('file', new Blob([encryptedData]), file.name);
        formData.append('name', file.name);
        formData.append('encryption_key', new Blob([key]));
        formData.append('encryption_iv', new Blob([iv]));
        formData.append('original_type', file.type);
        
        await dispatch(uploadFile(formData)).unwrap();
        
        // Update progress to 100% when done
        setUploadingFiles(prev => 
          prev.map(f => 
            f.id === uploadingFile.id 
              ? { ...f, progress: 100 } 
              : f
          )
        );
        
        // Remove completed file after a delay
        setTimeout(() => {
          setUploadingFiles(prev => prev.filter(f => f.id !== uploadingFile.id));
        }, 1000);
      }
      
      toast({
        title: 'Success',
        description: 'Files uploaded successfully!',
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error?.detail || 'Failed to upload files.',
        variant: 'destructive',
      });
      
      // Remove failed uploads
      setUploadingFiles([]);
    }
  }, [dispatch]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    maxSize: 10 * 1024 * 1024, // 10MB
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    onDropRejected: (rejectedFiles) => {
      rejectedFiles.forEach(({ file, errors }) => {
        if (errors[0]?.code === 'file-too-large') {
          toast({
            title: 'Error',
            description: `${file.name} is too large. Maximum size is 10MB.`,
            variant: 'destructive',
          });
        } else {
          toast({
            title: 'Error',
            description: `${file.name} is not a supported file type.`,
            variant: 'destructive',
          });
        }
      });
    },
  });

  const handleDelete = async (fileId: string) => {
    try {
      await dispatch(deleteFile(fileId)).unwrap();
      toast({
        title: 'Success',
        description: 'File deleted successfully!',
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error?.detail || 'Failed to delete file.',
        variant: 'destructive',
      });
    }
  };

  const handleDownload = async (fileId: string) => {
    try {
      await dispatch(downloadFile(fileId)).unwrap();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error?.detail || 'Failed to download file.',
        variant: 'destructive',
      });
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-4">Your Files</h1>
        
        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-colors duration-200 ease-in-out
            ${isDragActive ? 'border-primary bg-primary/5' : 'border-gray-300 hover:border-primary'}
          `}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          {isDragActive ? (
            <p className="mt-2 text-sm text-gray-600">Drop the files here...</p>
          ) : (
            <div>
              <p className="mt-2 text-sm text-gray-600">
                Drag and drop files here, or click to select files
              </p>
              <p className="mt-1 text-xs text-gray-500">
                Supported files: Images, PDFs, Documents (up to 10MB)
              </p>
              <p className="mt-1 text-xs text-gray-500">
                Files are encrypted before upload for your security
              </p>
            </div>
          )}
        </div>
        
        {/* Uploading Progress */}
        {uploadingFiles.length > 0 && (
          <div className="mt-4 space-y-4">
            {uploadingFiles.map((file) => (
              <div key={file.id} className="bg-white p-4 rounded-lg shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <FileText className="h-5 w-5 text-gray-400 mr-2" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{file.name}</p>
                      <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <span className="text-xs text-gray-500">
                    {file.progress < 50 ? 'Encrypting...' : file.progress < 100 ? 'Uploading...' : 'Complete'}
                  </span>
                </div>
                <Progress value={file.progress} className="h-1" />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* File List */}
      {isLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Loading files...</p>
        </div>
      ) : files.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <FileText className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No files</h3>
          <p className="mt-1 text-sm text-gray-500">Upload files to get started</p>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <ul className="divide-y divide-gray-200">
            {files.map((file: UploadedFile) => (
              <li
                key={file.id}
                className="p-4 hover:bg-gray-50 transition-colors duration-150 ease-in-out"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center min-w-0">
                    <FileText className="h-8 w-8 text-gray-400" />
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(file.size)} • Uploaded{' '}
                        {new Date(file.uploaded_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDownload(file.id)}
                      title="Download file"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {/* Open share dialog */}}
                      title="Share file"
                    >
                      <Share2 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(file.id)}
                      title="Delete file"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
} 