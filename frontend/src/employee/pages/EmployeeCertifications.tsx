import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Award, Download, ExternalLink, Calendar } from 'lucide-react';

const certifications = [
  {
    id: 1,
    title: 'Ice Handling Safety Certification',
    description: 'Blockchain-verified certification for safe ice handling procedures',
    issueDate: '2024-01-15',
    expiryDate: '2025-01-15',
    status: 'active',
    nftId: 'AIS-IHS-001',
    blockchainHash: '0x1234...abcd'
  },
  {
    id: 2,
    title: 'Equipment Operation Certification',
    description: 'Certified for operating ice production and handling equipment',
    issueDate: '2024-02-01',
    expiryDate: '2025-02-01',
    status: 'active',
    nftId: 'AIS-EOC-002',
    blockchainHash: '0x5678...efgh'
  },
  {
    id: 3,
    title: 'Quality Control Specialist',
    description: 'Advanced certification in ice quality standards and control',
    issueDate: null,
    expiryDate: null,
    status: 'pending',
    nftId: null,
    blockchainHash: null
  }
];

export function EmployeeCertifications() {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500';
      case 'pending':
        return 'bg-yellow-500';
      case 'expired':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">NFT Certificates</h1>
        <p className="text-muted-foreground">
          Your blockchain-verified certifications and achievements
        </p>
      </div>

      <div className="grid gap-6">
        {certifications.map((cert) => (
          <Card key={cert.id} className="relative">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Award className="h-5 w-5 text-blue-600" />
                  <CardTitle className="text-lg">{cert.title}</CardTitle>
                </div>
                <Badge variant="outline" className={getStatusColor(cert.status)}>
                  {cert.status.charAt(0).toUpperCase() + cert.status.slice(1)}
                </Badge>
              </div>
              <CardDescription>{cert.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {cert.status === 'active' && (
                <>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Issue Date:</span>
                      <div className="flex items-center mt-1">
                        <Calendar className="mr-2 h-4 w-4" />
                        {new Date(cert.issueDate!).toLocaleDateString()}
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Expires:</span>
                      <div className="flex items-center mt-1">
                        <Calendar className="mr-2 h-4 w-4" />
                        {new Date(cert.expiryDate!).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="text-muted-foreground">NFT ID:</span>
                      <code className="ml-2 px-2 py-1 bg-muted rounded text-xs">{cert.nftId}</code>
                    </div>
                    <div className="text-sm">
                      <span className="text-muted-foreground">Blockchain Hash:</span>
                      <code className="ml-2 px-2 py-1 bg-muted rounded text-xs">{cert.blockchainHash}</code>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Download className="mr-2 h-4 w-4" />
                      Download Certificate
                    </Button>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      View on Blockchain
                    </Button>
                  </div>
                </>
              )}

              {cert.status === 'pending' && (
                <div className="text-center py-4">
                  <p className="text-muted-foreground mb-4">
                    Complete required training modules to earn this certification
                  </p>
                  <Button>View Requirements</Button>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
