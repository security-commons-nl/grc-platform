'use client';

import { Cog6ToothIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';

export default function TenantPage() {
  return (
    <PageWrapper title="Tenant-instellingen">
      <Card>
        <EmptyState
          icon={Cog6ToothIcon}
          title="Tenant-configuratie wordt via de API beheerd"
          description="Gebruik de Swagger UI op /docs."
        />
      </Card>
    </PageWrapper>
  );
}
