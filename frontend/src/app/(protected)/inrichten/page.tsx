'use client';

import { HomeIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';

export default function InrichtenOverzichtPage() {
  return (
    <PageWrapper
      title="Inrichting — Overzicht"
      description="Overzicht van de inrichtingsstappen voor uw organisatie."
    >
      <Card>
        <EmptyState
          icon={HomeIcon}
          title="Stappen worden in de volgende fase gebouwd"
          description="Het inrichtingsoverzicht met stappen, voortgang en afhankelijkheden wordt in Fase 2 gerealiseerd."
        />
      </Card>
    </PageWrapper>
  );
}
