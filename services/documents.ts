import { apiService } from './api';
import { API_ENDPOINTS } from '../utils/constants';
import type { CourseMaterial, DocumentUploadResponse } from '../types';

class DocumentService {
  async uploadDocument(file: File, userId: number): Promise<DocumentUploadResponse> {
    // Use the uploadFile method from apiService which sends FormData
    return apiService.uploadFile<DocumentUploadResponse>(
      API_ENDPOINTS.UPLOAD_DOCUMENT, 
      file,
      { user_id: userId }
    );
  }

  async getUserDocuments(userId: number): Promise<{ documents: CourseMaterial[] }> {
    return apiService.get<{ documents: CourseMaterial[] }>(`${API_ENDPOINTS.USER_DOCUMENTS}/${userId}`);
  }

  validateFile(file: File): { isValid: boolean; error?: string } {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf'];

    if (file.size > maxSize) {
      return { isValid: false, error: 'File size must be less than 10MB' };
    }

    if (!allowedTypes.includes(file.type)) {
      return { isValid: false, error: 'Only PDF files are allowed' };
    }

    return { isValid: true };
  }
}

export const documentService = new DocumentService();