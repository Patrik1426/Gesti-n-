import { Project, getStatusLabel, getPriorityLabel, formatCurrency } from '@/lib/mockData';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AlertTriangle } from 'lucide-react';

interface Props {
  projects: Project[];
}

export function CriticalProjectsTable({ projects }: Props) {
  // Filtramos proyectos reales en riesgo o con prioridad crítica
  const criticalProjects = projects
    .filter(p => p.prioridad === 'critica' || p.status === 'en_riesgo' || p.status === 'retrasado')
    .slice(0, 5); // Solo los primeros 5

  return (
    <div className="bg-card rounded-xl p-6 shadow-sm border border-border animate-slide-up" style={{ animationDelay: '200ms' }}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display font-semibold text-lg">Atención Prioritaria</h3>
        <Badge variant="danger" className="flex items-center gap-1">
          <AlertTriangle className="h-3 w-3" />
          {criticalProjects.length} Detectados
        </Badge>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-3 px-2 text-sm font-medium text-muted-foreground">Proyecto</th>
              <th className="text-left py-3 px-2 text-sm font-medium text-muted-foreground">Estado</th>
              <th className="text-left py-3 px-2 text-sm font-medium text-muted-foreground">Avance</th>
              <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">Monto</th>
            </tr>
          </thead>
          <tbody>
            {criticalProjects.map((project) => (
              <tr key={project.id} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                <td className="py-3 px-2">
                  <div className="max-w-[200px]">
                    <p className="font-medium text-sm truncate">{project.nombre}</p>
                    <p className="text-xs text-muted-foreground truncate">{project.responsable}</p>
                  </div>
                </td>
                <td className="py-3 px-2">
                  <Badge variant={project.status as any}>{getStatusLabel(project.status)}</Badge>
                </td>
                <td className="py-3 px-2">
                  <div className="flex items-center gap-2">
                    <Progress value={project.avance} className="w-16 h-2" />
                    <span className="text-xs">{project.avance}%</span>
                  </div>
                </td>
                <td className="py-3 px-2 text-right">
                  <span className="text-sm font-medium">{formatCurrency(project.presupuesto)}</span>
                </td>
              </tr>
            ))}
            {criticalProjects.length === 0 && (
              <tr>
                <td colSpan={4} className="py-8 text-center text-muted-foreground text-sm">
                  ¡Excelente! No hay proyectos críticos por el momento.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}