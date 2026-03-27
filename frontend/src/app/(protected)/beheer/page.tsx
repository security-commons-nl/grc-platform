'use client';

import { ChartBarSquareIcon } from '@heroicons/react/24/outline';
import { PageWrapper } from '@/components/layout/page-wrapper';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';

export default function BeheerDashboardPage() {
  return (
    <PageWrapper
      title="Beheer — Dashboard"
      description="Centrale overzichtspagina voor governance, risico en compliance."
    >
      <Card>
        <EmptyState
          icon={ChartBarSquareIcon}
          title="Dashboard wordt in de volgende fase gebouwd"
          description="Het beheerdashboard met KPI's, scores en grafieken wordt in Fase 2 gerealiseerd."
        />
      </Card>
    </PageWrapper>
  );
}
