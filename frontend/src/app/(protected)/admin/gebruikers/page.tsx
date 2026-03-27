'use client';

import { UsersIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';

export default function GebruikersPage() {
  return (
    <PageWrapper title="Gebruikersbeheer">
      <Card>
        <EmptyState
          icon={UsersIcon}
          title="Gebruikersbeheer wordt via de API beheerd"
          description="Gebruik de Swagger UI op /docs."
        />
      </Card>
    </PageWrapper>
  );
}
