import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Award, BookOpen, Clock, CheckCircle } from 'lucide-react';

interface TrainingModule {
  id: string;
  title: string;
  description: string;
  duration: string;
  progress: number;
  status: 'available' | 'in-progress' | 'completed';
  type: string;
}

export default function EmployeeOnboarding() {
  const [modules, setModules] = useState<TrainingModule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModules = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/training/modules`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setModules(data);
        }
      } catch (error) {
        console.error('Failed to fetch training modules:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchModules();
  }, []);

  const handleStartTraining = async (moduleId: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/training/modules/${moduleId}/progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
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
    <div className="container mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Employee Onboarding</h1>
        <p className="text-muted-foreground">
          Complete your training modules to earn blockchain-verified NFT certifications
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {modules.map((module) => (
          <Card key={module.id} className="relative">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <BookOpen className="w-5 h-5" />
                  <CardTitle className="text-lg">{module.title}</CardTitle>
                </div>
                <Badge variant="outline">
                  {module.status.charAt(0).toUpperCase() + module.status.slice(1)}
                </Badge>
              </div>
              <CardDescription>{module.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                <span>{module.duration}</span>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Progress</span>
                  <span>{module.progress}%</span>
                </div>
                <Progress value={module.progress} className="w-full" />
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
                    <Award className="mr-2 h-4 w-4" />
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
