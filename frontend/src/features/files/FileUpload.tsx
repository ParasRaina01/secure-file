import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X } from 'lucide-react'
import { useDispatch } from 'react-redux'
import { AppDispatch } from '@/store'
import { uploadFile } from './filesSlice'
import { Button } from '@/components/ui/button'
import { useToast } from '@/hooks/use-toast'
import { encryptFile } from '@/lib/encryption'

interface UploadingFile {
  file: File
  progress: number
  error?: string
}

export const FileUpload: React.FC = () => {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([])
  const dispatch = useDispatch<AppDispatch>()
  const { toast } = useToast()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      progress: 0,
    }))
    setUploadingFiles(prev => [...prev, ...newFiles])

    for (let i = 0; i < acceptedFiles.length; i++) {
      const file = acceptedFiles[i]
      try {
        // Encrypt the file before uploading
        const { encryptedFile, key } = await encryptFile(file)

        // Create a new file with the original name but encrypted content
        const encryptedFileObject = new File([encryptedFile], file.name, {
          type: 'application/octet-stream',
        })

        // Update progress to show encryption is complete
        setUploadingFiles(prev =>
          prev.map((f, index) =>
            f.file === file ? { ...f, progress: 33 } : f
          )
        )

        // Upload the encrypted file
        const formData = new FormData()
        formData.append('file', encryptedFileObject)
        formData.append('encryption_key', key)
        formData.append('original_type', file.type)

        // Update progress to show upload started
        setUploadingFiles(prev =>
          prev.map((f, index) =>
            f.file === file ? { ...f, progress: 66 } : f
          )
        )

        await dispatch(uploadFile(formData)).unwrap()

        // Update progress to show completion
        setUploadingFiles(prev =>
          prev.filter(f => f.file !== file)
        )

        toast({
          title: 'Success',
          description: `${file.name} uploaded successfully`,
        })
      } catch (error: any) {
        setUploadingFiles(prev =>
          prev.map(f =>
            f.file === file
              ? { ...f, error: error.message || 'Upload failed' }
              : f
          )
        )

        toast({
          variant: 'destructive',
          title: 'Error',
          description: `Failed to upload ${file.name}`,
        })
      }
    }
  }, [dispatch, toast])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxSize: 100 * 1024 * 1024, // 100MB
  })

  const removeFile = (file: File) => {
    setUploadingFiles(prev => prev.filter(f => f.file !== file))
  }

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
        <p className="text-lg font-medium">
          {isDragActive
            ? 'Drop the files here...'
            : 'Drag & drop files here, or click to select files'}
        </p>
        <p className="text-sm text-muted-foreground mt-2">
          Files up to 100MB are supported
        </p>
      </div>

      {uploadingFiles.length > 0 && (
        <div className="mt-8 space-y-4">
          {uploadingFiles.map((uploadingFile, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-4 bg-card rounded-lg"
            >
              <div className="flex-1 mr-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">{uploadingFile.file.name}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(uploadingFile.file)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div
                    className="bg-primary rounded-full h-2 transition-all"
                    style={{ width: `${uploadingFile.progress}%` }}
                  />
                </div>
                {uploadingFile.error && (
                  <p className="text-sm text-destructive mt-1">
                    {uploadingFile.error}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
} 