import { useState, useEffect, useMemo } from 'react';
import { 
  FolderKanban, DollarSign, Users, AlertTriangle, 
  TrendingUp, CheckCircle, Clock 
} from 'lucide-react';

// Componentes UI
import { KPICard } from '@/components/dashboard/KPICard';
import { ProjectsStatusChart } from '@/components/dashboard/ProjectsStatusChart';
import { BudgetChart } from '@/components/dashboard/BudgetChart';
import { CriticalProjectsTable } from '@/components/dashboard/CriticalProjectsTable';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { Skeleton } from '@/components/ui/skeleton'; // Usamos tu componente existente

// Lógica y Tipos
import { Project, formatCurrency, formatNumber } from '@/lib/mockData';
import { fetchProjects } from '@/lib/api';

export function DashboardView() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  // 1. Carga de Datos
  useEffect(() => {
    let isMounted = true;
    fetchProjects()
      .then(data => {
        if (isMounted) {
          setProjects(data);
          setLoading(false);
        }
      })
      .catch(err => console.error("Error al cargar dashboard:", err));
    
    return () => { isMounted = false; };
  }, []);

  // 2. Cálculos Optimizados (Solo se ejecutan si cambian los proyectos)
  const stats = useMemo(() => {
    const totalBudget = projects.reduce((sum, p) => sum + (p.presupuesto || 0), 0);
    const totalExecuted = projects.reduce((sum, p) => sum + (p.ejecutado || 0), 0);
    const totalBeneficiaries = projects.reduce((sum, p) => sum + (p.beneficiarios || 0), 0);
    const atRiskCount = projects.filter(p => p.status === 'en_riesgo' || p.status === 'retrasado').length;
    
    // Evitar división por cero
    const executionRate = totalBudget > 0 
      ? ((totalExecuted / totalBudget) * 100).toFixed(1) 
      : "0.0";
      
    const avgAdvance = projects.length > 0 
      ? Math.round(projects.reduce((sum, p) => sum + (p.avance || 0), 0) / projects.length) 
      : 0;

    return { 
      totalBudget, totalExecuted, totalBeneficiaries, 
      atRiskCount, executionRate, avgAdvance 
    };
  }, [projects]);

  // 3. Estado de Carga Elegante (Skeleton)
  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        {/* KPIs Skeletons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-xl" />
          ))}
        </div>
        {/* Charts Skeletons */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80 rounded-xl" />
          <Skeleton className="h-80 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="font-display text-2xl md:text-3xl font-bold text-foreground">
          Panel Ejecutivo
        </h1>
        <p className="text-muted-foreground mt-1">
          Vista consolidada del POA 2025 (Datos en Tiempo Real)
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total de Proyectos"
          value={projects.length}
          subtitle="En cartera activa"
          icon={FolderKanban}
          variant="default"
          delay={0}
        />
        <KPICard
          title="Presupuesto Total"
          value={formatCurrency(stats.totalBudget)}
          subtitle={`${stats.executionRate}% ejecutado`}
          icon={DollarSign}
          variant="success"
          delay={100}
        />
        <KPICard
          title="Beneficiarios"
          value={formatNumber(stats.totalBeneficiaries)}
          subtitle="Ciudadanos impactados"
          icon={Users}
          variant="info"
          delay={200}
        />
        <KPICard
          title="Proyectos en Riesgo"
          value={stats.atRiskCount}
          subtitle="Requieren atención"
          icon={AlertTriangle}
          variant="danger"
          delay={300}
        />
      </div>

      {/* KPIs Secundarios */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatusSummaryCard 
          icon={CheckCircle} color="text-success" bg="bg-success/10"
          value={projects.filter(p => p.status === 'completado').length} 
          label="Completados" delay="150ms" 
        />
        <StatusSummaryCard 
          icon={Clock} color="text-info" bg="bg-info/10"
          value={projects.filter(p => p.status === 'en_ejecucion').length} 
          label="En Ejecución" delay="200ms" 
        />
        <StatusSummaryCard 
          icon={TrendingUp} color="text-primary" bg="bg-primary/10"
          value={`${stats.avgAdvance}%`} 
          label="Avance Global" delay="250ms" 
        />
      </div>

      {/* Gráficas (Pasando datos reales) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ProjectsStatusChart projects={projects} />
        {/* Aquí está el componente que querías arreglar */}
        <BudgetChart projects={projects} />
      </div>

      {/* Tablas Inferiores */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <CriticalProjectsTable projects={projects} />
        </div>
        <RecentActivity projects={projects} />
      </div>
    </div>
  );
}

// Mini componente auxiliar para limpiar el código principal
function StatusSummaryCard({ icon: Icon, color, bg, value, label, delay }: any) {
  return (
    <div className="bg-card rounded-xl p-5 shadow-sm border border-border flex items-center gap-4 animate-slide-up" style={{ animationDelay: delay }}>
      <div className={`p-3 rounded-lg ${bg}`}>
        <Icon className={`h-6 w-6 ${color}`} />
      </div>
      <div>
        <p className="text-2xl font-display font-bold">{value}</p>
        <p className="text-sm text-muted-foreground">{label}</p>
      </div>
    </div>
  );
}