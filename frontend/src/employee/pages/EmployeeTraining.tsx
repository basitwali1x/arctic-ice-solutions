import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { Clock, Play, CheckCircle, Award, BookOpen, Shield, Users, Star } from 'lucide-react';
import { useState, useEffect } from 'react';

export function EmployeeTraining() {
  const [trainingModules, setTrainingModules] = useState<any[]>([]);
  const [employeeProgress, setEmployeeProgress] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };

        const [modulesResponse, progressResponse] = await Promise.all([
          fetch('/api/training/modules', { headers }),
          fetch('/api/employee/progress', { headers })
        ]);

        if (modulesResponse.ok && progressResponse.ok) {
          const modules = await modulesResponse.json();
          const progress = await progressResponse.json();
          
          const modulesWithProgress = modules.map((module: any) => {
            const moduleProgress = progress.progress_details?.find((p: any) => p.module_id === module.id);
            return {
              ...module,
              progress: moduleProgress?.progress || 0,
              status: moduleProgress?.completed ? 'completed' : (moduleProgress?.progress > 0 ? 'in-progress' : 'available')
            };
          });
          
          setTrainingModules(modulesWithProgress);
          setEmployeeProgress(progress);
        }
      } catch (error) {
        console.error('Failed to fetch training data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleStartTraining = async (moduleId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/training/modules/${moduleId}/progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ progress: 100 })
      });

      if (response.ok) {
        window.location.reload();
      }
    } catch (error) {
      console.error('Failed to update progress:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'in-progress':
        return 'bg-blue-500';
      case 'available':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'safety':
        return <Shield className="w-5 h-5" />;
      case 'equipment':
        return <Star className="w-5 h-5" />;
      case 'service':
        return <Users className="w-5 h-5" />;
      case 'quality':
        return <Award className="w-5 h-5" />;
      default:
        return <BookOpen className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading training modules...</p>
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Award className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-2xl font-bold">{employeeProgress?.overall_progress || 0}%</p>
                <p className="text-sm text-muted-foreground">Overall Progress</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-2xl font-bold">{employeeProgress?.completed_modules || 0}/{employeeProgress?.total_modules || 0}</p>
                <p className="text-sm text-muted-foreground">Modules Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Star className="h-8 w-8 text-yellow-600" />
              <div>
                <p className="text-2xl font-bold">{employeeProgress?.certifications_earned || 0}</p>
                <p className="text-sm text-muted-foreground">Certifications Earned</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {trainingModules.map((module) => (
          <Card key={module.id} className="relative">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getTypeIcon(module.type)}
                  <CardTitle className="text-lg">{module.title}</CardTitle>
                </div>
                <Badge variant="outline" className={getStatusColor(module.status)}>
                  {module.status.charAt(0).toUpperCase() + module.status.slice(1)}
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
                  <span>{module.progress}%</span>
                </div>
                <Progress value={module.progress} className="h-2" />
              </div>

              <Button 
                className="w-full" 
                variant={module.status === 'completed' ? 'outline' : 'default'}
                disabled={module.status === 'completed'}
                onClick={() => module.status !== 'completed' && handleStartTraining(module.id)}
              >
                {module.status === 'completed' ? (
                  <>
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Completed
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-4 w-4" />
                    {module.status === 'in-progress' ? 'Continue' : 'Start Training'}
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
