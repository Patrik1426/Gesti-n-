import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KPICardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  // SOLUCIÓN: Aceptamos ambas formas para que no falle TS
  trend?: string | { value: number; label: string }; 
  trendUp?: boolean;
  description?: string;
  alert?: boolean;
}

export function KPICard({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  trendUp, 
  alert 
}: KPICardProps) {
  
  // Lógica de visualización del trend
  let trendContent;
  if (typeof trend === 'object') {
     // Si es objeto {value, label}
     trendContent = (
        <>
          <span className="font-bold">{trend.value > 0 ? '+' : ''}{trend.value}</span> 
          {' '}{trend.label}
        </>
     );
  } else {
     // Si es string directo
     trendContent = trend;
  }

  return (
    <div className={cn(
      "bg-card rounded-xl p-5 shadow-sm border border-border flex items-start justify-between animate-slide-up hover:shadow-md transition-all",
      alert && "border-l-4 border-l-destructive"
    )}>
      <div>
        <p className="text-sm font-medium text-muted-foreground mb-1">{title}</p>
        <h3 className="text-2xl font-display font-bold text-foreground">{value}</h3>
        
        {trend && (
          <div className={cn(
            "flex items-center gap-1 text-xs mt-2 font-medium",
            trendUp ? "text-emerald-600" : "text-destructive"
          )}>
            {trendUp ? (
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            ) : (
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" /></svg>
            )}
            <span>{trendContent}</span>
          </div>
        )}
      </div>
      
      <div className={cn(
        "p-3 rounded-lg",
        alert ? "bg-destructive/10" : "bg-primary/10"
      )}>
        <Icon className={cn(
          "h-5 w-5",
          alert ? "text-destructive" : "text-primary"
        )} />
      </div>
    </div>
  );
}