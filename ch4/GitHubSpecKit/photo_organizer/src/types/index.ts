export interface Album {
  id: number;
  name: string;
  date: string;
  displayOrder: number;
  coverPhotoId: number | null;
  coverThumbnailUrl: string | null;
  photoCount: number;
  createdAt: string;
}

export interface Photo {
  id: number;
  albumId: number;
  filename: string;
  imageUrl: string;
  thumbnailUrl: string;
  mimeType: string;
  sizeBytes: number;
  width: number | null;
  height: number | null;
  displayOrder: number;
  addedAt: string;
}

export interface ApiError {
  error: 'VALIDATION_ERROR' | 'NOT_FOUND' | 'PAYLOAD_TOO_LARGE' | 'INTERNAL_ERROR';
  message: string;
  field?: string;
}

export interface AlbumWithPhotos extends Album {
  photos: Photo[];
}

export type EffectType =
  | 'grayscale'
  | 'sepia'
  | 'vintage'
  | 'blur'
  | 'sharpen'
  | 'brightness'
  | 'contrast'
  | 'saturation';

export interface EffectParam {
  type: EffectType;
  intensity: number; // integer 0–100
}

export type EffectChain = EffectParam[]; // length: 0–5

export type OutputFormat = 'jpeg' | 'png';

export interface ProcessRequest {
  effects: EffectChain;
  format: OutputFormat;
}

export interface ExportRequest {
  effects: EffectChain;
  format: OutputFormat;
  photoIds?: number[];
}
