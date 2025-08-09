import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Progress } from '../../components/ui/progress';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { TrendingUp, Award, BookOpen, Target, Calendar, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { apiRequest } from '../../utils/api';

interface ProgressData {
  overall_progress: number;
  completed_modules: number;
  total_modules: number;
  certifications_earned: number;
  total_certifications: number;
  current_streak: number;
  total_hours: number;
  progress_details: any[];
}

const recentActivity = [
  {
    id: 1,
    type: 'completion',
    title: 'Completed Ice Handling Safety Training',
    date: '2024-01-15',
    points: 100
  },
  {
    id: 2,
    type: 'certification',
    title: 'Earned Equipment Operation Certification',
    date: '2024-01-10',
    points: 250
  },
  {
    id: 3,
    type: 'progress',
    title: 'Started Quality Control Standards Module',
    date: '2024-01-08',
    points: 50
  },
  {
    id: 4,
    type: 'milestone',
    title: 'Reached 20 Hours of Training',
    date: '2024-01-05',
    points: 150
  }
];

const upcomingGoals = [
  {
    id: 1,
    title: 'Complete Customer Service Training',
    dueDate: '2024-02-15',
    progress: 25,
    priority: 'high'
  },
  {
    id: 2,
    title: 'Earn Quality Control Certification',
    dueDate: '2024-03-01',
    progress: 0,
    priority: 'medium'
  },
  {
    id: 3,
    title: 'Complete Advanced Safety Module',
    dueDate: '2024-03-15',
    progress: 0,
    priority: 'low'
  }
];

export function EmployeeProgress() {
  const [progressData, setProgressData] = useState<ProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProgressData();
  }, []);

  const fetchProgressData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiRequest('/api/employee/progress');
      if (!response) {
        throw new Error('Failed to fetch progress data');
      }

      const data = await response.json();
      setProgressData(data);
    } catch (err) {
      console.error('Failed to fetch progress data:', err);
      setError('Failed to load progress data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'completion':
        return <BookOpen className="h-4 w-4 text-blue-500" />;
      case 'certification':
        return <Award className="h-4 w-4 text-yellow-500" />;
      case 'milestone':
        return <Target className="h-4 w-4 text-green-500" />;
      default:
        return <TrendingUp className="h-4 w-4 text-purple-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-yellow-500';
      default:
        return 'bg-green-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading progress data...</span>
      </div>
    );
  }

  if (error || !progressData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Progress Tracking</h1>
          <p className="text-muted-foreground">
            Real-time updates on your training progress and achievements
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error || 'Failed to load progress data'}</p>
          <Button 
            onClick={fetchProgressData} 
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
        <h1 className="text-3xl font-bold tracking-tight">Progress Tracking</h1>
        <p className="text-muted-foreground">
          Real-time updates on your training progress and achievements
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overall Progress</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{progressData.overall_progress}%</div>
            <Progress value={progressData.overall_progress} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Modules Completed</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {progressData.completed_modules}/{progressData.total_modules}
            </div>
            <p className="text-xs text-muted-foreground">
              {progressData.total_modules - progressData.completed_modules} remaining
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Certifications</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {progressData.certifications_earned}/{progressData.total_certifications}
            </div>
            <p className="text-xs text-muted-foreground">
              {progressData.total_certifications - progressData.certifications_earned} available
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Training Hours</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{progressData.total_hours}h</div>
            <p className="text-xs text-muted-foreground">
              {progressData.current_streak} day streak
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest training achievements and progress</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center space-x-4">
                {getActivityIcon(activity.type)}
                <div className="flex-1 space-y-1">
                  <p className="text-sm font-medium leading-none">{activity.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(activity.date).toLocaleDateString()}
                  </p>
                </div>
                <Badge variant="outline">+{activity.points} pts</Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Upcoming Goals</CardTitle>
            <CardDescription>Your training objectives and deadlines</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {upcomingGoals.map((goal) => (
              <div key={goal.id} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">{goal.title}</span>
                    <Badge variant="outline" className={getPriorityColor(goal.priority)}>
                      {goal.priority}
                    </Badge>
                  </div>
                  <div className="flex items-center text-xs text-muted-foreground">
                    <Calendar className="mr-1 h-3 w-3" />
                    {new Date(goal.dueDate).toLocaleDateString()}
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span>Progress</span>
                    <span>{goal.progress}%</span>
                  </div>
                  <Progress value={goal.progress} className="h-2" />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
