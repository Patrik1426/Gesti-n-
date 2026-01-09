import { useState, useEffect } from 'react';
import { direcciones, Project } from '@/lib/mockData'; // Quitamos mockProjects, mantenemos tipos y catálogos estáticos
import { fetchProjects } from '@/lib/api'; // Importamos la conexión real
import { ProjectCard } from '@/components/projects/ProjectCard';
import { ProjectDetail } from '@/components/projects/ProjectDetail';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton'; // Usamos componentes de UI existentes
import { Search, Grid, List, Plus, RefreshCw } from 'lucide-react'; // Agregué RefreshCw para recargar
import { cn } from '@/lib/utils';
import { toast } from 'sonner'; // Asumiendo que usas sonner o el hook de toast que vi en tus archivos

export function ProjectsView() {
  // --- Estados de Datos ---
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // --- Estados de UI ---
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // --- Estados de Filtros ---
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [directionFilter, setDirectionFilter] = useState<string>('all');

  // --- Carga de Datos ---
  const loadProjects = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchProjects();
      setProjects(data);
      // Opcional: Mostrar toast de éxito solo si es una recarga manual
    } catch (err) {
      console.error(err);
      setError('No se pudieron cargar los proyectos. Verifica que el backend esté corriendo.');
      toast.error("Error de conexión con el servidor");
    } finally {
      setIsLoading(false);
    }
  };

  // Cargar al montar el componente
  useEffect(() => {
    loadProjects();
  }, []);

  // --- Lógica de Filtrado (Aplicada sobre los datos reales) ---
  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.nombre.toLowerCase().includes(search.toLowerCase()) ||
      project.responsable.toLowerCase().includes(search.toLowerCase()) ||
      project.ubicacion.toLowerCase().includes(search.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || project.prioridad === priorityFilter;
    const matchesDirection = directionFilter === 'all' || project.direccion === directionFilter;
    
    return matchesSearch && matchesStatus && matchesPriority && matchesDirection;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-fade-in">
        <div>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-foreground">
            Cartera de Proyectos
          </h1>
          <p className="text-muted-foreground mt-1">
            {isLoading ? 'Cargando proyectos...' : `${filteredProjects.length} proyectos en seguimiento`}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" onClick={loadProjects} title="Recargar datos">
            <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
          </Button>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            Nuevo Proyecto
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-card rounded-xl p-4 shadow-sm border border-border space-y-4 animate-slide-up">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Buscar por nombre, responsable o ubicación..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
              disabled={isLoading}
            />
          </div>
          
          <div className="flex flex-wrap gap-2">
            <Select value={statusFilter} onValueChange={setStatusFilter} disabled={isLoading}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Estado" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="en_ejecucion">En Ejecución</SelectItem>
                <SelectItem value="planificado">Planificado</SelectItem>
                <SelectItem value="completado">Completado</SelectItem>
                <SelectItem value="retrasado">Retrasado</SelectItem>
                <SelectItem value="en_riesgo">En Riesgo</SelectItem>
              </SelectContent>
            </Select>

            <Select value={priorityFilter} onValueChange={setPriorityFilter} disabled={isLoading}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Prioridad" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                <SelectItem value="critica">Crítica</SelectItem>
                <SelectItem value="alta">Alta</SelectItem>
                <SelectItem value="media">Media</SelectItem>
                <SelectItem value="baja">Baja</SelectItem>
              </SelectContent>
            </Select>

            <Select value={directionFilter} onValueChange={setDirectionFilter} disabled={isLoading}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Dirección" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas</SelectItem>
                {direcciones.map(dir => (
                  <SelectItem key={dir} value={dir}>{dir.replace('Dirección de ', '')}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="flex border border-border rounded-lg overflow-hidden">
              <Button
                variant="ghost"
                size="icon"
                className={cn("rounded-none", viewMode === 'grid' && "bg-muted")}
                onClick={() => setViewMode('grid')}
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className={cn("rounded-none", viewMode === 'list' && "bg-muted")}
                onClick={() => setViewMode('list')}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="flex flex-col space-y-3">
              <Skeleton className="h-[200px] w-full rounded-xl" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-[250px]" />
                <Skeleton className="h-4 w-[200px]" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Error State */}
      {!isLoading && error && (
        <div className="text-center py-12 text-destructive animate-fade-in bg-destructive/10 rounded-xl border border-destructive/20">
          <p className="text-lg font-semibold">Error de conexión</p>
          <p className="text-sm">{error}</p>
          <Button variant="link" onClick={loadProjects} className="mt-2">
            Reintentar
          </Button>
        </div>
      )}

      {/* Projects Grid/List */}
      {!isLoading && !error && (
        <>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {filteredProjects.map((project, index) => (
                <ProjectCard 
                  key={project.id} 
                  project={project} 
                  onClick={() => setSelectedProject(project)}
                  delay={index * 50}
                />
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {filteredProjects.map((project, index) => (
                <ProjectCard 
                  key={project.id} 
                  project={project} 
                  onClick={() => setSelectedProject(project)}
                  delay={index * 30}
                />
              ))}
            </div>
          )}

          {filteredProjects.length === 0 && (
            <div className="text-center py-12 text-muted-foreground animate-fade-in">
              <p className="text-lg">No se encontraron proyectos</p>
              <p className="text-sm">Intenta ajustar los filtros de búsqueda</p>
            </div>
          )}
        </>
      )}

      {/* Project Detail Modal */}
      {selectedProject && (
        <ProjectDetail 
          project={selectedProject} 
          onClose={() => setSelectedProject(null)} 
        />
      )}
    </div>
  );
}