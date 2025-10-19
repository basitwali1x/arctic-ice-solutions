import React, { useState, useCallback, useRef } from 'react';
import { Upload, X, File, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface FileUploadProps {
  onUploadComplete?: (file: UploadedFile) => void;
  onUploadError?: (error: string) => void;
  category?: string;
  description?: string;
  locationId?: string;
  maxFileSize?: number;
  acceptedFileTypes?: string[];
}

interface UploadedFile {
  id: string;
  file_name: string;
  original_name: string;
  file_size: number;
  mime_type: string;
  category?: string;
  description?: string;
  location_id?: string;
  uploaded_by: string;
  uploaded_at: string;
}

interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  error?: string;
  uploadedFile?: UploadedFile;
}

export function FileUpload({
  onUploadComplete,
  onUploadError,
  category,
  description,
  locationId,
  maxFileSize = 10 * 1024 * 1024,
  acceptedFileTypes = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/gif',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
    'text/csv'
  ]
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    if (file.size > maxFileSize) {
      return `File size exceeds ${maxFileSize / (1024 * 1024)}MB limit`;
    }

    if (acceptedFileTypes.length > 0 && !acceptedFileTypes.includes(file.type)) {
      return `File type ${file.type} is not supported`;
    }

    return null;
  };

  const uploadFile = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setUploadingFiles(prev => [
        ...prev,
        { file, progress: 0, status: 'error', error: validationError }
      ]);
      onUploadError?.(validationError);
      return;
    }

    const uploadingFile: UploadingFile = {
      file,
      progress: 0,
      status: 'uploading'
    };

    setUploadingFiles(prev => [...prev, uploadingFile]);

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (category) formData.append('category', category);
      if (description) formData.append('description', description);
      if (locationId) formData.append('location_id', locationId);

      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          setUploadingFiles(prev =>
            prev.map(uf =>
              uf.file === file ? { ...uf, progress } : uf
            )
          );
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const uploadedFile = JSON.parse(xhr.responseText);
          setUploadingFiles(prev =>
            prev.map(uf =>
              uf.file === file
                ? { ...uf, progress: 100, status: 'success', uploadedFile }
                : uf
            )
          );
          onUploadComplete?.(uploadedFile);
        } else {
          const errorMessage = xhr.responseText || 'Upload failed';
          setUploadingFiles(prev =>
            prev.map(uf =>
              uf.file === file
                ? { ...uf, status: 'error', error: errorMessage }
                : uf
            )
          );
          onUploadError?.(errorMessage);
        }
      });

      xhr.addEventListener('error', () => {
        const errorMessage = 'Network error occurred';
        setUploadingFiles(prev =>
          prev.map(uf =>
            uf.file === file
              ? { ...uf, status: 'error', error: errorMessage }
              : uf
          )
        );
        onUploadError?.(errorMessage);
      });

      const token = localStorage.getItem('token');
      xhr.open('POST', `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/files/upload`);
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }
      xhr.send(formData);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      setUploadingFiles(prev =>
        prev.map(uf =>
          uf.file === file
            ? { ...uf, status: 'error', error: errorMessage }
            : uf
        )
      );
      onUploadError?.(errorMessage);
    }
  };

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return;

    Array.from(files).forEach(file => {
      uploadFile(file);
    });
  }, [uploadFile]);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    handleFiles(files);
  }, [handleFiles]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  }, [handleFiles]);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const removeFile = (file: File) => {
    setUploadingFiles(prev => prev.filter(uf => uf.file !== file));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      <Card
        className={`border-2 border-dashed transition-colors cursor-pointer ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Upload className="w-12 h-12 text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            Drag and drop files here
          </p>
          <p className="text-sm text-gray-500 mb-4">
            or click to browse
          </p>
          <p className="text-xs text-gray-400">
            Max file size: {maxFileSize / (1024 * 1024)}MB
          </p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            className="hidden"
            onChange={handleFileInputChange}
            accept={acceptedFileTypes.join(',')}
          />
        </CardContent>
      </Card>

      {uploadingFiles.length > 0 && (
        <div className="space-y-2">
          {uploadingFiles.map((uploadingFile, index) => (
            <Card key={index} className="p-4">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  {uploadingFile.status === 'uploading' && (
                    <File className="w-8 h-8 text-blue-500" />
                  )}
                  {uploadingFile.status === 'success' && (
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  )}
                  {uploadingFile.status === 'error' && (
                    <AlertCircle className="w-8 h-8 text-red-500" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {uploadingFile.file.name}
                    </p>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeFile(uploadingFile.file);
                      }}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>

                  <p className="text-xs text-gray-500 mb-2">
                    {formatFileSize(uploadingFile.file.size)}
                  </p>

                  {uploadingFile.status === 'uploading' && (
                    <Progress value={uploadingFile.progress} className="h-2" />
                  )}

                  {uploadingFile.status === 'success' && (
                    <Alert className="mt-2">
                      <CheckCircle className="h-4 w-4" />
                      <AlertDescription>
                        Upload complete
                      </AlertDescription>
                    </Alert>
                  )}

                  {uploadingFile.status === 'error' && (
                    <Alert variant="destructive" className="mt-2">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>
                        {uploadingFile.error || 'Upload failed'}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
