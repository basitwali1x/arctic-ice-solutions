import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Progress } from '../../components/ui/progress';
import { Badge } from '../../components/ui/badge';
import { BookOpen, Clock, CheckCircle, PlayCircle, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { apiRequest } from '../../utils/api';

interface TrainingModule {
  id: string;
  title: string;
  description: string;
  duration: string;
  type: string;
  status: string;
}

interface EmployeeProgress {
  employee_id: string;
  module_id: string;
  progress: number;
  completed: boolean;
  last_updated: string;
}

interface ProgressData {
  overall_progress: number;
  completed_modules: number;
  total_modules: number;
  certifications_earned: number;
  total_certifications: number;
  current_streak: number;
  total_hours: number;
  progress_details: EmployeeProgress[];
}

export function EmployeeTraining() {
  const [trainingModules, setTrainingModules] = useState<TrainingModule[]>([]);
  const [progressData, setProgressData] = useState<ProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updatingProgress, setUpdatingProgress] = useState<string | null>(null);

  useEffect(() => {
    fetchTrainingData();
  }, []);

  const fetchTrainingData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [modulesResponse, progressResponse] = await Promise.all([
        apiRequest('/api/training/modules'),
        apiRequest('/api/employee/progress')
      ]);

      if (!modulesResponse || !progressResponse) {
        throw new Error('Failed to fetch training data');
      }

      const modules = await modulesResponse.json();
      const progress = await progressResponse.json();

      setTrainingModules(modules);
      setProgressData(progress);
    } catch (err) {
      console.error('Failed to fetch training data:', err);
      setError('Failed to load training data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getModuleProgress = (moduleId: string): number => {
    if (!progressData) return 0;
    const moduleProgress = progressData.progress_details.find(p => p.module_id === moduleId);
    return moduleProgress?.progress || 0;
  };

  const getModuleStatus = (moduleId: string): string => {
    const progress = getModuleProgress(moduleId);
    if (progress >= 100) return 'completed';
    if (progress > 0) return 'in-progress';
    return 'not-started';
  };

  const handleStartTraining = async (moduleId: string) => {
    try {
      setUpdatingProgress(moduleId);
      
      const currentProgress = getModuleProgress(moduleId);
      const newProgress = currentProgress === 0 ? 25 : Math.min(currentProgress + 25, 100);
      
      await apiRequest(`/api/training/modules/${moduleId}/progress`, {
        method: 'POST',
        body: JSON.stringify({ progress: newProgress })
      });

      await fetchTrainingData();
    } catch (err) {
      console.error('Failed to update training progress:', err);
      setError('Failed to update progress. Please try again.');
    } finally {
      setUpdatingProgress(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'in-progress':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      case 'in-progress':
        return <PlayCircle className="h-4 w-4" />;
      default:
        return <BookOpen className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading training modules...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Training Modules</h1>
          <p className="text-muted-foreground">
            Complete your training modules to earn blockchain-verified certifications
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error}</p>
          <Button 
            onClick={fetchTrainingData} 
            variant="outline" 
            className="mt-2"
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Training Modules</h1>
        <p className="text-muted-foreground">
          Complete your training modules to earn blockchain-verified certifications
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {trainingModules.map((module) => {
          const progress = getModuleProgress(module.id);
          const status = getModuleStatus(module.id);
          const isUpdating = updatingProgress === module.id;
          
          return (
            <Card key={module.id} className="relative">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{module.title}</CardTitle>
                  <Badge variant="outline" className={getStatusColor(status)}>
                    {getStatusIcon(status)}
                    <span className="ml-1 capitalize">{status.replace('-', ' ')}</span>
                  </Badge>
                </div>
                <CardDescription>{module.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center text-sm text-muted-foreground">
                  <Clock className="mr-2 h-4 w-4" />
                  {module.duration}
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{progress}%</span>
                  </div>
                  <Progress value={progress} className="h-2" />
                </div>

                <Button 
                  className="w-full" 
                  variant={status === 'completed' ? 'outline' : 'default'}
                  onClick={() => handleStartTraining(module.id)}
                  disabled={isUpdating}
                >
                  {isUpdating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    <>
                      {status === 'completed' ? 'Review Module' : 
                       status === 'in-progress' ? 'Continue Training' : 'Start Training'}
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
