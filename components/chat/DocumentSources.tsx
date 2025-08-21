import React from 'react';
import { FileText, ExternalLink } from 'lucide-react';

interface DocumentSourcesProps {
  sources: string[];
}

export const DocumentSources: React.FC<DocumentSourcesProps> = ({ sources }) => {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 p-4 bg-purple-50 border border-purple-200 rounded-xl">
      <div className="flex items-center space-x-2 mb-3">
        <FileText className="w-4 h-4 text-purple-600" />
        <h4 className="text-sm font-medium text-purple-900">
          Sources Used ({sources.length})
        </h4>
      </div>
      
      <div className="space-y-2">
        {sources.map((source, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-2 bg-white rounded-lg border border-purple-100"
          >
            <div className="flex items-center space-x-2">
              <FileText className="w-3 h-3 text-purple-500" />
              <span className="text-sm text-purple-800 truncate">
                {source}
              </span>
            </div>
            <button className="p-1 text-purple-400 hover:text-purple-600 transition-colors">
              <ExternalLink className="w-3 h-3" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};