import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Progress } from '../../components/ui/progress';
import { Badge } from '../../components/ui/badge';
import { BookOpen, Clock, CheckCircle, PlayCircle } from 'lucide-react';

const trainingModules = [
  {
    id: 1,
    title: 'Ice Handling & Safety Protocols',
    description: 'Essential safety procedures for ice handling, storage, and delivery operations',
    duration: '45 minutes',
    progress: 100,
    status: 'completed',
    type: 'safety'
  },
  {
    id: 2,
    title: 'Equipment Operation Training',
    description: 'Proper operation of ice production and handling equipment',
    duration: '60 minutes',
    progress: 75,
    status: 'in-progress',
    type: 'equipment'
  },
  {
    id: 3,
    title: 'Customer Service Excellence',
    description: 'Best practices for customer interactions and service delivery',
    duration: '30 minutes',
    progress: 0,
    status: 'not-started',
    type: 'service'
  },
  {
    id: 4,
    title: 'Quality Control Standards',
    description: 'Understanding and maintaining ice quality standards',
    duration: '40 minutes',
    progress: 0,
    status: 'not-started',
    type: 'quality'
  }
];

export function EmployeeTraining() {
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Training Modules</h1>
        <p className="text-muted-foreground">
          Complete your training modules to earn blockchain-verified certifications
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {trainingModules.map((module) => (
          <Card key={module.id} className="relative">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{module.title}</CardTitle>
                <Badge variant="outline" className={getStatusColor(module.status)}>
                  {getStatusIcon(module.status)}
                  <span className="ml-1 capitalize">{module.status.replace('-', ' ')}</span>
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
              >
                {module.status === 'completed' ? 'Review Module' : 
                 module.status === 'in-progress' ? 'Continue Training' : 'Start Training'}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
