import React, { useState, useCallback } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { documentService } from '../../services/documents';
import { Button } from '../ui/Button';

interface UploadPageProps {
  onUploadSuccess: () => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({ onUploadSuccess }) => {
  const { user } = useAuth();
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<{
    success: boolean;
    message: string;
    details?: any;
  } | null>(null);

  const validateAndSetFile = useCallback((file: File) => {
    const validation = documentService.validateFile(file);
    
    if (!validation.isValid) {
      setUploadResult({
        success: false,
        message: validation.error || 'File validation failed'
      });
      return false;
    }

    setSelectedFile(file);
    setUploadResult(null);
    return true;
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      validateAndSetFile(files[0]);
    }
  }, [validateAndSetFile]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      validateAndSetFile(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !user) return;

    setIsUploading(true);
    setUploadResult(null);

    try {
      const result = await documentService.uploadDocument(selectedFile, user.id);
      
      setUploadResult({
        success: result.success,
        message: result.message,
        details: result
      });

      if (result.success) {
        setTimeout(() => {
          onUploadSuccess();
        }, 2000);
      }
    } catch (error) {
      setUploadResult({
        success: false,
        message: error instanceof Error ? error.message : 'Upload failed'
      });
    } finally {
      setIsUploading(false);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setUploadResult(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Document</h1>
        <p className="text-gray-600">
          Upload your course materials and PDFs to enable AI-powered assistance with RAG technology
        </p>
      </div>

      {/* Upload Area */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-white/20 mb-6">
        {!selectedFile ? (
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 ${
              isDragOver
                ? 'border-blue-400 bg-blue-50 scale-105'
                : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
            }`}
          >
            <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-blue-600" />
            </div>
            
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Drop your PDF here
            </h3>
            <p className="text-gray-600 mb-6">
              or click to browse and select a file
            </p>
            
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            
            <label htmlFor="file-upload">
              <Button
                // as="span"
                variant="primary"
                size="lg"
                icon={<Upload className="w-5 h-5" />}
                className="cursor-pointer"
              >
                Choose File
              </Button>
            </label>
            
            <div className="mt-6 text-sm text-gray-500">
              <p><strong>Supported format:</strong> PDF files only</p>
              <p><strong>Maximum size:</strong> 10 MB</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Selected File */}
            <div className="flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">{selectedFile.name}</h4>
                  <p className="text-sm text-gray-600">
                    {formatFileSize(selectedFile.size)} • PDF Document
                  </p>
                </div>
              </div>
              
              <button
                onClick={clearFile}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Upload Button */}
            <div className="flex justify-center">
              <Button
                onClick={handleUpload}
                variant="primary"
                size="lg"
                isLoading={isUploading}
                disabled={isUploading}
                icon={<Upload className="w-5 h-5" />}
              >
                {isUploading ? 'Processing Document...' : 'Upload & Process'}
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Upload Result */}
      {uploadResult && (
        <div className={`p-6 rounded-xl border ${
          uploadResult.success 
            ? 'bg-green-50 border-green-200' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-start space-x-3">
            {uploadResult.success ? (
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            )}
            
            <div className="flex-1">
              <h4 className={`font-medium ${
                uploadResult.success ? 'text-green-900' : 'text-red-900'
              }`}>
                {uploadResult.success ? 'Upload Successful!' : 'Upload Failed'}
              </h4>
              
              <p className={`mt-1 text-sm ${
                uploadResult.success ? 'text-green-700' : 'text-red-700'
              }`}>
                {uploadResult.message}
              </p>

              {uploadResult.success && uploadResult.details && (
                <div className="mt-3 space-y-1 text-sm text-green-700">
                  {uploadResult.details.chunks_created && (
                    <p>✓ Created {uploadResult.details.chunks_created} text chunks</p>
                  )}
                  {uploadResult.details.text_length && (
                    <p>✓ Extracted {uploadResult.details.text_length} characters</p>
                  )}
                  <p>✓ Document is now ready for AI-powered questions</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* How it Works */}
      <div className="mt-8 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">How Document Processing Works</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Upload className="w-6 h-6 text-purple-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-1">1. Upload</h4>
            <p className="text-sm text-gray-600">
              Your PDF is securely uploaded and validated
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-1">2. Process</h4>
            <p className="text-sm text-gray-600">
              Text is extracted and split into searchable chunks
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-1">3. Ready</h4>
            <p className="text-sm text-gray-600">
              AI can now answer questions using your document
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};