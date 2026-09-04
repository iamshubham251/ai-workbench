import React from 'react';
import { UploadCloud } from 'lucide-react';

export const UploadDropzone: React.FC = () => {
  return (
    <div className="upload-dropzone">
      <UploadCloud className="upload-icon" size={48} />
      <div className="upload-title">Drop a document here</div>
      <div className="upload-subtitle">or browse files</div>
      <div className="upload-formats">Accepted formats: PDF, DOCX, XLSX, PPTX</div>
    </div>
  );
};
