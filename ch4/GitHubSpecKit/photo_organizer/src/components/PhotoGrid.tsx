'use client';

import PhotoTile from './PhotoTile';
import type { Photo } from '@/types';

interface PhotoGridProps {
  photos: Photo[];
  onPhotoClick: (index: number) => void;
  onPhotoDelete?: (id: number) => void;
}

export default function PhotoGrid({ photos, onPhotoClick, onPhotoDelete }: PhotoGridProps) {
  return (
    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-2">
      {photos.map((photo, index) => (
        <PhotoTile
          key={photo.id}
          thumbnailUrl={photo.thumbnailUrl}
          filename={photo.filename}
          onClick={() => onPhotoClick(index)}
          onDelete={onPhotoDelete ? () => onPhotoDelete(photo.id) : undefined}
        />
      ))}
    </div>
  );
}
