import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FileUpload } from '@/components/FileUpload';
import { Download, Trash2, File, RefreshCw } from 'lucide-react';
import { apiRequest } from '../utils/api';
import { useErrorToast } from '../hooks/useErrorToast';
import { API_BASE_URL } from '../lib/constants';

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

interface Location {
  id: string;
  name: string;
}

export function FileManager() {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [uploadCategory, setUploadCategory] = useState<string>('');
  const [uploadDescription, setUploadDescription] = useState<string>('');
  const { showError } = useErrorToast();

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedLocation) params.append('location_id', selectedLocation);
      if (selectedCategory) params.append('category', selectedCategory);

      const response = await apiRequest(`/api/files?${params.toString()}`);
      if (response) {
        const data = await response.json();
        setFiles(data);
      }
    } catch (error) {
      showError('Failed to fetch files');
    } finally {
      setLoading(false);
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await apiRequest('/api/locations');
      if (response) {
        const data = await response.json();
        setLocations(data);
      }
    } catch (error) {
      showError('Failed to fetch locations');
    }
  };

  useEffect(() => {
    fetchFiles();
    fetchLocations();
  }, [selectedLocation, selectedCategory]);

  const handleUploadComplete = (file: UploadedFile) => {
    setFiles(prev => [file, ...prev]);
  };

  const handleUploadError = (error: string) => {
    showError(error);
  };

  const handleDownload = async (fileId: string, fileName: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/files/${fileId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      showError('Failed to download file');
    }
  };

  const handleDelete = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this file?')) {
      return;
    }

    try {
      const response = await apiRequest(`/api/files/${fileId}`, {
        method: 'DELETE'
      });

      if (response) {
        setFiles(prev => prev.filter(f => f.id !== fileId));
      }
    } catch (error) {
      showError('Failed to delete file');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">File Manager</h1>
          <p className="text-gray-500 mt-1">Upload and manage files</p>
        </div>
        <Button onClick={fetchFiles} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Upload Files</CardTitle>
          <CardDescription>
            Upload files with drag-and-drop or by clicking to browse
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="upload-category">Category (Optional)</Label>
              <Input
                id="upload-category"
                placeholder="e.g., invoices, reports, photos"
                value={uploadCategory}
                onChange={(e) => setUploadCategory(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="upload-description">Description (Optional)</Label>
              <Input
                id="upload-description"
                placeholder="Brief description of the file"
                value={uploadDescription}
                onChange={(e) => setUploadDescription(e.target.value)}
              />
            </div>
          </div>

          <FileUpload
            onUploadComplete={handleUploadComplete}
            onUploadError={handleUploadError}
            category={uploadCategory}
            description={uploadDescription}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Uploaded Files</CardTitle>
          <CardDescription>
            View and manage all uploaded files
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <Label htmlFor="filter-location">Filter by Location</Label>
              <Select value={selectedLocation} onValueChange={setSelectedLocation}>
                <SelectTrigger id="filter-location">
                  <SelectValue placeholder="All Locations" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Locations</SelectItem>
                  {locations.map(location => (
                    <SelectItem key={location.id} value={location.id}>
                      {location.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <Label htmlFor="filter-category">Filter by Category</Label>
              <Input
                id="filter-category"
                placeholder="Enter category"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              />
            </div>
          </div>

          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading files...</div>
          ) : files.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No files found. Upload some files to get started.
            </div>
          ) : (
            <div className="space-y-2">
              {files.map(file => (
                <Card key={file.id} className="p-4">
                  <div className="flex items-center gap-4">
                    <File className="w-8 h-8 text-blue-500 flex-shrink-0" />
                    
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {file.original_name}
                      </p>
                      <div className="flex gap-4 text-sm text-gray-500 mt-1">
                        <span>{formatFileSize(file.file_size)}</span>
                        {file.category && <span>• {file.category}</span>}
                        <span>• Uploaded by {file.uploaded_by}</span>
                        <span>• {formatDate(file.uploaded_at)}</span>
                      </div>
                      {file.description && (
                        <p className="text-sm text-gray-600 mt-1">{file.description}</p>
                      )}
                    </div>

                    <div className="flex gap-2 flex-shrink-0">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownload(file.id, file.original_name)}
                      >
                        <Download className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(file.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
