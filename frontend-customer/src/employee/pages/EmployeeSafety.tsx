import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Separator } from '../../components/ui/separator';
import { Shield, AlertTriangle, CheckCircle, FileText, Phone } from 'lucide-react';

const safetyProtocols = [
  {
    id: 1,
    title: 'Ice Handling Safety',
    category: 'Physical Safety',
    priority: 'high',
    description: 'Proper lifting techniques, protective equipment, and handling procedures',
    lastUpdated: '2024-01-15',
    status: 'current'
  },
  {
    id: 2,
    title: 'Equipment Safety Procedures',
    category: 'Equipment',
    priority: 'high',
    description: 'Safe operation of ice production and handling equipment',
    lastUpdated: '2024-01-10',
    status: 'current'
  },
  {
    id: 3,
    title: 'Vehicle Safety & Maintenance',
    category: 'Transportation',
    priority: 'medium',
    description: 'Pre-trip inspections, safe driving practices, and maintenance protocols',
    lastUpdated: '2024-01-05',
    status: 'current'
  },
  {
    id: 4,
    title: 'Emergency Response Procedures',
    category: 'Emergency',
    priority: 'critical',
    description: 'Response protocols for accidents, injuries, and emergency situations',
    lastUpdated: '2024-01-20',
    status: 'current'
  }
];

const emergencyContacts = [
  { title: 'Emergency Services', number: '911' },
  { title: 'Safety Manager', number: '(555) 123-4567' },
  { title: 'Operations Center', number: '(555) 987-6543' },
  { title: 'HR Department', number: '(555) 456-7890' }
];

export function EmployeeSafety() {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-500';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Safety Protocols</h1>
        <p className="text-muted-foreground">
          Comprehensive safety guides for ice handling, storage, and delivery operations
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          {safetyProtocols.map((protocol) => (
            <Card key={protocol.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Shield className="h-5 w-5 text-blue-600" />
                    <CardTitle className="text-lg">{protocol.title}</CardTitle>
                  </div>
                  <Badge variant="outline" className={getPriorityColor(protocol.priority)}>
                    {protocol.priority.charAt(0).toUpperCase() + protocol.priority.slice(1)}
                  </Badge>
                </div>
                <CardDescription>
                  <span className="font-medium">{protocol.category}</span> • {protocol.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center">
                    <CheckCircle className="mr-2 h-4 w-4 text-green-500" />
                    Current Version
                  </div>
                  <span>Updated: {new Date(protocol.lastUpdated).toLocaleDateString()}</span>
                </div>
                
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm">
                    <FileText className="mr-2 h-4 w-4" />
                    View Protocol
                  </Button>
                  <Button variant="outline" size="sm">
                    Download PDF
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertTriangle className="mr-2 h-5 w-5 text-red-500" />
                Emergency Contacts
              </CardTitle>
              <CardDescription>
                Important numbers for emergency situations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {emergencyContacts.map((contact, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{contact.title}</span>
                    <Button variant="outline" size="sm">
                      <Phone className="mr-2 h-4 w-4" />
                      {contact.number}
                    </Button>
                  </div>
                  {index < emergencyContacts.length - 1 && <Separator className="mt-4" />}
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Safety Reminders</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                <span className="text-sm">Always wear protective equipment</span>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                <span className="text-sm">Report incidents immediately</span>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                <span className="text-sm">Follow proper lifting techniques</span>
              </div>
              <div className="flex items-start space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                <span className="text-sm">Keep work areas clean and organized</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
