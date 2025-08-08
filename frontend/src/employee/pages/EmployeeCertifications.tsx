import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Award, Download, ExternalLink, Calendar } from 'lucide-react';
import { useState, useEffect } from 'react';


export function EmployeeCertifications() {
  const [certifications, setCertifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCertifications = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/employee/certifications', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const certs = await response.json();
          setCertifications(certs);
        }
      } catch (error) {
        console.error('Failed to fetch certifications:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCertifications();
  }, []);

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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading certifications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">NFT Certificates</h1>
        <p className="text-muted-foreground">
          Your blockchain-verified certifications and achievements
        </p>
      </div>

      <div className="grid gap-6">
        {certifications.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <Award className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Certifications Yet</h3>
              <p className="text-muted-foreground">
                Complete training modules to earn blockchain-verified certifications
              </p>
            </CardContent>
          </Card>
        ) : (
          certifications.map((cert) => (
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
                        {new Date(cert.issue_date!).toLocaleDateString()}
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Expires:</span>
                      <div className="flex items-center mt-1">
                        <Calendar className="mr-2 h-4 w-4" />
                        {new Date(cert.expiry_date!).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="text-muted-foreground">NFT ID:</span>
                      <code className="ml-2 px-2 py-1 bg-muted rounded text-xs">{cert.nft_id}</code>
                    </div>
                    <div className="text-sm">
                      <span className="text-muted-foreground">Blockchain Hash:</span>
                      <code className="ml-2 px-2 py-1 bg-muted rounded text-xs">{cert.blockchain_hash}</code>
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
          ))
        )}
      </div>
    </div>
  );
}
