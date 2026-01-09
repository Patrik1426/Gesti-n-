import { useState, useEffect } from 'react';
import { 
  FolderKanban, 
  DollarSign, 
  Users, 
  AlertTriangle,
  TrendingUp,
  Clock
} from 'lucide-react';
import { fetchProjects } from '@/lib/api'; // Conexión real
import { Project } from '@/lib/mockData'; // Solo la interfaz (tipo)
import { KPICard } from '@/components/dashboard/KPICard';
import { ProjectsStatusChart } from '@/components/dashboard/ProjectsStatusChart';
import { BudgetChart } from '@/components/dashboard/BudgetChart';
import { CriticalProjectsTable } from '@/components/dashboard/CriticalProjectsTable';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { toast } from 'sonner';

export function DashboardView() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // 1. Cargar datos reales al montar
  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchProjects();
        setProjects(data);
      } catch (error) {
        console.error(error);
        toast.error("Error cargando datos del tablero");
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  // 2. Cálculos en tiempo real (reemplazando la lógica de mocks)
  const totalProjects = projects.length;
  // Sumamos presupuesto, asegurando que no sea null (|| 0)
  const totalBudget = projects.reduce((sum, p) => sum + (p.presupuesto || 0), 0);
  const totalExecuted = projects.reduce((sum, p) => sum + (p.ejecutado || 0), 0);
  const totalBeneficiaries = projects.reduce((sum, p) => sum + (p.beneficiarios || 0), 0);
  
  const projectsAtRisk = projects.filter(p => p.status === 'en_riesgo' || p.status === 'retrasado').length;
  const projectsInExecution = projects.filter(p => p.status === 'en_ejecucion').length;
  
  // Evitar división por cero
  const executionRate = totalBudget > 0 ? ((totalExecuted / totalBudget) * 100).toFixed(1) : "0.0";
  const averageProgress = totalProjects > 0 ? Math.round(projects.reduce((sum, p) => sum + (p.avance || 0), 0) / totalProjects) : 0;

  // Formateadores auxiliares para la vista
  const formatCurrency = (amount: number) => 
    new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', maximumFractionDigits: 0 }).format(amount);
  
  const formatNumber = (num: number) => 
    new Intl.NumberFormat('es-MX').format(num);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="font-display text-2xl md:text-3xl font-bold text-foreground">
          Panel Ejecutivo
        </h1>
        <p className="text-muted-foreground mt-1">
          {isLoading ? 'Conectando con servidor...' : 'Resumen general de gestión de obras'}
        </p>
      </div>

      {/* KPI Grid - MANTENIENDO TU DISEÑO ORIGINAL */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        
        <KPICard
          title="Total Proyectos"
          value={formatNumber(totalProjects)}
          icon={FolderKanban}
          trend={{ value: 12, label: "vs mes anterior" }} // Ejemplo estático o calcúlalo si tienes fechas
          trendUp={true}
        />

        <KPICard
          title="Presupuesto Total"
          value={formatCurrency(totalBudget)}
          icon={DollarSign}
          trend={{ value: Number(executionRate), label: "% ejercido" }}
          trendUp={true}
        />

        <KPICard
          title="Beneficiarios"
          value={formatNumber(totalBeneficiaries)}
          icon={Users}
          trend={{ value: 5, label: "nuevas zonas" }}
          trendUp={true}
        />

        <KPICard
          title="Atención Requerida"
          value={projectsAtRisk}
          icon={AlertTriangle}
          trend={{ value: projectsAtRisk, label: "proyectos" }}
          trendUp={false}
          alert={projectsAtRisk > 0}
        />
        
        {/* Tus tarjetas personalizadas (Custom Divs) */}
        <div className="bg-card rounded-xl p-5 shadow-sm border border-border flex items-center gap-4 animate-slide-up" style={{ animationDelay: '200ms' }}>
          <div className="p-3 rounded-lg bg-info/10">
            <Clock className="h-6 w-6 text-blue-500" />
          </div>
          <div>
            <p className="text-2xl font-display font-bold">{projectsInExecution}</p>
            <p className="text-sm text-muted-foreground">En Ejecución</p>
          </div>
        </div>

        <div className="bg-card rounded-xl p-5 shadow-sm border border-border flex items-center gap-4 animate-slide-up" style={{ animationDelay: '250ms' }}>
          <div className="p-3 rounded-lg bg-primary/10">
            <TrendingUp className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-2xl font-display font-bold">{averageProgress}%</p>
            <p className="text-sm text-muted-foreground">Avance Promedio</p>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pasamos los proyectos reales como Props */}
        <ProjectsStatusChart projects={projects} />
        <BudgetChart projects={projects} />
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <CriticalProjectsTable projects={projects} />
        </div>
        <div>
          <RecentActivity />
        </div>
      </div>
    </div>
  );
}