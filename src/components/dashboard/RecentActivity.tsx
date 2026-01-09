import { CheckCircle, AlertTriangle, FileText, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Project } from '@/lib/mockData';

interface Props {
  projects: Project[];
}

export function RecentActivity({ projects }: Props) {
  // Generamos actividades dinámicas basadas en los datos reales
  const completed = projects.filter(p => p.status === 'completado').slice(0, 2);
  const risky = projects.filter(p => p.status === 'en_riesgo').slice(0, 2);
  const newProjects = projects.slice(0, 1); // Asumimos los primeros son nuevos

  const activities = [
    ...risky.map(p => ({
      id: `risk-${p.id}`,
      title: 'Alerta de Riesgo',
      description: `${p.nombre} requiere atención inmediata.`,
      time: 'Hace poco',
      icon: AlertTriangle,
      color: 'text-danger bg-danger/10'
    })),
    ...completed.map(p => ({
      id: `complete-${p.id}`,
      title: 'Proyecto Completado',
      description: `${p.nombre} ha finalizado.`,
      time: 'Hoy',
      icon: CheckCircle,
      color: 'text-success bg-success/10'
    })),
    ...newProjects.map(p => ({
      id: `new-${p.id}`,
      title: 'Nuevo Proyecto Registrado',
      description: p.nombre,
      time: 'Reciente',
      icon: FileText,
      color: 'text-primary bg-primary/10'
    }))
  ].slice(0, 5); // Mostrar solo 5 eventos

  return (
    <div className="bg-card rounded-xl p-6 shadow-sm border border-border animate-slide-up" style={{ animationDelay: '300ms' }}>
      <h3 className="font-display font-semibold text-lg mb-4">Actividad del Sistema</h3>
      
      <div className="space-y-4">
        {activities.map((activity, index) => {
          const Icon = activity.icon;
          return (
            <div key={activity.id} className="flex items-start gap-3 animate-fade-in">
              <div className={cn("p-2 rounded-lg shrink-0", activity.color)}>
                <Icon className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm">{activity.title}</p>
                <p className="text-xs text-muted-foreground truncate">{activity.description}</p>
              </div>
              <span className="text-xs text-muted-foreground whitespace-nowrap">{activity.time}</span>
            </div>
          );
        })}
        {activities.length === 0 && (
          <div className="text-center text-muted-foreground text-sm py-4">
            Sin actividad reciente registrada.
          </div>
        )}
      </div>
    </div>
  );
}