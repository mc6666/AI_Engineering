'use client';

import { useState, useCallback } from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  rectSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import AlbumCard from './AlbumCard';
import type { Album } from '@/types';

interface SortableAlbumProps {
  album: Album;
  onDelete?: (id: number) => void;
}

function SortableAlbum({ album, onDelete }: SortableAlbumProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: album.id,
  });

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 10 : undefined,
  };

  return (
    <div ref={setNodeRef} style={style}>
      <AlbumCard album={album} onDelete={onDelete} dragHandleProps={{ ...attributes, ...listeners }} />
    </div>
  );
}

interface AlbumGridProps {
  initialAlbums: Album[];
  onDelete?: (id: number) => void;
}

export default function AlbumGrid({ initialAlbums, onDelete }: AlbumGridProps) {
  const [albumList, setAlbumList] = useState(initialAlbums);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const handleDragEnd = useCallback(async (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = albumList.findIndex((a) => a.id === active.id);
    const newIndex = albumList.findIndex((a) => a.id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;

    // Optimistic reorder
    const next = [...albumList];
    const [moved] = next.splice(oldIndex, 1);
    next.splice(newIndex, 0, moved);
    setAlbumList(next);

    const predecessor = next[newIndex - 1];
    const successor = next[newIndex + 1];
    const body: Record<string, number> = {};
    if (predecessor) body.predecessorOrder = predecessor.displayOrder;
    if (successor) body.successorOrder = successor.displayOrder;

    try {
      const res = await fetch(`/api/albums/${active.id}/reorder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        // Revert on failure
        setAlbumList(albumList);
      }
    } catch {
      setAlbumList(albumList);
    }
  }, [albumList]);

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={albumList.map((a) => a.id)} strategy={rectSortingStrategy}>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {albumList.map((album) => (
            <SortableAlbum key={album.id} album={album} onDelete={onDelete} />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}
