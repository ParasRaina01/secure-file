import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useFileUpload } from '../hooks/useFileUpload';
import { Progress } from './ui/progress';
import { Button } from './ui/button';
import { Icons } from './ui/icons';

export function FileUpload() {
  const { uploadFile, progress, error, isUploading } = useFileUpload();
  
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      await uploadFile(acceptedFiles[0]);
    }
  }, [uploadFile]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    disabled: isUploading,
  });
  
  const progressPercentage = progress
    ? Math.round((progress.uploaded / progress.total) * 100)
    : 0;
  
  return (
    <div className="w-full max-w-md mx-auto">
      <div
        {...getRootProps()}
        className={`
          p-8 border-2 border-dashed rounded-lg text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive ? 'border-primary bg-primary/5' : 'border-gray-300'}
          ${isUploading ? 'cursor-not-allowed opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          <div className="flex justify-center">
            {isUploading ? (
              <Icons.spinner className="h-10 w-10 animate-spin text-primary" />
            ) : (
              <Icons.upload className="h-10 w-10 text-gray-400" />
            )}
          </div>
          
          <div className="space-y-2">
            <p className="text-sm font-medium">
              {isDragActive
                ? 'Drop the file here'
                : 'Drag and drop a file here, or click to select'}
            </p>
            <p className="text-xs text-gray-500">
              Files will be encrypted before upload
            </p>
          </div>
          
          {!isDragActive && !isUploading && (
            <Button type="button" variant="outline" size="sm">
              Select File
            </Button>
          )}
        </div>
      </div>
      
      {isUploading && (
        <div className="mt-4 space-y-2">
          <Progress value={progressPercentage} />
          <p className="text-xs text-center text-gray-500">
            Encrypting and uploading: {progressPercentage}%
          </p>
        </div>
      )}
      
      {error && (
        <p className="mt-4 text-sm text-red-500 text-center">{error}</p>
      )}
    </div>
  );
} 