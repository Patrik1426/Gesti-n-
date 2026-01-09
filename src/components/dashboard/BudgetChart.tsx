import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Project } from '@/lib/mockData';

interface Props {
  projects: Project[];
}

export function BudgetChart({ projects }: Props) {
  // Tomamos los 6 proyectos con mayor presupuesto para la gráfica
  const topProjects = [...projects]
    .sort((a, b) => b.presupuesto - a.presupuesto)
    .slice(0, 6);

  const data = topProjects.map(project => ({
    name: project.nombre.length > 20 ? project.nombre.substring(0, 20) + '...' : project.nombre,
    presupuesto: project.presupuesto / 1000000, // Convertir a Millones
    ejecutado: project.ejecutado / 1000000,
  }));

  return (
    <div className="bg-card rounded-xl p-6 shadow-sm border border-border animate-slide-up" style={{ animationDelay: '100ms' }}>
      <h3 className="font-display font-semibold text-lg mb-4">Top Presupuesto vs Ejecutado (Millones MXN)</h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis type="number" tick={{ fontSize: 12 }} />
            <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11 }} tickLine={false} />
            <Tooltip formatter={(value: number) => [`$${value.toFixed(2)}M`, '']} contentStyle={{ borderRadius: '8px' }} />
            <Legend />
            <Bar dataKey="presupuesto" name="Presupuesto" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
            <Bar dataKey="ejecutado" name="Ejecutado" fill="hsl(var(--success))" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}